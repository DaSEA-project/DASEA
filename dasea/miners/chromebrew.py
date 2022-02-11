import sys
import csv
import logging
import requests
import git
import os
import re
import shutil
from datetime import datetime
from core.common.datamodel import Package, Version, Dependency, Kind
from core.common.utils import _serialize_data

CHROMEBREW_REGISTRY = "https://github.com/skycocker/chromebrew"
TMP_DIR = "./data/tmp/chromebrew"

TODAY = datetime.today().strftime("%m-%d-%Y")
PKGS_FILE = f"data/out/chromebrew/chromebrew_packages_{TODAY}.csv"
VERSIONS_FILE = f"data/out/chromebrew/chromebrew_versions_{TODAY}.csv"
DEPS_FILE = f"data/out/chromebrew/chromebrew_dependencies_{TODAY}.csv"

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M"
)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)


def _collect_pkg_registry():
    try:
        git.Repo.clone_from(CHROMEBREW_REGISTRY, TMP_DIR)
    except Exception as err:
        raise IOError("Cannot download Chromebew registry.")


def _get_pkg_names():
    pkg_names = []
    file_names = os.listdir(TMP_DIR + "/packages")

    for file_name in file_names:
        pkg_names.append(file_name.replace(".rb", ""))

    return pkg_names


def _collect_packages(metadata_dict):
    LOGGER.info("Collecting Chromebrew registry...")
    pkg_idx_map = {}
    packages = []
    for idx, pkg_name in enumerate(metadata_dict):
        p = Package(idx, pkg_name, "Chromebrew")
        packages.append(p)
        pkg_idx_map[pkg_name] = idx

    return pkg_idx_map, packages


def _collect_versions(pkg_idx_map):
    versions = []
    version_idx = 0
    file_names = os.listdir(TMP_DIR + "/packages")
    for file_name in file_names:
        with open(TMP_DIR + "/packages/" + file_name, "r") as file:
            pkg_name = file_name.replace(".rb", "")
            pkg_idx = pkg_idx_map.get(pkg_name, None)

            for line in file:
                if "description '" in line:
                    description = re.sub("description ", "", line).strip().strip("'")

                if "homepage '" in line:
                    homepage = re.sub("homepage ", "", line).strip().strip("'")

                if "version '" in line:
                    version = re.sub("version ", "", line).strip().strip("'")

                if "@_ver = '" in line:
                    version = re.sub("@_ver = ", "", line).strip().strip("'")

                if "license '" in line:
                    license = re.sub("license ", "", line).strip().strip("'")

                if "source_url '" in line:
                    repository = re.sub("source_url ", "", line).strip().strip("'")

            v = Version(
                idx=version_idx,
                pkg_idx=pkg_idx,
                name=pkg_name,
                version=version,
                description=description,
                homepage=homepage,
                license=license,
                repository=repository,
                author=None,
                maintainer=None,
            )
            versions.append(v)
            version_idx += 1
    return versions


def _collect_dependencies(versions_lst, pkg_idx_map):
    deps = []
    version_idx = 0

    file_names = os.listdir(TMP_DIR + "/packages")
    for file_name in file_names:
        with open(TMP_DIR + "/packages/" + file_name, "r") as file:
            pkg_name = file_name.replace(".rb", "")
            source_pkg_idx = pkg_idx_map.get(pkg_name, None)

            for line in file:
                if "depends_on '" in line:
                    dependencies = re.findall("'([^']*)'", line)

                    for dependency in dependencies:
                        dep_name = dependency.strip("'")
                        target_pkg_idx = pkg_idx_map.get(dep_name, None)

                        d = Dependency(
                            pkg_idx=source_pkg_idx,
                            source_idx=version_idx,
                            target_idx=target_pkg_idx,
                            source_name=pkg_name,
                            target_name=dep_name,
                            source_version=versions_lst[version_idx].version,
                            target_version=versions_lst[target_pkg_idx].version if target_pkg_idx != None else None,
                            # double check this
                            kind=Kind.BUILD.name,
                        )
                        deps.append(d)
    version_idx += 1

    return deps


def mine():
    try:
        _collect_pkg_registry()
    except IOError as e:
        LOGGER.error(str(e))
        sys.exit(1)

    pkg_names = _get_pkg_names()
    LOGGER.info("Creating DaSEA packages...")
    pkg_idx_map, packages_lst = _collect_packages(pkg_names)
    LOGGER.info("Creating DaSEA versions...")
    versions_lst = _collect_versions(pkg_idx_map)
    LOGGER.info("Creating DaSEA dependencies...")
    deps_lst = _collect_dependencies(versions_lst, pkg_idx_map)

    _serialize_data(packages_lst, PKGS_FILE)
    _serialize_data(versions_lst, VERSIONS_FILE)
    _serialize_data(deps_lst, DEPS_FILE)

    # delete cloned repo
    shutil.rmtree(TMP_DIR, ignore_errors=True)


if __name__ == "__main__":
    mine()
