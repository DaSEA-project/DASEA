import sys
import csv
import requests
from dasea.datamodel import Package, Version, Dependency, Kind
from dasea.utils import _serialize_data

FPM_REGISTRY = "https://raw.githubusercontent.com/fortran-lang/fpm-registry/master/index.json"
PKGS_FILE = "data/out/fpm/packages.csv"
VERSIONS_FILE = "data/out/fpm/versions.csv"
DEPS_FILE = "data/out/fpm/dependencies.csv"


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
        p = Package(idx, pkg_name, "FPM", "Fortran")
        packages.append(p)
        pkg_idx_map[pkg_name] = idx

    return pkg_idx_map, packages


def _collect_versions(metadata_dict, pkg_idx_map):
    # TODO: Kasper does some cleaning of the metadata_dict. Understand what and why!
    versions = []
    version_idx_map = {}
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
            version_idx_map[version_info["name"]] = version_idx
            version_idx += 1
    return version_idx_map, versions


def _collect_dependencies(metadata_dict, pkg_idx_map, versions_idx_map):
    deps = []
    for idx, (pkg_name, data) in enumerate(metadata_dict.items()):
        for version, version_info in data.items():
            source_pkg_idx = pkg_idx_map.get(pkg_name, None)
            for dep_name, dep_info in version_info.get("dependencies", {}).items():
                d = Dependency(
                    pkg_idx=source_pkg_idx,
                    source_idx=versions_idx_map[version_info["name"]],
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
            for dep_name, dep_info in version_info.get("dev-dependencies", {}).items():
                d = Dependency(
                    pkg_idx=source_pkg_idx,
                    source_idx=versions_idx_map[version_info["name"]],
                    target_idx=pkg_idx_map.get(dep_name, ""),
                    source_name=version_info["name"],
                    target_name=dep_name,
                    source_version=version_info["version"],
                    target_version=dep_info.get("tag", "") or dep_info.get("rev", ""),
                    kind=Kind.DEV.name,
                )
                deps.append(d)
    return deps


def mine():
    try:
        metadata_dict = _collect_pkg_registry()
    except IOError as e:
        # TODO: log error here
        sys.exit(1)
    pkg_names = list(metadata_dict.keys())

    pkg_idx_map, packages_lst = _collect_packages(metadata_dict)
    version_idx_map, versions_lst = _collect_versions(metadata_dict, pkg_idx_map)
    deps_lst = _collect_dependencies(metadata_dict, pkg_idx_map, version_idx_map)

    _serialize_data(packages_lst, PKGS_FILE)
    _serialize_data(versions_lst, VERSIONS_FILE)
    _serialize_data(deps_lst, DEPS_FILE)


if __name__ == "__main__":
    mine()
