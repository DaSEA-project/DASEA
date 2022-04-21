from cmath import log
import sys
import logging
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from tqdm import tqdm
from dasea.common.datamodel import Package, Version, Dependency, Kind
from dasea.common.utils import _serialize_data
import re


# Based on:
# https://luarocks.org/modules

LUAROCKS_REGISTRY = "https://luarocks.org/modules"
LUAROCKS_PACKAGE_URL =  "https://luarocks.org{pkg_url}"
LUAROCKS_VERSION_URL = "https://luarocks.org{pkg_url}-{version}.rockspec"

HEADERS = {
    "User-Agent": "DaSEA Research Project (Please don't ban, https://dasea.org)",
    "From": "daseaITU@gmail.com",
}

TODAY = datetime.today().strftime("%m-%d-%Y")
PKGS_FILE = f"data/out/luarocks/luarocks_packages_{TODAY}.csv"
VERSIONS_FILE = f"data/out/luarocks/luarocks_versions_{TODAY}.csv"
DEPS_FILE = f"data/out/luarocks/luarocks_dependencies_{TODAY}.csv"

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M"
)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)


def _collect_pkg_registry():
    LOGGER.info("Collecting LuaRocks registry...")
    packageNames = []

    r = requests.get(LUAROCKS_REGISTRY, headers=HEADERS)
    if not r.ok:
        raise IOError("Cannot download LuaRocks registry.")

    soup = BeautifulSoup(r.content, features="html5lib")

    try:
        paginationRange = soup.find("span", {"class": "pager_label"}).text
        last_page = paginationRange.split("of ")[1]
    except AttributeError:
        last_page = 1

    for page in tqdm(range(1, int(last_page))):
        r = requests.get(LUAROCKS_REGISTRY + f"?page={page}", headers=HEADERS)
        if not r.ok:
            raise IOError("Cannot download LuaRocks registry.")

        soup = BeautifulSoup(r.content, features="html5lib")

        for pkg in soup.find_all("a", {"class": "title"}):
            packageNames.append({
                "name": pkg.text,
                "url": pkg.get("href")
            })

    return packageNames

def _collect_packages(metadata_dict):
    pkg_idx_map = {}
    packages = []
    for idx, pkg in enumerate(metadata_dict):
        pkg_name = pkg['name']
        p = Package(idx, pkg_name, "LuaRocks")
        packages.append(p)
        pkg_idx_map[pkg_name] = idx

    return pkg_idx_map, packages


def _collect_versions_with_dependencies(metadata_dict, pkg_idx_map):
    versions = []
    dependencies = []
    version_idx = 0

    for pckg in tqdm(metadata_dict):
        pkg_name = pckg['name']
        pkg_url = pckg['url']

        # Get the package versions
        url = LUAROCKS_PACKAGE_URL.format(pkg_url=pkg_url)
        r = requests.get(url, headers=HEADERS)
        if not r.ok:
            print(r.status_code, "PKG", pkg_name)
            continue

        package_versions = []
        soup = BeautifulSoup(r.content, features="html5lib")
        try:
          versions_containers = soup.find_all("div", {"class": "version_row"})

          for div in versions_containers:
            version = div.find('a').text
            package_versions.append(version)
        except AttributeError:
          pass

        for version_number in package_versions:
            pkg_idx = pkg_idx_map.get(pkg_name, None)

            # Scrape the package version data
            version_info = scrape_package_version_info(pkg_name,pkg_url, version_number)


            v = Version(
                idx=version_idx,
                pkg_idx=pkg_idx,
                name=pkg_name,
                version=version_number,
                license=version_info["license"],
                description=version_info["description"],
                homepage=version_info["homepage"],
                repository=version_info["repository"],
                author=version_info["author"],
                maintainer=None # There is no information
            )
            versions.append(v)

            try:
                for target_name in version_info["dependencies"]:
                    source_pkg_idx = pkg_idx_map.get(pkg_name, None)
                    target_idx = pkg_idx_map.get(target_name, ""),

                    d = Dependency(
                        pkg_idx=source_pkg_idx,
                        source_idx=version_idx,
                        target_idx=target_idx,
                        source_name=pkg_name,
                        target_name= target_name,# includes the target_version as well, but hard to split it
                        source_version=version_number,
                        target_version="",
                        kind=Kind.BUILD.name, # This is interpretation, it is not mentioned on the homepage
                    )
                    dependencies.append(d)
            except:
                pass  # Then there are just no dependencies declared

            version_idx += 1
    return versions, dependencies

def scrape_package_version_info(pkg_name, pkg_url, version_number):
    pkg_url = pkg_url.replace("modules", "manifests")
    version_url = LUAROCKS_VERSION_URL.format(pkg_url=pkg_url, version=version_number)

    r = requests.get(version_url, headers=HEADERS)
    if not r.ok:
        print(r.status_code, "VERSION", pkg_name, version_number)
        return None
    body = r.text

    try:
      author = pkg_url.split('/')[2]
    except:
      author = ""
    try:
      source_url =  re.search('url = "(.*)"', body).group(1)
    except:
      source_url = ""

    try:
      description = re.search('summary = "(.*)"', body).group(1)
    except:
      description = ""

    try:
      license =  re.search('license = "(.*)"', body).group(1)
    except:
      license = ""

    try:
      homepage =  re.search('homepage = "(.*)"', body).group(1)
    except:
      homepage = ""

    try:
      dependencies =  re.search('dependencies = (.*)}', body).group(1).replace( '{', '').replace( '"', '').split(",")
    except:
      dependencies = []

    version_data_with_deps = {
        "version": version_number,
        "license": license,
        "description": description,
        "repository": source_url,
        "author": author,
        "dependencies": dependencies,
        "homepage": homepage
    }

    return version_data_with_deps

def mine():
    try:
        metadata_dict = _collect_pkg_registry()
    except IOError as e:
        LOGGER.error(str(e))
        sys.exit(1)

    LOGGER.info("Creating DaSEA packages...")
    pkg_idx_map, packages_lst = _collect_packages(metadata_dict)
    LOGGER.info("Creating DaSEA versions with dependencies...")

    versions_lst, deps_lst = _collect_versions_with_dependencies(metadata_dict, pkg_idx_map)

    _serialize_data(packages_lst, PKGS_FILE)
    _serialize_data(versions_lst, VERSIONS_FILE)
    _serialize_data(deps_lst, DEPS_FILE)


if __name__ == "__main__":
    mine()
