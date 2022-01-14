import sys
import csv
import logging
import requests
from datetime import datetime
from dasea.datamodel import Package, Version, Dependency, Kind
from dasea.utils import _serialize_data


FPM_REGISTRY = "https://raw.githubusercontent.com/fortran-lang/fpm-registry/master/index.json"

TODAY = datetime.today().strftime("%m-%d-%Y")
PKGS_FILE = f"data/out/fpm/fpm_packages_{TODAY}.csv"
VERSIONS_FILE = f"data/out/fpm/fpm_versions_{TODAY}.csv"
DEPS_FILE = f"data/out/fpm/fpm_dependencies_{TODAY}.csv"

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M"
)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)


def _collect_pkg_registry():
    r = requests.get(FPM_REGISTRY)
    if not r.ok:
        raise IOError("Cannot download FPM registry.")
    metadata_dict = r.json()["packages"]
    return metadata_dict


def _collect_packages(metadata_dict):
    pkg_idx_map = {}
    packages = []
    for idx, (pkg_name, _) in enumerate(metadata_dict.items()):
        p = Package(idx, pkg_name, "FPM")
        packages.append(p)
        pkg_idx_map[pkg_name] = idx

    return pkg_idx_map, packages


def _collect_versions(metadata_dict, pkg_idx_map):
    # TODO: Kasper does some cleaning of the metadata_dict. Understand what and why!
    versions = []
    version_idx = 0
    for pkg_name, data in metadata_dict.items():
        for version, version_info in data.items():
            pkg_idx = pkg_idx_map.get(pkg_name, None)
            v = Version(
                idx=version_idx,
                pkg_idx=pkg_idx,
                name=version_info["name"],
                version=version_info["version"],
                license=version_info["license"],
                description=version_info["description"],
                homepage=None,  # There is no information about it in the response
                repository=version_info["git"],
                author=version_info["author"],
                maintainer=version_info["maintainer"],
            )
            versions.append(v)
            version_idx += 1
    return versions


def _collect_dependencies(metadata_dict, pkg_idx_map):
    deps = []
    version_idx = 0
    for idx, (pkg_name, data) in enumerate(metadata_dict.items()):
        for version, version_info in data.items():
            source_pkg_idx = pkg_idx_map.get(pkg_name, None)

            deps_decl = version_info.get("dependencies", {})
            dev_deps_decl = version_info.get("dev-dependencies", {})
            if deps_decl == None:
                # sometimes there is an explicit None value stored
                deps_decl = {}
            if dev_deps_decl == None:
                dev_deps_decl = {}

            for dep_name, dep_info in deps_decl.items():
                d = Dependency(
                    pkg_idx=source_pkg_idx,
                    source_idx=version_idx,
                    target_idx=pkg_idx_map.get(
                        dep_name, ""
                    ),  # There are packages provided as dependencies, which do not exist on the registry, but which are referred to and downloaded from, e.g., Github
                    source_name=version_info["name"],
                    target_name=dep_name,
                    source_version=version_info["version"],
                    target_version=dep_info.get("tag", "") or dep_info.get("rev", ""),
                    kind=Kind.BUILD.name,
                )
                deps.append(d)
            for dep_name, dep_info in dev_deps_decl.items():
                d = Dependency(
                    pkg_idx=source_pkg_idx,
                    source_idx=version_idx,
                    target_idx=pkg_idx_map.get(dep_name, ""),
                    source_name=version_info["name"],
                    target_name=dep_name,
                    source_version=version_info["version"],
                    target_version=dep_info.get("tag", "") or dep_info.get("rev", ""),
                    kind=Kind.DEV.name,
                )
                deps.append(d)
            version_idx += 1

    return deps


def mine():
    try:
        metadata_dict = _collect_pkg_registry()
    except IOError as e:
        LOGGER.error(str(e))
        sys.exit(1)
    pkg_names = list(metadata_dict.keys())

    pkg_idx_map, packages_lst = _collect_packages(metadata_dict)
    versions_lst = _collect_versions(metadata_dict, pkg_idx_map)
    deps_lst = _collect_dependencies(metadata_dict, pkg_idx_map)

    _serialize_data(packages_lst, PKGS_FILE)
    _serialize_data(versions_lst, VERSIONS_FILE)
    _serialize_data(deps_lst, DEPS_FILE)


if __name__ == "__main__":
    mine()
