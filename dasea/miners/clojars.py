import sys
import logging
import requests
from datetime import datetime
from dasea.common.datamodel import Package, Version, Dependency, Kind
from dasea.common.utils import _serialize_data
from tqdm import tqdm

# Based on the documentation form here:
# https://github.com/clojars/clojars-web/wiki/Data

# TODO: https://clojars.org/search?q=reveal&format=json
CLOJARS_REGISTRY = "https://repo.clojars.org/all-jars.clj"
CLOJARS_PACKAGE_URL =  "https://clojars.org/api/artifacts/{jar_name}"
CLOJARS_VERSION_URL = "https://clojars.org/{pkg_name}/versions/{version}"

HEADERS = {
    "User-Agent": "DaSEA Research Project (Please don't ban, daseaITU@gmail.com)",
    "From": "daseaITU@gmail.com",
}

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


def _collect_versions_with_dependencies(metadata_dict, pkg_idx_map):
    versions = dependencies = []
    version_idx = 0
    for pkg_name in tqdm(metadata_dict):
        # Request the package data
        r = requests.get(CLOJARS_PACKAGE_URL.format(jar_name=pkg_name), headers=HEADERS)
        if not r.ok:
            print(r.status_code, "PKG", pkg_name)
            continue
        package_versions = r.json()["recent_versions"]
        for package_version in package_versions:
            version_number = package_version['version']
            pkg_idx = pkg_idx_map.get(pkg_name, None)

            # Scrape the package version data
            version_info = scrape_package_version_info(pkg_name, version_number)

            try:
                v = Version(
                    idx=version_idx,
                    pkg_idx=pkg_idx,
                    # name=version_info["name"],
                    name=pkg_name,
                    version=version_number,
                    license=version_info["license"],
                    description=version_info["description"],
                    homepage=None,  # There is no information about it in the response
                    repository=version_info["repository"],
                    author=version_info["author"],
                    maintainer=None # There is no information about it in the response
                )
                versions.append(v)
            except:
                v = Version(
                    idx=version_idx,
                    pkg_idx=pkg_idx,
                    # name=version_info["name"],
                    name=pkg_name,
                    version=version_number,
                    license=None,
                    description=None,
                    homepage=None,  # There is no information about it in the response
                    repository=None,
                    author=None,
                    maintainer=None # There is no information about it in the response
                )
                versions.append(v)

            try:
                for d in version_info["dependencies"]:
                    # Get source ID
                    target_name, target_version = d.text.split()
                    # if the TARGET_ID cannot be found it is a reference to a
                    # Maven package
                    # What to do with them?
                    target_idx = pkg_idx_map.get(target_name, None)
                    source_pkg_idx = pkg_idx_map.get(pkg_name, None)

                    d = Dependency(
                        pkg_idx=source_pkg_idx,
                        source_idx=version_idx,
                        target_idx=target_idx,
                        source_name=pkg_name,
                        target_name=target_name,
                        source_version=version_number,
                        target_version=target_version,
                        kind=Kind.BUILD.name, # This is interpretation, it is not mentioned on the homepage
                    )
                    dependencies.append(d)
            except:
                pass  # Then there are just no dependencies declared

            version_idx += 1
    return versions, dependencies

def scrape_package_version_info(pkg_name, version_number):
    r = requests.get(CLOJARS_VERSION_URL.format(pkg_name=pkg_name, version=version_number), headers=HEADERS)
    if not r.ok:
        print(r.status_code, "VERSION", pkg_name, version_number)
        return None

    soup = BeautifulSoup(r.content, features="html5lib")

    try:
        license = soup.find("ul", {"id": "licenses"}).find("a").text
    except:
        license = ""
    try:
        description = soup.find("p", {"class": "description"}).text
    except:
        description = ""
    try:
        sources_url = soup.find("li", {"class": "col-xs-12 col-sm-3"}).find("a").get("href")
    except:
        sources_url = ""
    try:
        author = soup.find("ul", {"id": "jar-sidebar"}).find("li").find("a").text
    except:
        author = ""
    # try:
    #     date = soup.find("ul", {"id": "jar-sidebar"}).find("span").get("title")
    # except:
    #     date = ""
    # try:
    #     source_version = (
    #         soup.find("ul", {"id": "jar-sidebar"}).find("span", {"class": "commit-url"}).find("a").get("href")
    #     )
    # except:
    #     source_version = ""
    try:
        dependencies = soup.find("ul", {"id": "dependencies"}).find_all("a")
    except:
        dependencies = []

    version_data_with_deps = {
        "version": version_number,
        "license": license,
        "description": description,
        "repository": sources_url,
        "author": author,
        "dependencies": dependencies
        # Clojar specific columns
        # "date": date,
        # "source_version": source_version,
    }

    return version_data_with_deps




# def _collect_dependencies(metadata_dict, pkg_idx_map):
#     deps = []
#     version_idx = 0
#     for idx, (pkg_name, data) in enumerate(metadata_dict.items()):
#         package_versions = []
#         for version, version_info in data.items():
#             # Add version number to list, to check if version appears more than once in package registry
#             if version in package_versions:
#                 continue
#             package_versions.append(version_info["version"])

#             source_pkg_idx = pkg_idx_map.get(pkg_name, None)
#             deps_decl = version_info.get("dependencies", {})
#             dev_deps_decl = version_info.get("dev-dependencies", {})
#             if deps_decl == None:
#                 # sometimes there is an explicit None value stored
#                 deps_decl = {}
#             if dev_deps_decl == None:
#                 dev_deps_decl = {}

#             for dep_name, dep_info in deps_decl.items():
#                 d = Dependency(
#                     pkg_idx=source_pkg_idx,
#                     source_idx=version_idx,
#                     target_idx=pkg_idx_map.get(
#                         dep_name, ""
#                     ),  # There are packages provided as dependencies, which do not exist on the registry, but which are referred to and downloaded from, e.g., Github
#                     source_name=version_info["name"],
#                     target_name=dep_name,
#                     source_version=version_info["version"],
#                     target_version=dep_info.get("tag", "") or dep_info.get("rev", ""),
#                     kind=Kind.BUILD.name,
#                 )
#                 deps.append(d)
#             for dep_name, dep_info in dev_deps_decl.items():
#                 d = Dependency(
#                     pkg_idx=source_pkg_idx,
#                     source_idx=version_idx,
#                     target_idx=pkg_idx_map.get(dep_name, ""),
#                     source_name=version_info["name"],
#                     target_name=dep_name,
#                     source_version=version_info["version"],
#                     target_version=dep_info.get("tag", "") or dep_info.get("rev", ""),
#                     kind=Kind.DEV.name,
#                 )
#                 deps.append(d)
#             version_idx += 1

#     return deps


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
    LOGGER.info("Creating DaSEA versions with dependencies...")

    versions_lst, deps_lst = _collect_versions_with_dependencies(metadata_dict, pkg_idx_map)

    _serialize_data(packages_lst, PKGS_FILE)
    _serialize_data(versions_lst, VERSIONS_FILE)
    _serialize_data(deps_lst, DEPS_FILE)


if __name__ == "__main__":
    mine()
