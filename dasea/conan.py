import sys
import yaml
import json
import logging
import subprocess
from glob import glob
from pathlib import Path
from dataclasses import dataclass
from dasea.datamodel import Package, Version, Dependency, Kind
from dasea.utils import _serialize_data


CONAN_INDEX_URL = "https://github.com/conan-io/conan-center-index"
CONAN_INDEX_LOCAL = "data/tmp/conan/conan-center-index"
CONAN_METADATA = "data/tmp/conan/metadata"
PKGS_FILE = "data/out/conan/packages.csv"
VERSIONS_FILE = "data/out/conan/versions.csv"
DEPS_FILE = "data/out/conan/dependencies.csv"

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M"
)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)


@dataclass
class ConanVersion(Version):
    os_platform: str


@dataclass
class ConanDependency(Dependency):
    target_version_idx: str


def clone_index_repo():
    if Path(CONAN_INDEX_LOCAL).is_dir():
        cmd = f"git -C {CONAN_INDEX_LOCAL} pull"
    else:
        cmd = f"git clone -v {CONAN_INDEX_URL} {CONAN_INDEX_LOCAL}"

    r = subprocess.run(cmd, shell=True)
    if r.returncode != 0:
        raise IOError("Cannot clone/update Conan registry.")


def create_name_version_lst(pkg_config_files):
    name_version_lst = []
    for conf_file in pkg_config_files:
        with open(conf_file) as fp:
            conf_data = yaml.safe_load(fp)
        name = Path(conf_file).parts[-2]
        name_version_lst += [(name, version) for version in conf_data["versions"].keys()]
    return name_version_lst


def collect_dependency_info(name, version):
    # Remember that the `conan` tool has to be on PATH
    outfile = Path(CONAN_METADATA, name, f"{version}.json")
    if not outfile.is_file():
        cmd = f"conan info -n requires {name}/{version}@ --json {outfile}"
        r = subprocess.run(cmd, shell=True)
        if r.returncode != 0:
            # TODO: log cmd error message?
            LOGGER.error(f"Omitting {name}/{version}@ on {sys.platform}")


def read_meta_data(name, version):
    metafile = Path(CONAN_METADATA, name, f"{version}.json")
    with open(metafile) as fp:
        d = json.load(fp)
    return d


def generate_package_csv(pkg_names_map):
    csv_rows = []
    for idx, name in pkg_names_map.items():
        p = Package(idx, name, "conan", "C/C++")
        csv_rows.append(p.to_csv())

    # with open()


def _collect_packages(pkg_names_lst):
    pkg_idx_map = {name: idx for idx, name in enumerate(pkg_names_lst)}
    packages = []
    for pkg_name, idx in pkg_idx_map.items():
        p = Package(idx, pkg_name, "Conan", "C/C++")
        packages.append(p)

    return pkg_idx_map, packages


def _collect_versions(name_version_lst, metadata_lst, pkg_idx_map):
    versions = []
    version_idx_map = {}
    for version_idx, (pkg_name, version) in enumerate(name_version_lst):
        version_info = metadata_lst[version_idx][0]  # Entries for dependencies are provided after the first element

        v = ConanVersion(
            idx=version_idx,
            pkg_idx=pkg_idx_map.get(pkg_name, None),
            name=pkg_name,
            version=version,
            license=version_info["license"],
            description=version_info["description"],
            homepage=version_info["homepage"],
            repository=None,  # There is no information about it in the data
            author=None,
            maintainer=None,
            os_platform=sys.platform,
        )
        versions.append(v)
        version_idx_map[version_info["reference"]] = version_idx

    return version_idx_map, versions


def _collect_dependencies(name_version_lst, metadata_lst, pkg_idx_map, version_idx_map):
    deps = []
    for version_idx, (pkg_name, version) in enumerate(name_version_lst):
        version_info = metadata_lst[version_idx][0]

        for dep in version_info.get("requires", []):
            dep_name, dep_version = dep.split("/")
            d = ConanDependency(
                pkg_idx=pkg_idx_map.get(pkg_name, None),
                source_idx=version_idx,
                target_idx=pkg_idx_map[dep_name],
                source_name=pkg_name,
                target_name=dep_name,
                source_version=version,
                target_version=dep_version,
                kind=Kind.BUILD.name,
                target_version_idx=version_idx_map.get(dep, ""),
            )
            deps.append(d)
    return deps


def mine():
    try:
        clone_index_repo()
    except IOError as e:
        LOGGER.error(str(e))
        sys.exit(1)

    # Collect information about what packages exist in which versions
    glob_pattern = f"{CONAN_INDEX_LOCAL}/recipes/**/config.yml"
    pkg_config_files = glob(glob_pattern, recursive=True)
    name_version_lst = create_name_version_lst(pkg_config_files)

    # Collect for each package version a metadata JSON file via the `conan` tool
    # This takes ca. two hours, and it only collects information for packages that can be build on this platform.
    # TODO: Run the collection on Windows, Linux, and MacOS and subsequently
    # merge the collected data
    for name, version in name_version_lst:
        collect_dependency_info(name, version)

    # glob for the files here since not all packages have to have metadata, e.g., in case they
    # cannot be build on this os_platform
    glob_pattern = f"{CONAN_METADATA}/*"
    pkg_names_lst = sorted([Path(p).stem for p in glob(glob_pattern)])
    pkg_idx_map, packages_lst = _collect_packages(pkg_names_lst)

    glob_pattern = f"{CONAN_METADATA}/**/*.json"
    metadata_files = glob(glob_pattern, recursive=True)
    name_version_lst = [(Path(p).parts[-2], Path(p).stem) for p in metadata_files]

    metadata_lst = [read_meta_data(n, v) for n, v in name_version_lst]
    version_idx_map, versions_lst = _collect_versions(name_version_lst, metadata_lst, pkg_idx_map)

    deps_lst = _collect_dependencies(name_version_lst, metadata_lst, pkg_idx_map, version_idx_map)

    _serialize_data(packages_lst, PKGS_FILE)
    _serialize_data(versions_lst, VERSIONS_FILE)
    _serialize_data(deps_lst, DEPS_FILE)
