import sys
import logging
import requests
from datetime import datetime
from dasea.common.datamodel import Package, Version, Dependency, Kind
from dasea.common.utils import _serialize_data

# Based on the documentation form here:
# https://github.com/clojars/clojars-web/wiki/Data

CLOJARS_REGISTRY = "https://repo.clojars.org/all-jars.clj"

TODAY = datetime.today().strftime("%m-%d-%Y")
PKGS_FILE = f"data/out/clojars/clojars_packages_{TODAY}.csv"
VERSIONS_FILE = f"data/out/clojars/clojars_versions_{TODAY}.csv"
DEPS_FILE = f"data/out/clojars/clojars_dependencies_{TODAY}.csv"


import os
import csv
import operator
import itertools
from bs4 import BeautifulSoup


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M"
)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)


def _collect_pkg_registry():
    LOGGER.info("Collecting Clojars registry...")
    r = requests.get(CLOJARS_REGISTRY)
    if not r.ok:
        raise IOError("Cannot download FPM registry.")

    jars = set([])
    for line in r.text.splitlines():
      # Remove the brackets
      jar_name, _ = line[1:-1].split()
      jars.add(jar_name)

    return sorted(list(jars))



def _collect_packages(metadata_dict):
    pkg_idx_map = {}
    packages = []
    for idx, pkg_name in enumerate(metadata_dict):
        p = Package(idx, pkg_name, "Clojars")
        packages.append(p)
        pkg_idx_map[pkg_name] = idx

    return pkg_idx_map, packages


def _collect_versions(metadata_dict, pkg_idx_map):
    versions = []
    version_idx = 0
    for pkg_name in metadata_dict:

        # Request the package data
        r = requests.get(f"https://clojars.org/repo/{pkg_name}")
        package_versions = []
        # TODO: https://clojars.org/search?q=reveal&format=json
        # FIXME: stopped here
        # for _, version_info in data.items():
        #     # Add version number to list, to check if version appears more than once in package registry
        #     if version_info["version"] in package_versions:
        #         continue

        #     package_versions.append(version_info["version"])
        #     pkg_idx = pkg_idx_map.get(pkg_name, None)
        #     v = Version(
        #         idx=version_idx,
        #         pkg_idx=pkg_idx,
        #         name=version_info["name"],
        #         version=version_info["version"],
        #         license=version_info["license"],
        #         description=version_info["description"],
        #         homepage=None,  # There is no information about it in the response
        #         repository=version_info["git"],
        #         author=version_info["author"],
        #         maintainer=version_info["maintainer"],
        #     )
        #     versions.append(v)
        #     version_idx += 1
    return versions


def _collect_dependencies(metadata_dict, pkg_idx_map):
    deps = []
    version_idx = 0
    for idx, (pkg_name, data) in enumerate(metadata_dict.items()):
        package_versions = []
        for version, version_info in data.items():
            # Add version number to list, to check if version appears more than once in package registry
            if version in package_versions:
                continue
            package_versions.append(version_info["version"])

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
    # pkg_names = list(metadata_dict.keys())
    print(f"Found {len(metadata_dict)} packages in registry.")
    # print(metadata_dict)
    LOGGER.info("Creating metadata_dict packages...")
    pkg_idx_map, packages_lst = _collect_packages(metadata_dict)
    LOGGER.info("Creating DaSEA versions...")

    versions_lst = _collect_versions(metadata_dict, pkg_idx_map)
    # LOGGER.info("Creating DaSEA dependencies...")
    # deps_lst = _collect_dependencies(metadata_dict, pkg_idx_map)

    # _serialize_data(packages_lst, PKGS_FILE)
    # _serialize_data(versions_lst, VERSIONS_FILE)
    # _serialize_data(deps_lst, DEPS_FILE)


if __name__ == "__main__":
    mine()
