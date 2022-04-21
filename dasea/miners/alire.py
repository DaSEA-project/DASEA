import sys
import toml
import shutil
import logging
import subprocess
from glob import glob
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from dasea.common.utils import _serialize_data
from dasea.common.datamodel import Package, Version, Dependency, Kind


ALIRE_INDEX_URL = "https://github.com/alire-project/alire-index.git"
ALIRE_INDEX_LOCAL = "data/tmp/alire/alire-index"

TODAY = datetime.today().strftime("%m-%d-%Y")
PKGS_FILE = f"data/out/alire/alire_packages_{TODAY}.csv"
VERSIONS_FILE = f"data/out/alire/alire_versions_{TODAY}.csv"
DEPS_FILE = f"data/out/alire/alire_dependencies_{TODAY}.csv"


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M"
)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)


@dataclass
class AlireDependency(Dependency):
    os_platform: str


def clone_index_repo():
    LOGGER.info("Collecting Alire registry")
    if Path(ALIRE_INDEX_LOCAL).is_dir():
        cmd = f"git -C {ALIRE_INDEX_LOCAL} pull"
    else:
        cmd = f"git clone -v {ALIRE_INDEX_URL} {ALIRE_INDEX_LOCAL}"

    r = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if r.returncode != 0:
        raise IOError("Cannot clone/update Alire registry.")


def read_meta_data(metafile):
    with open(metafile) as fp:
        d = toml.load(fp)
    return d


def _collect_packages(pkg_name_lst):
    pkg_idx_map = {n: idx for idx, n in enumerate(pkg_name_lst)}
    packages = []
    for pkg_name, idx in pkg_idx_map.items():
        p = Package(idx, pkg_name, "Alire")
        packages.append(p)

    return pkg_idx_map, packages


# Remove version index map?
def _collect_versions(metadata_lst, pkg_idx_map):
    versions = []
    for version_idx, version_info in enumerate(metadata_lst):
        pkg_name = version_info["name"]
        v = Version(
            idx=version_idx,
            pkg_idx=pkg_idx_map.get(pkg_name, None),
            name=pkg_name,
            version=version_info.get("version", ""),
            license=version_info.get("licenses", ""),
            description=version_info.get("description"),
            homepage=version_info.get("website", ""),
            repository=version_info.get("origin", {}).get("url", ""),
            author=version_info.get("authors", ""),
            maintainer=version_info["maintainers"],
        )
        versions.append(v)

    return versions


def _collect_dependencies(metadata_lst, pkg_idx_map):
    deps = []
    for version_idx, version_info in enumerate(metadata_lst):
        pkg_name = version_info["name"]
        source_pkg_idx = pkg_idx_map.get(pkg_name, None)
        for dep_info in version_info.get("depends-on", []):
            for target_name, target_version in dep_info.items():
                if target_name == "case(os)":
                    # 'case(os)': {'windows': {'winpthreads': '*'}}
                    for os_platform, d_info in target_version.items():
                        for target_name, target_version in d_info.items():
                            d = AlireDependency(
                                pkg_idx=source_pkg_idx,
                                source_idx=version_idx,
                                target_idx=pkg_idx_map.get(target_name, None),
                                source_name=pkg_name,
                                target_name=target_name,
                                source_version=version_info["version"],
                                target_version=target_version,
                                kind=Kind.BUILD.name,
                                os_platform=os_platform,
                            )
                else:
                    d = AlireDependency(
                        pkg_idx=source_pkg_idx,
                        source_idx=version_idx,
                        target_idx=pkg_idx_map.get(target_name, None),
                        source_name=pkg_name,
                        target_name=target_name,
                        source_version=version_info["version"],
                        target_version=target_version,
                        kind=Kind.BUILD.name,
                        os_platform=None,
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
    glob_pattern = f"{ALIRE_INDEX_LOCAL}/index/**/*.toml"
    pkg_config_files = glob(glob_pattern, recursive=True)
    # Remove 'index/index.toml', which does not describe a package
    pkg_config_files.remove(str(Path(ALIRE_INDEX_LOCAL, "index", "index.toml")))

    pkg_name_lst = sorted(set([Path(p).parts[-2] for p in pkg_config_files]))
    metadata_lst = [read_meta_data(p) for p in pkg_config_files]

    LOGGER.info("Creating DaSEA packages...")
    pkg_idx_map, packages_lst = _collect_packages(pkg_name_lst)
    LOGGER.info("Creating DaSEA versions...")
    versions_lst = _collect_versions(metadata_lst, pkg_idx_map)
    LOGGER.info("Creating DaSEA dependencies...")
    deps_lst = _collect_dependencies(metadata_lst, pkg_idx_map)

    _serialize_data(packages_lst, PKGS_FILE)
    _serialize_data(versions_lst, VERSIONS_FILE)
    _serialize_data(deps_lst, DEPS_FILE)

    shutil.rmtree(ALIRE_INDEX_LOCAL)


if __name__ == "__main__":
    mine()
