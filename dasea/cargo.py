import os
import json
import logging
import operator
import requests
import itertools
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
from dataclasses import dataclass
from collections import defaultdict
from dasea.datamodel import Package, Version, Dependency, Kind
from dasea.utils import _serialize_data


# Based on the documentation form here:
CRATES_URL = "https://crates.io/api/v1/crates?page={page_idx}&per_page=100"
CRATE_URL = "https://crates.io/api/v1/crates/{name}"
VERSION_URL = "https://crates.io/api/v1/crates/{name}/{version}/dependencies"
INDEX_FILE = "data/tmp/cargo/crates_index.json"


TODAY = datetime.today().strftime("%m-%d-%Y")
PKGS_FILE = f"data/out/cargo/cargo_packages_{TODAY}.csv"
VERSIONS_FILE = f"data/out/cargo/cargo_versions_{TODAY}.csv"
DEPS_FILE = f"data/out/cargo/cargo_dependencies_{TODAY}.csv"


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M"
)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)


@dataclass
class CargoPackage(Package):
    description: str
    homepage: str
    repository: str


@dataclass
class CargoVersion(Version):
    author_nick: str
    created_at: str
    updated_at: str
    no_downloads: int


@dataclass
class CargoDependency(Dependency):
    kind_str: str
    optional: bool
    target: str


def _collect_pkg_metadata():
    if os.path.isfile(INDEX_FILE):
        with open(INDEX_FILE) as fp:
            crates_info = json.load(fp)
        return crates_info

    LOGGER.info("Collecting package index from the web, it takes some time...")
    page_idx = 1
    r = requests.get(CRATES_URL.format(page_idx=page_idx))
    r.raise_for_status()

    crates_info = r.json()["crates"]
    next_page = r.json()["meta"]["next_page"]
    while next_page:
        if page_idx % 50 == 0:
            print(page_idx)
        r = requests.get(CRATES_URL.format(page_idx=page_idx))
        crates_info += r.json()["crates"]
        next_page = r.json()["meta"]["next_page"]
        page_idx += 1

    with open(INDEX_FILE, "w") as fp:
        json.dump(crates_info, fp)
    return crates_info


def _parse_crates(crates_docs):
    keep = [
        # "id",  # Names and ids are always the same, so keep only one of them
        "name",
        "description",
        "homepage",
        "repository",
        "downloads",
        "created_at",
        "updated_at",
    ]
    crates_infos = []
    for c in crates_docs:
        crate_info = {}
        for col in keep:
            crate_info[col] = c[col]
        crates_infos.append(crate_info)
    return crates_infos


def _collect_version_metadata(pkgs_name_lst):
    LOGGER.info("Collecting package versions from the web, it takes some hours..")
    pkg_versions_map = {}
    for pkg_name in pkgs_name_lst:
        r = requests.get(CRATE_URL.format(name=pkg_name))
        if not r.ok:
            # print(r.status_code, "PKG", pkg_name)
            LOGGER.warning(f"{r.status_code} PKG {pkg_name}")
            continue
        pkg_versions_map[pkg_name] = r.json()["versions"]
    return pkg_versions_map


def _collect_dependency_metadata(version_idx_map):
    LOGGER.info("Collecting version dependencies from the web, it takes some hours..")
    version_deps_map = defaultdict(dict)
    for pkg_name, version_info in version_idx_map.items():
        for version_num, version_idx in version_info.items():
            print(pkg_name, version_num)
            r = requests.get(VERSION_URL.format(name=pkg_name, version=version_num))
            if not r.ok:
                # print(r.status_code, "VERSION", pkg_name, version_num)
                LOGGER.warning(f"{r.status_code} VERSION {pkg_name} {version_num}")
                continue

            version_deps_map[pkg_name][version_num] = r.json().get("dependencies", [])
    return version_deps_map


def _collect_packages(pkg_name_lst):
    packages = []
    pkg_idx_map = {}
    for idx, pkg_info in enumerate(pkg_name_lst):
        p = CargoPackage(
            idx=idx,
            name=pkg_info["name"],
            pkgman="Cargo",
            description=pkg_info["description"],
            homepage=pkg_info["homepage"],
            repository=pkg_info["repository"],
        )
        packages.append(p)
        pkg_idx_map[pkg_info["name"]] = idx

    return pkg_idx_map, packages


def _collect_versions(version_metadata_dict, pkg_idx_map):
    versions = []
    version_idx = 0
    version_idx_map = defaultdict(dict)
    for pkg_name, version_info_lst in version_metadata_dict.items():
        for version_info in version_info_lst:
            crate = {}
            if type(version_info["crate"]) == dict:
                crate = version_info["crate"]
            published_by = {}
            if version_info["published_by"]:
                published_by = version_info["published_by"]

            v = CargoVersion(
                idx=version_idx,
                pkg_idx=pkg_idx_map.get(pkg_name, None),
                name=pkg_name,
                version=version_info["num"],
                license=version_info["license"],
                description=crate.get("description", None),
                homepage=published_by.get("url", None),
                repository=crate.get("repository", None),
                author=published_by.get("name", None),  # or shall the login be taken?
                maintainer=None,  # There is no such information
                author_nick=published_by.get("login", None),
                created_at=version_info["created_at"],
                updated_at=version_info["updated_at"],
                no_downloads=version_info["downloads"],
            )
            versions.append(v)
            version_idx += 1

            version_idx_map[pkg_name][version_info["num"]] = version_idx

    return version_idx_map, versions


def _collect_dependencies(version_idx_map, deps_metadata_dict, pkg_idx_map):
    deps = []
    dep_kind_map = {
        "normal": Kind.NORMAL.name,
        "dev": Kind.DEV.name,
        "build": Kind.BUILD.name,
    }

    for pkg_name, version_idx_lst in version_idx_map.items():
        for version_num, version_idx in version_idx_lst.items():
            for dep_info in deps_metadata_dict[pkg_name][version_num]:
                d = CargoDependency(
                    pkg_idx=pkg_idx_map.get(pkg_name, None),
                    source_idx=version_idx,
                    target_idx=pkg_idx_map[dep_info["crate_id"]],
                    source_name=pkg_name,
                    target_name=dep_info["crate_id"],
                    source_version=version_idx,
                    target_version=dep_info["req"],
                    kind=dep_kind_map.get(dep_info["kind"], None),  # Kind.BUILD.name,
                    kind_str=dep_info["kind"],
                    optional=dep_info["optional"],
                    target=dep_info["target"],
                )
                deps.append(d)
    return deps


def mine():
    pkg_metadata_dict = _collect_pkg_metadata()
    pkgs_lst = _parse_crates(pkg_metadata_dict)
    LOGGER.info(f"There should be {len(pkgs_lst)} pkgs in the end.")
    pkg_idx_map, packages_lst = _collect_packages(pkgs_lst)
    _serialize_data(packages_lst, PKGS_FILE)

    pkgs_name_lst = [p["name"] for p in pkgs_lst]
    version_metadata_dict = _collect_version_metadata(pkgs_name_lst)
    # -->
    version_idx_map, versions_lst = _collect_versions(version_metadata_dict, pkg_idx_map)
    _serialize_data(versions_lst, VERSIONS_FILE)
    del versions_lst  # Free some RAM
    del version_metadata_dict

    deps_metadata_dict = _collect_dependency_metadata(version_idx_map)
    deps_lst = _collect_dependencies(version_idx_map, deps_metadata_dict, pkg_idx_map)
    _serialize_data(deps_lst, DEPS_FILE)

    # os.remove(INDEX_FILE)


if __name__ == "__main__":
    mine()
