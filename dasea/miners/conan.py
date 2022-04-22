from cmath import log
import sys
import requests
from tqdm import tqdm
import json
import logging
import subprocess
from glob import glob
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from dasea.common.datamodel import Package, Version, Dependency, Kind
from dasea.common.utils import _serialize_data

# Based on the requests executed here:
# https://conan.io/center/glib

CONAN_REGISTRY = "https://conan.io/center/api/ui/allpackages"
CONAN_PACKAGE_URL ="https://conan.io/center/api/ui/details?name={pkg_name}&user=_&channel=_"
CONAN_REVISIONS_URL = "https://conan.io/center/api/ui/revisions?name={pkg_name}&version={version}&user=_&channel=_"
CONAN_DEPENDENCIES_URL = "https://conan.io/center/api/ui/dependencies?name={pkg_name}&version={version}&user=_&channel=_&revision={revision}"


HEADERS = {
    "User-Agent": "DaSEA Research Project (Please don't ban, https://dasea.org)",
    "From": "daseaITU@gmail.com",
}

TODAY = datetime.today().strftime("%m-%d-%Y")
PKGS_FILE = f"data/out/conan/conan_packages_{TODAY}.csv"
VERSIONS_FILE = f"data/out/conan/conan_versions_{TODAY}.csv"
DEPS_FILE = f"data/out/conan/conan_dependencies_{TODAY}.csv"

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M"
)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

@dataclass
class ConanDependency(Dependency):
    revision: str

def _collect_pkg_registry():
    r = requests.get(CONAN_REGISTRY, headers=HEADERS)
    if not r.ok:
        raise IOError("Cannot download CONAN registry.")
    metadata_lst = r.json()["packages"]
    return metadata_lst

def _collect_packages(metadata_lst):
    pkg_idx_map = {d["name"]: idx for idx, d in enumerate(metadata_lst)}
    packages = []
    for pkg_name, idx in pkg_idx_map.items():
        p = Package(idx, pkg_name, "Conan")
        packages.append(p)
    return pkg_idx_map, packages

def _collect_versions(metadata_lst, pkg_idx_map):
    versions = []
    version_idx = 0

    for pkg in tqdm(metadata_lst):
        pkg_name = pkg["name"]
        pkg_idx = pkg_idx_map.get(pkg_name, None)
        versions_url = CONAN_PACKAGE_URL.format(pkg_name=pkg_name)

        versions_req = requests.get(versions_url, headers=HEADERS)
        if not versions_req.ok:
            LOGGER.error(versions_req.status_code, "PACKAGE VERSIONS", pkg_name)
            continue

        versions_data = versions_req.json()["versions"]
        additional_package_data = versions_req.json()
        for version_data in versions_data:
            v = Version(
                idx=version_idx,
                pkg_idx=pkg_idx,
                name=pkg_name,
                version=version_data.get("version", ""),
                license=version_data.get("license", ""),
                description=pkg.get("description"),
                homepage=additional_package_data.get("homepage", ""),
                repository=None,
                author=None,
                maintainer=None,
            )
            versions.append(v)
            version_idx += 1

    return versions


def _collect_dependencies(versions_lst, pkg_idx_map):
    dependencies = []

    for version_data in tqdm(versions_lst):
        pkg_name = version_data.name
        source_pkg_idx = version_data.pkg_idx
        version_idx = version_data.idx
        source_version = version_data.version

        ## Get latest revision for version
        revisions_url = CONAN_REVISIONS_URL.format(pkg_name=pkg_name, version=source_version)
        revisions_req = requests.get(revisions_url, headers=HEADERS)
        if not revisions_req.ok:
            LOGGER.error(revisions_req.status_code, "VERSION REVISIONS", source_version)
            continue

        ## Based on how they fetch data for a package on their website, ex: https://conan.io/center/openssl

        if len(revisions_req.json()["revisions"]) == 0:
            LOGGER.error("MISSING REVISIONS", pkg_name, source_version)
            continue

        latest_revision = revisions_req.json()["revisions"][0]


        ## Get dependencies for version + latest revision
        dependencies_url = CONAN_DEPENDENCIES_URL.format(pkg_name=pkg_name, version=source_version, revision=latest_revision)

        dep_req = requests.get(dependencies_url, headers=HEADERS)
        if not dep_req.ok:
            LOGGER.error(dep_req.status_code, "VERSION REVISIONS", source_version)
            continue
        dependencies_data = dep_req.json()

        for dependency in dependencies_data.get("dependencies", []):
            if dependency["name_version"] == '':
                continue

            split_name_and_version = dependency["name_version"].split("/")
            if(len(split_name_and_version) != 2):
                LOGGER.error("Invalid dependency name_version", dependency["name_version"])
                continue

            dep_name = split_name_and_version[0]
            dep_version = split_name_and_version[1]

            d = ConanDependency(
                pkg_idx=source_pkg_idx,
                source_idx=version_idx,
                target_idx=pkg_idx_map[dep_name],
                source_name=pkg_name,
                target_name=dep_name,
                source_version=source_version,
                target_version=dep_version,
                kind=Kind.BUILD.name,
                revision=latest_revision
            )
            dependencies.append(d)
    return dependencies



def mine():
    LOGGER.info("Collecting Conan registry")
    try:
        metadata_lst = _collect_pkg_registry()
    except IOError as e:
        LOGGER.error(str(e))
        sys.exit(1)

    LOGGER.info("Creating DaSEA packages...")
    pkg_idx_map, packages_lst = _collect_packages(metadata_lst)

    LOGGER.info("Creating DaSEA versions...")
    versions_lst = _collect_versions(metadata_lst, pkg_idx_map)

    LOGGER.info("Creating DaSEA dependencies...")
    deps_lst = _collect_dependencies(versions_lst, pkg_idx_map)

    _serialize_data(packages_lst, PKGS_FILE)
    _serialize_data(versions_lst, VERSIONS_FILE)
    _serialize_data(deps_lst, DEPS_FILE)
