import csv
import requests
from dataclasses import dataclass
from dasea.datamodel import Package, Version, Dependency, Kind
from dasea.utils import _serialize_data


VCPKG_REGISTRY = "https://vcpkg.io/output.json"
PKGS_FILE = "data/out/vcpkg/packages.csv"
VERSIONS_FILE = "data/out/vcpkg/versions.csv"
DEPS_FILE = "data/out/vcpkg/dependencies.csv"


@dataclass
class VCPKGDependency(Dependency):
    os_platform: str


def _collect_pkg_registry():
    r = requests.get(VCPKG_REGISTRY)
    if not r.ok:
        raise IOError("Cannot download VCPKG registry.")
    metadata_lst = r.json()["Source"]
    return metadata_lst


def _collect_packages(metadata_lst):
    pkg_idx_map = {d["Name"]: idx for idx, d in enumerate(metadata_lst)}
    packages = []
    for pkg_name, idx in pkg_idx_map.items():
        p = Package(idx, pkg_name, "VCPKG", "C/C++")
        packages.append(p)

    return pkg_idx_map, packages


def _collect_versions(metadata_lst, pkg_idx_map):
    versions = []
    for version_idx, data in enumerate(metadata_lst):
        pkg_name = data["Name"]
        pkg_idx = pkg_idx_map.get(pkg_name, None)
        v = Version(
            idx=version_idx,
            pkg_idx=pkg_idx,
            name=data["Name"],
            version=data["Version"],
            license=data.get("License", ""),
            description=data.get("Description"),
            homepage=data.get("Homepage", ""),
            repository=None,
            author=None,
            maintainer=data.get("Maintainers", ""),
        )
        versions.append(v)
    return versions


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
    try:
        metadata_lst = _collect_pkg_registry()
    except IOError as e:
        # TODO: log error here
        sys.exit(1)
    pkg_names = [d["Name"] for d in metadata_lst]

    pkg_idx_map, packages_lst = _collect_packages(metadata_lst)
    versions_lst = _collect_versions(metadata_lst, pkg_idx_map)
    deps_lst = _collect_dependencies(metadata_lst, pkg_idx_map)

    _serialize_data(packages_lst, PKGS_FILE)
    _serialize_data(versions_lst, VERSIONS_FILE)
    _serialize_data(deps_lst, DEPS_FILE)


if __name__ == "__main__":
    mine()
