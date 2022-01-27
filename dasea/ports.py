import logging
import subprocess
from glob import glob
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from dasea.datamodel import Package, Version, Dependency, Kind
from dasea.utils import _serialize_data


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M"
)
LOGGER = logging.getLogger(__name__)


@dataclass
class PortsPackage(Package):
    platform: str


@dataclass
class PortsVersion(Version):
    distname: str


def _get_platform_str():
    cmd = "uname -n"
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    platform_str = r.stdout.strip()
    if platform_str.endswith(".localdomain"):
        platform_str = platform_str.replace(".localdomain", "")

    return platform_str


PLATFORM_STR = _get_platform_str()


# The variables are listed in the man page of port files:
# https://man.openbsd.org/bsd.port.mk.5
# I parse only the variables concerning port name, version, maintainer,
# licenses and dependencies. I neglect all others
# But it seems that there is no license information for ports available, see
# man page above.

if PLATFORM_STR.startswith("freebsd"):

    # The variables are listed in the description of port files:
    # https://docs.freebsd.org/en/books/porters-handbook/makefiles/
    # We parse only the variables concerning port name, version, maintainer,
    # licenses, and dependencies. All others are neglected

    MK_VARS = [
        "PORTNAME",
        "DISTVERSION",
        "CATEGORIES",
        "PKGNAMEPREFIX",
        "PKGNAMESUFFIX",
        "PORTVERSION",
        "PORTREVISION",
        "DISTNAME",
        "MAINTAINER",
        "COMMENT",
        "LICENSE",
        "GH_ACCOUNT",
        "GH_PROJECT",
        "LIB_DEPENDS",
        "MY_DEPENDS",
        "BUILD_DEPENDS",
        "RUN_DEPENDS",
        "FETCH_DEPENDS",
        "EXTRACT_DEPENDS",
        "PATCH_DEPENDS",
        "USES",
    ]
    # TODO: make this configurable? E.g., with quarterly ports tree.
    PORTS_DIR = "/usr/ports/"  # This assumes the default location on FreeBSD
elif PLATFORM_STR.startswith("openbsd"):
    # OpenBSD Port Makefiles do not have a LICENSE field, see find /usr/ports/ -name 'Makefile' -type f -exec grep LICENSE {} \;
    MK_VARS = [
        "PKGNAME",
        "FULLPKGNAME",
        "DISTVERSION",
        "VERSION",
        "CATEGORIES",
        "DISTNAME",
        "MAINTAINER",
        "COMMENT",
        "GH_ACCOUNT",
        "GH_PROJECT",
        "BUILD_DEPENDS",
        "LIB_DEPENDS",
        "RUN_DEPENDS",
        "TEST_DEPENDS",
    ]
    PORTS_DIR = "/usr/ports/"
elif PLATFORM_STR.startswith("netbsd"):
    # https://netbsd.org/docs/pkgsrc/pkgsrc.html#components.Makefile
    MK_VARS = [
        "PKGNAME",
        "DISTNAME",
        "CATEGORIES",
        "MAINTAINER",
        "OWNER",
        "HOMEPAGE",
        "COMMENT",
        "LICENSE",
        "DEPENDS",
        "BUILD_DEPENDS",
        "TOOL_DEPENDS",
        "TEST_DEPENDS",
        "USE_TOOLS",
    ]
    PORTS_DIR = "/usr/pkgsrc/"


TODAY = datetime.today().strftime("%m-%d-%Y")
PKGS_FILE = f"data/out/ports/{PLATFORM_STR}/{PLATFORM_STR}_packages_{TODAY}.csv"
VERSIONS_FILE = f"data/out/ports/{PLATFORM_STR}/{PLATFORM_STR}_versions_{TODAY}.csv"
DEPS_FILE = f"data/out/ports/{PLATFORM_STR}/{PLATFORM_STR}_dependencies_{TODAY}.csv"


def _collect_mk_files():
    mk_file_pattern = Path(PORTS_DIR, "**", "Makefile")
    mk_files = glob(str(mk_file_pattern), recursive=True)

    # Filter out the Makefiles that are not from ports but from tooling
    # Ports are organized by category in directories with only lower characters.
    mk_files = [m for m in mk_files if Path(m).parts[3] == Path(m).parts[3].lower()]
    # Filter out the Makefiles of the categories, which would have five path
    # elements
    mk_files = [m for m in mk_files if len(Path(m).parts) == 6]

    return mk_files


def _parse_metadata(mk_file):

    if PLATFORM_STR.startswith("freebsd") or PLATFORM_STR.startswith("netbsd"):
        var_switch = "-v"
    elif PLATFORM_STR.startswith("openbsd"):
        var_switch = "-V"  # OpenBSD does not support variable expansion when printing variables
    mk_vars_lst = [f"{var_switch} {m}" for m in MK_VARS]
    mk_vars_str = " ".join(mk_vars_lst)

    cmd = f"make {mk_vars_str} -f {mk_file}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=Path(mk_file).parent)

    if result.returncode != 0:
        # TODO: What to return then? A dict with only keys?
        # Is this case needed at all? On FreeBSD 11.4, it does not seem to happen.
        return None
    else:
        return dict(zip(MK_VARS, result.stdout.splitlines()))


def _process_metadata(mk_info, port_mk_file):
    for mk_var, vals in mk_info.items():
        if mk_var in [
            "CATEGORIES",
            "LIB_DEPENDS",
            "MY_DEPENDS",
            "BUILD_DEPENDS",
            "RUN_DEPENDS",
            "FETCH_DEPENDS",
            "EXTRACT_DEPENDS",
            "PATCH_DEPENDS",
            "TEST_DEPENDS",  # OpenBSD and NetBSD  
            "USES",
            # NetBSD values:
            "DEPENDS",
            "TOOL_DEPENDS",
            "USE_TOOLS"
        ]:
            if vals:
                if " " in vals:
                    # Multiple dependencies are turned from a string to a list
                    mk_info[mk_var] = vals.split()
                else:
                    # In case of one dependency only make it a list too to make
                    # later processing more easy
                    mk_info[mk_var] = [vals]
            else:
                mk_info[mk_var] = []

    if PLATFORM_STR.startswith("freebsd"):
        # The full pkg name of a port is according to
        # https://docs.freebsd.org/en/books/porters-handbook/makefiles/#porting-pkgnameprefix-suffix
        mk_info[
            "PKGNAME"
        ] = f'{mk_info.get("PKGNAMEPREFIX", "")}{mk_info["PORTNAME"]}{mk_info.get("PKGNAMESUFFIX", "")}-{mk_info.get("PORTVERSION", "")}'
        # In FreeBSD licenses are space-separated lists, in NetBSD they are boolean expressions, and in OpenBSD they do not exist
        mk_info["LICENSE"] = mk_info["LICENSE"].split(),
    elif PLATFORM_STR.startswith("openbsd"):
        mk_info["PKGNAME"] = mk_info["FULLPKGNAME"]

    mk_info["PORTTREEID"] = str(Path(*Path(port_mk_file).parts[3:-1]))

    # The following exists only for FreeBSD and OpenBSD but not for NetBSD
    if mk_info.get("GH_ACCOUNT", ""):
        mk_info["GH_URL"] = "https://github.com/" + mk_info.get("GH_ACCOUNT", "") + "/" + mk_info.get("GH_PROJECT", "")
    else:
        mk_info["GH_URL"] = ""

    # TODO: There must be more parsing, right?
    return mk_info


def _collect_metadata(port_mk_files):
    """Creates a dictionary with metadata per port makefile.
    Since parsing of metadata calls repeatedly the `make` command on the terminal
    this function takes long to complete (ca. 50 minutes)
    """
    # from tqdm import tqdm
    mk_file_metadata_map = {}
    # for port_idx, port_mk_file in tqdm(enumerate(port_mk_files)):
    for port_idx, port_mk_file in enumerate(port_mk_files):
        if mk_info := _parse_metadata(port_mk_file):
            mk_info = _process_metadata(mk_info, port_mk_file)
        else:
            LOGGER.warning(f"{port_mk_file} is erroneous and cannot be parsed...")
            mk_info = {"PORTTREEID": str(Path(*Path(port_mk_file).parts[-3:-1]))}

        mk_file_metadata_map[port_mk_file] = mk_info

    return mk_file_metadata_map


def _collect_packages(mk_file_metadata_map):
    packages = []
    pkg_idx_map = {}
    for idx, (port_mk_file, mk_info) in enumerate(mk_file_metadata_map.items()):
        pkg_name = mk_info["PORTTREEID"]

        p = PortsPackage(idx=idx, name=pkg_name, pkgman="ports", platform=PLATFORM_STR)
        packages.append(p)
        pkg_idx_map[pkg_name] = idx

    return pkg_idx_map, packages


def _collect_versions(mk_file_metadata_map, pkg_idx_map):

    if PLATFORM_STR.startswith("freebsd"):
        version_key = "PORTVERSION"  # or take DISTVERSION for FreeBSD?
    elif PLATFORM_STR.startswith("openbsd"):
        version_key = "VERSION"
        # TODO: this variable is not always set. Instead, values may be encoded in DISTNAME for example like:
        # libdwarf-${V}
        # ${GH_PROJECT}-${V}
        # bamf-${V}.${P}
        # astyle_${V}_linux
        # sqlite-autoconf-${VER:C/.$/0\0/}00
        # PyMySQL-${MODPY_EGG_VERSION}
        # psqlodbc-${VERSION}
        # pg-toolbox-$V
        # metaauto-${VERSION}
        # ${GH_PROJECT}-${GH_TAGNAME:C/^(v|V|ver|[Rr]el|[Rr]elease)[-._]?([0-9])/\2/}
        # In future some of these values should be expanded. However, OpenBSD `make` does not support this unlike 
        # FreeBSD `make` with `-v` instead of `-V` 
    elif PLATFORM_STR.startswith("netbsd"):
        # NetBSD does not have such a field. Version numbers are stored in DISTNAME (and sometimes in PKGNAME) and
        # They are not easily extracted from these since they do not follow a common schema.
        version_key = ""

    versions = []
    for idx, (port_mk_file, mk_info) in enumerate(mk_file_metadata_map.items()):
        pkg_name = mk_info["PORTTREEID"]

        v = PortsVersion(
            idx=idx,  # There is only one version per Makefile
            pkg_idx=pkg_idx_map[pkg_name],
            name=pkg_name,
            version=mk_info.get(version_key, ""),
            license=mk_info.get("LICENSE", ""),  # OpenBSD does not have a LICENSE field
            description=mk_info["COMMENT"],
            homepage=mk_info.get("HOMEPAGE", ""),  # Only NetBSD has such a field
            repository=mk_info.get("GH_URL", None),
            author=None,
            maintainer=mk_info["MAINTAINER"],
            distname=mk_info["DISTNAME"]
        )

        versions.append(v)

    return versions


def _extract_dep_port_tree_id(dep_decl_str):
    if PLATFORM_STR.startswith("freebsd"):
        dep_port_tree_id = dep_decl_str.split(":")[1].split("@")[0]
    elif PLATFORM_STR.startswith("openbsd"):
        dep_els = dep_decl_str.split(":")
        if len(dep_els) == 1:
            dep_port_tree_id = dep_els[0]
        else:
            if "/" in dep_els[1]:
                dep_port_tree_id = dep_els[1]
            else:
                dep_port_tree_id = dep_els[0]
        # Detach the port flavor from the porttree id 
        dep_port_tree_id_els = dep_port_tree_id.split(",")
        dep_port_tree_id = dep_port_tree_id_els[0]
    elif PLATFORM_STR.startswith("netbsd"):
        dep_els = dep_decl_str.split(":")
        if len(dep_els) == 1:
            dep_port_tree_id = ""
        else:
            dep_port_tree_id = dep_els[1].replace("../../", "")
    return dep_port_tree_id


# for _, v in mk_file_metadata_map.items():
#     if oi := _extract_dep_port_tree_id(v["DEPENDS"]):
#         if oi.startswith("www/p5-Plack"):
#             print(v)
#             break



def _collect_dependencies(mk_file_metadata_map, pkg_idx_map):
    dep_kind_map = {
                        "LIB_DEPENDS": Kind.LIB,
                        "MY_DEPENDS": Kind.MY,
                        "BUILD_DEPENDS": Kind.BUILD,
                        "RUN_DEPENDS": Kind.RUN,
                        "FETCH_DEPENDS": Kind.FETCH,
                        "EXTRACT_DEPENDS": Kind.EXTRACT,
                        "PATCH_DEPENDS": Kind.PATCH,
                        "TEST_DEPENDS": Kind.TEST
                    }
    dependencies = []

    if PLATFORM_STR.startswith("freebsd"):
        version_key = "PORTVERSION"  # or take DISTVERSION for FreeBSD?
    elif PLATFORM_STR.startswith("openbsd"):
        version_key = "VERSION"
    elif PLATFORM_STR.startswith("netbsd"):
        version_key = ""

    for idx, (port_mk_file, mk_info) in enumerate(mk_file_metadata_map.items()):
        pkg_name = mk_info["PORTTREEID"]

        # TODO: Add USES clause in future
        for dep_kind in ["LIB_DEPENDS", "MY_DEPENDS", "BUILD_DEPENDS", "RUN_DEPENDS", "FETCH_DEPENDS", "EXTRACT_DEPENDS", "PATCH_DEPENDS"]:

            # TODO [FreeBSD]: Some dependencies are declared multiple times. But they seem to be coming from other sources than
            # the Makefile, see e.g. emulators/qemu42 `make -V RUN_DEPENDS /usr/ports/emulators/qemu42/Makefile`
            # The Makefile does not contain a RUN_DEPENDS declaration, but x11/libX11, x11/libXext, and x11/pixman are
            # declared 3 and 2 times as dependencies???
            # Consequently, we convert them to sets here to avoid duplicate edges for the same dependency in the graph
            for dep_decl in set(mk_info.get(dep_kind, "")):
                dep_port_tree_id = _extract_dep_port_tree_id(dep_decl)
                try:
                    dep_version_constraint = dep_decl.split(":")[1].split("@")[1]
                except:
                    dep_version_constraint = ""
                dep_port_idx = pkg_idx_map.get(dep_port_tree_id, "")

                version_idx = pkg_idx_map[pkg_name]
                d = Dependency(
                    pkg_idx=pkg_idx_map[pkg_name],
                    source_idx=version_idx,
                    target_idx=dep_port_idx,
                    source_name=pkg_name,
                    target_name=dep_port_tree_id,
                    source_version=mk_info.get(version_key, ""),  # Resort to DISTNAME on NetBSD instead?
                    target_version=dep_version_constraint,
                    kind=dep_kind_map[dep_kind].name,
                )
                dependencies.append(d)
    return dependencies


def mine():
    LOGGER.info("Collecting Makefiles")
    port_mk_files = _collect_mk_files()
    LOGGER.info(f"Found {len(port_mk_files)} ports...")

    LOGGER.info("Parsing metadata from Makefiles...")
    mk_file_metadata_map = _collect_metadata(port_mk_files)

    LOGGER.info("Converting packages to DaSEA...")
    pkg_idx_map, packages_lst = _collect_packages(mk_file_metadata_map)
    _serialize_data(packages_lst, PKGS_FILE)
    del packages_lst  # free some memory

    LOGGER.info("Converting versions to DaSEA...")
    versions_lst = _collect_versions(mk_file_metadata_map, pkg_idx_map)
    _serialize_data(versions_lst, VERSIONS_FILE)
    del versions_lst  # free some memory

    LOGGER.info("Converting dependencies to DaSEA...")
    deps_lst = _collect_dependencies(mk_file_metadata_map, pkg_idx_map)
    _serialize_data(deps_lst, DEPS_FILE)
    del deps_lst  # free some memory


if __name__ == "__main__":
    mine()
