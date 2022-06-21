from cmath import log
import shutil
import sys
import os
import logging
import requests
from datetime import datetime
from tqdm import tqdm
from dasea.common.datamodel import Package, Version, Dependency, Kind
from dasea.common.utils import _serialize_data, _serialize_data_rows
from bs4 import BeautifulSoup
import pickle

# Based on the documentation form here:
# https://stackoverflow.com/questions/21419009/json-api-for-pypi-how-to-list-packages

PYPI_REGISTRY = "https://pypi.python.org/simple/"
TMP_REGISTRY_FILE = "./data/tmp/pypi/pkg_names.pkl"

PKG_URL = "https://pypi.python.org/pypi/{pkg_name}/json"
VERSION_URL = "https://pypi.python.org/pypi/{pkg_name}/{version}/json"

# Due to rate limiting and fair use, we have to set such a header
# https://warehouse.pypa.io/api-reference/#rate-limiting
HEADERS = {
    "User-Agent": "DaSEA Research Project (Please don't ban, https://dasea-project.github.io/DASEA)",
    "From": "daseaITU@gmail.com",
}

TODAY = datetime.today().strftime("%m-%d-%Y")
PKGS_FILE = f"data/out/pypi/pypi_packages_{TODAY}.csv"
VERSIONS_FILE = f"data/out/pypi/pypi_versions_{TODAY}.csv"
DEPS_FILE = f"data/out/pypi/pypi_dependencies_{TODAY}.csv"

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M"
)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)


def _collect_pkg_registry():
    # Packages already collected
    if os.path.isfile(TMP_REGISTRY_FILE):
        with open(TMP_REGISTRY_FILE, "rb") as fp:
            pkg_names = pickle.load(fp)
            return pkg_names

    # Download and unpack index file
    r = requests.get(PYPI_REGISTRY)
    soup = BeautifulSoup(r.content, features="lxml")
    pkg_names = [link.text for link in soup.findAll("a")]

    # Save to file
    with open(TMP_REGISTRY_FILE, "wb") as fp:
        pickle.dump(pkg_names, fp)

    return pkg_names

# Write chunks to csv, and empty array to save memory
def _write_chunk_to_csv(array, file):
    _serialize_data_rows(array, file)


def _collect_packages(metadata_dict):
    pkg_idx_map = {}
    packages = []
    for idx, pkg_name in enumerate(metadata_dict):
        # PyPI is case insensitive: https://stackoverflow.com/questions/26503509/is-pypi-case-sensitive
        name = pkg_name.lower()
        p = Package(idx, name, "PyPi")
        packages.append(p)
        pkg_idx_map[name] = idx

    return pkg_idx_map, packages


def _collect_versions_with_dependencies(metadata_dict, pkg_idx_map):
    version_idx = 0

    for pkg_name in tqdm(metadata_dict):
        versions = []
        dependencies = []
        # Request the package versions data
        pkg_url = PKG_URL.format(pkg_name=pkg_name)

        r = requests.get(pkg_url, headers=HEADERS)
        if not r.ok:
            LOGGER.error(r.status_code, r, "PACKAGE", pkg_name)
            continue
        pkg_doc = r.json()

        version_numbers = list(pkg_doc["releases"].keys())

        for version_number in version_numbers:
                # Request the specific version data
                version_url = VERSION_URL.format(pkg_name=pkg_name, version=version_number)
                req = requests.get(version_url, headers=HEADERS)
                if not req.ok:
                    LOGGER.error(r.status_code, r, "VERSION", pkg_name, version_number)
                    continue

                # Parse general information about the version
                # Check, e.g., https://pypi.org/pypi/Flask/1.0.4/json for more
                # information on possible/desired fields
                version_info = req.json()["info"]
                pkg_idx = pkg_idx_map.get(pkg_name, None)
                print("VERSION ID", version_idx)
                v = Version(
                        idx=version_idx,
                        pkg_idx=pkg_idx,
                        name=pkg_name,
                        version=version_number,
                        # licenses sometimes is an array, sometimes a string
                        license=version_info["license"],
                        description=version_info["summary"], # Use summary instead of description, since description is in various formats
                        homepage=version_info["home_page"],
                        repository= version_info["project_urls"].get("Code") if version_info["project_urls"] else None,
                        author=version_info["author"],
                        maintainer=version_info["maintainer"]
                    )
                versions.append(v)

                # Parse dependencies
                deps = req.json()["info"]["requires_dist"]
                if not deps:
                    deps = []

                for d in deps:
                    (
                        target_name,
                        version_constraint,
                        constraint,
                    ) = _parse_version_deps(d)

                    try:
                        # PyPI is case insensitive: https://stackoverflow.com/questions/26503509/is-pypi-case-sensitive
                        target_id = pkg_idx_map.get(target_name.lower(), None)
                    except KeyError:
                        # Dep declarations may contain optional values:
                        # https://stackoverflow.com/questions/46775346/what-do-square-brackets-mean-in-pip-install
                        if target_name.lower().endswith("]"):
                            target_id = pkg_idx_map.get(target_name.lower().split("[")[0], None)

                    d = Dependency(
                        pkg_idx=pkg_idx,
                        source_idx=version_idx,
                        target_idx=target_id,
                        source_name=pkg_name,
                        target_name=target_name,
                        source_version=version_number,
                        target_version=version_constraint,
                        kind=Kind.RUN.name, # TODO: Check if this is correct
                    )
                    dependencies.append(d)
                version_idx += 1
        ## Write to file after each version
        if versions:
            _write_chunk_to_csv(versions, VERSIONS_FILE)
        if dependencies:
            _write_chunk_to_csv(dependencies, DEPS_FILE)

def _parse_version_deps(dependency):

    dep = dependency.split(";")
    if len(dep) == 1:
        target = dep[0]
        constraint = ""
    elif len(dep) == 2:
        target, constraint = dep
        target = target.strip()
        constraint = constraint.strip()

    t = target.split("(")
    if len(t) == 1:
        target_name = t[0]
        version_constraint = ""
    elif len(t) == 2:
        target_name, version_constraint = t
        version_constraint = version_constraint.replace(")", "")
        target_name = target_name.strip()
        version_constraint = version_constraint.strip()

    return (target_name, version_constraint, constraint)

def mine():
    LOGGER.info("Collecting PyPi registry")
    try:
        metadata_dict = _collect_pkg_registry()
    except IOError as e:
        LOGGER.error(str(e))
        sys.exit(1)

    LOGGER.info("Creating DaSEA packages...")
    pkg_idx_map, packages_lst = _collect_packages(metadata_dict)
    _serialize_data(packages_lst, PKGS_FILE)

    LOGGER.info("Creating DaSEA versions with dependencies...")
    _collect_versions_with_dependencies(metadata_dict, pkg_idx_map)

    # delete tmp files
    shutil.rmtree(TMP_REGISTRY_FILE, ignore_errors=True)

if __name__ == "__main__":
    mine()