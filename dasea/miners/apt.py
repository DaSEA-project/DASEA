import requests
import subprocess
from dataclasses import dataclass
from dasea.common.datamodel import Package, Version, Dependency, Kind
from dasea.common.utils import _serialize_data
from collections import defaultdict
from mongita import MongitaClientDisk
from tqdm import tqdm


PKGS_FILE = "data/out/ubuntu/packages.csv"
VERSIONS_FILE = "data/out/ubuntu/versions.csv"
DEPS_FILE = "data/out/ubuntu/dependencies.csv"

VERSIONS_DB = "data/tmp/ubuntu/versions_db"


@dataclass
class APTPackage(Package):
    platform: str
    virtual: bool


@dataclass
class APTVersion(Version):
    original_maintainer: str
    architecture: str
    origin: str


def _get_platform_str():
    cmd = "uname -n"  # "lsb_release -sd"
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.stdout.strip()


def _collect_packages():
    """Collect all virtual and concrete packages. The former via `aptitude` and
    the latter via `apt-cache dump`.
    """
    # Find all packages, virtual packages included
    cmd = 'apt-cache dump | grep "Package: "'
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    pkg_names = [l.replace("Package: ", "") for l in r.stdout.splitlines()]
    # For some reason few packages appear twice...
    pkg_names = list(set(pkg_names))

    # Find only all virtual packages
    cmd = "aptitude search '?virtual'"
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    # The removes the leading `v` and the trailing dash from the output
    # which looks originally like the following: `v  4ti2-doc:i386 -`
    virt_pkg_names = set([l[1:-2].strip() for l in r.stdout.splitlines()])

    platform_str = _get_platform_str()

    pkg_idx_map = {}
    packages = []
    for idx, pkg_name in enumerate(pkg_names):
        is_virtual = False
        if pkg_name in virt_pkg_names:
            is_virtual = True
        p = APTPackage(idx=idx, name=pkg_name, pkgman="apt", platform=platform_str, virtual=is_virtual)
        packages.append(p)
        pkg_idx_map[pkg_name] = idx

    return pkg_idx_map, packages


def _collect_version_info(metainfo_str, version_dicts=defaultdict(dict)):
    """Parsing of output from `apt-cache show` and `apt-cache showsrc` is expensive!
    However, since it seems that [`python-apt`](https://apt-team.pages.debian.net/python-apt/) does not provide information,
    such as, vcs-git fields, I resort to parsing the text output instead of wrapping libapt, which would be quicker

    Generally, there is a one-to-many relation between a source package and binary packages
    apt-cache showsrc freeipa-server-trust-ad
    apt-cache show freeipa-server-trust-ad
    apt-cache show freeipa-admintools
    apt-cache showsrc freeipa-admintools

    where the source package is freeipa


    , freeipa-common, freeipa-client, python-ipaclient, python-ipalib, freeipa-server, freeipa-server-dns, freeipa-server-trust-ad, freeipa-tests, python-ipaserver, python-ipatests
    """
    version_dict = {}
    for line in metainfo_str.splitlines():

        if not line:  # Empty line denotes start of a new version
            if version_dict["Version"] in version_dicts[version_dict["Package"]].keys():
                version_dicts[version_dict["Package"]][version_dict["Version"]].update(version_dict)
            else:
                version_dicts[version_dict["Package"]][version_dict["Version"]] = version_dict

            version_dict = {}
        elif line.startswith(" "):
            # That should only be the case for detailed package description,
            # which we ignore
            # TODO: Check there are some other long fields like that?

            continue
        else:
            try:
                key, value = line.split(": ", 1)
                version_dict[key] = value
            except Exception as e:
                # We ignore all fields with multiple values on multiple lines
                # These are for example Package-List, Files, Checksums-Sha1, Checksums-Sha256, etc.
                # in case of source packages
                continue
    return version_dicts


# def _collect_version_info(pkg_name):
#     cmd = f"apt-cache show {pkg_name}"
#     r = subprocess.run(cmd, shell=True, capture_output=True, text=True)

#     version_dicts = []
#     version_dict = {}
#     for line in r.stdout.splitlines():

#         if not line:  # Empty line denotes start of a new version
#             version_dicts.append(version_dict)
#             version_dict = {}
#         elif line.startswith(" "):
#             # That should only be the case for detailed package description,
#             # which we ignore
#             continue
#         else:
#             key, value = line.split(": ", 1)
#             version_dict[key] = value

#     return version_dicts


def _collect_versions(pkg_names):
    all_version_dicts = {}

    for idx, pkg_name in enumerate(pkg_names):
        version_dicts = _collect_version_info(pkg_name)
        version_dicts = _collect_version_info(pkg_name, version_dicts=version_dicts, kind="source")
        all_version_dicts.update(version_dicts)

        if idx > 200:
            break
    return all_version_dicts


def _extract_version_info(pkg_names):
    dbclient = MongitaClientDisk(host=VERSIONS_DB)
    versions_db = dbclient.versions
    collection = versions_db.collection

    version_idx_map = defaultdict(dict)
    version_idx = 0
    for pkg_name in tqdm(pkg_names):
        # Has to be done in two stages, since information of a single package is distributed between
        # binary and source package
        version_dicts = _collect_version_info(pkg_name)
        version_dicts = _collect_version_info(pkg_name, version_dicts=version_dicts, kind="source")

        collection.insert_one(version_dicts)

        # for k in version_dicts[pkg_name].keys():
        #     version_idx_map[pkg_name][k] = version_idx
        #     version_idx += 1

    return version_idx_map


def _collect_versions(pkg_names, pkg_idx_map):
    versions = []
    all_version_dicts = {}
    version_idx = 0
    version_idx_map = {}

    for pkg_name in pkg_names:
        version_dicts = _collect_version_info(pkg_name)
        version_dicts = _collect_version_info(pkg_name, version_dicts=version_dicts, kind="source")
        all_version_dicts.update(version_dicts)

        pkg_idx = pkg_idx_map.get(pkg_name, None)
        for version_dict in version_dicts:
            v = APTVersion(
                idx=version_idx,
                pkg_idx=pkg_idx,
                name=version_dict["Package"],
                version=version_dict["Version"],
                license=None,  # This does not seem to exist in the data
                description=version_dict.get("Description"),  # TODO: -en
                homepage=data.get("Homepage", ""),
                repository=None,
                author=None,
                maintainer=version_dict("Maintainer", None),
                original_maintainer=version_dict("Original-Maintainer", None),
                architecture=version_dict("Architecture", None),
                origin=version_dict("Origin", None),
            )
            versions.append(v)
            version_idx_map[pkg_name][version_dict["Version"]] = version_idx
            version_idx += 1
    return versions, all_version_dicts, version_idx_map


# apt-cache depends rmail
# apt-cache show exim4-daemon-light


def _parse_version_deps(metainfo_str):
    """
    This function parses the text output of ...
    """

    version_dicts = []
    version_dict = {}
    for line in metainfo_str.splitlines():
        if not line:  # Empty line denotes start of a new version
            version_dicts.append(version_dict)
            version_dict = {}
        elif line.startswith(" "):
            # That should only be the case for detailed package description,
            # which we ignore
            # TODO: Check there are some other long fields like that?
            continue
        else:
            key, value = line.split(": ", 1)
            version_dict[key] = value
            # TODO: in case of Depends and some others parse value
            # split on ",", strip, extract version in ()

    return version_dicts


def _collect_dependencies(metadata_lst, pkg_idx_map):
    deps = []
    for version_idx, data in enumerate(metadata_lst):
        pkg_name = data["Name"]
        source_pkg_idx = pkg_idx_map.get(pkg_name, None)
        for dep_info in data.get("Dependencies", []):
            if type(dep_info) == str:
                dep_name = dep_info
                platform = ""
            elif type(dep_info) == dict:
                dep_name = dep_info["name"]
                platform = dep_info.get("platform", "")

            d = VCPKGDependency(
                pkg_idx=source_pkg_idx,
                # TODO: double check if the following lookup yields the desired result!
                source_idx=version_idx,
                target_idx=pkg_idx_map[dep_name],
                source_name=data["Name"],
                target_name=dep_name,
                source_version=data["Version"],
                target_version=None,
                kind=Kind.BUILD.name,
                os_platform=platform,
            )
            deps.append(d)
    return deps


def mine():
    pkg_idx_map, packages_lst = _collect_packages()
    _serialize_data(packages_lst, PKGS_FILE)

    pkg_names = [p.name for p in packages_lst]
    del packages_lst  # to save some RAM...


    # Exporting apt-cache information to text files.
    # This is done as a Shell script since the Python version above crashes due to a memory leak: `version_idx_map = _extract_version_info(pkg_names)`
    if not Path(Path.home(), "pkginfo").is_dir():
        subprocess.run("bash bin/export_apt_data.sh")

    for p in pkg_names:
        bin_info = Path(Path.home(), "pkginfo", "bin", p)
        src_info = Path(Path.home(), "pkginfo", "src", p)

        if os.path.getsize(bin_info) > 0:
            with open(bin_info) as fp:
                bin_contents = fp.read()


        if os.path.getsize(src_info) > 0:
            with open(src_info) as fp:
                src_contents = fp.read()


        for line in bin_contents.splitlines():
            if not line:
                continue
        # TODO: do the same with src





#     versions_lst, version_dicts = _collect_versions(pkg_names, pkg_idx_map)
#     deps_lst = _collect_dependencies(version_dicts, pkg_idx_map)

#     _serialize_data(versions_lst, VERSIONS_FILE)
#     _serialize_data(deps_lst, DEPS_FILE)


# libc6-x32:amd64
# gcc-multilib:amd64
# g++-multilib:amd64
# g++-multilib:amd64
# gcc-multilib:amd64
# libc6-x32:amd64


if __name__ == "__main__":
    mine()


# Get all package names
# apt-cache dump | grep "Package: " | wc -l

# Get info about maintainers, homepage, etc. License missing?
# apt-cache show python-pyte


# Get info about versions and their dependencies
# apt-cache showpkg python-pyte
