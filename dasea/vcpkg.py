import logging
import requests
from datetime import datetime
from dataclasses import dataclass
from dasea.datamodel import Package, Version, Dependency, Kind
from dasea.utils import _serialize_data


VCPKG_REGISTRY = "https://vcpkg.io/output.json"

TODAY = datetime.today().strftime("%m-%d-%Y")
PKGS_FILE = f"data/out/vcpkg/vcpkg_packages_{TODAY}.csv"
VERSIONS_FILE = f"data/out/vcpkg/vcpkg_versions_{TODAY}.csv"
DEPS_FILE = f"data/out/vcpkg/vcpkg_dependencies_{TODAY}.csv"

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M"
)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)


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
        p = Package(idx, pkg_name, "VCPKG")
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
        LOGGER.error(str(e))
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
