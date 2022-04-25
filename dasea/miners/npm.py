import os
import sys
import json
import ijson  # see https://pypi.org/project/ijson
import logging
import requests
from datetime import datetime
from dasea.common.datamodel import Package, Version, Dependency
from dasea.common.utils import _serialize_data_rows


INDEX_DOC_URL = "https://replicate.npmjs.com/_all_docs"
INDEX_DOC_FILE = "./data/tmp/npm/projects.json"
FULL_DOCS_URL = "https://replicate.npmjs.com/_all_docs?include_docs=true"
FULL_DOCS_FILE = "./data/tmp/npm/full_npm_dump.json"

TODAY = datetime.today().strftime("%m-%d-%Y")
PKGS_FILE = f"data/out/npm/npm_packages_{TODAY}.csv"
VERSIONS_FILE = f"data/out/npm/npm_versions_{TODAY}.csv"
DEPENDENCIES_FILE = f"data/out/npm/npm_dependencies_{TODAY}.csv"



PKG_IDX_MAP = {}

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M"
)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

def _extract_name_details(doc):
    if doc == None:
        name_details = ""
    elif type(doc) == list:
        name_details = []
        for d in doc:
            if type(d) == dict:
                name_details.append((d.get("name", ""), d.get("email", "")))
            elif type(d) == str:
                name_details.append(d)
    elif type(doc) == dict:
        name_details = (doc.get("name", ""), doc.get("email", ""))
    elif type(doc) == str:
        name_details = doc

    name_details_str = str(name_details)
    return name_details_str

def collect_pkg_names():
    if os.path.isfile(INDEX_DOC_FILE):
        LOGGER.info("Reusing earlier npm index document...")
        with open(INDEX_DOC_FILE) as fp:
            proj_json = json.load(fp)
    else:
        # Download NPM index document takes +2 hours
        LOGGER.info("Downloading npm index document...")
        r = requests.get(INDEX_DOC_URL)
        proj_json = r.json()
        with open(INDEX_DOC_FILE, "w") as fp:
            json.dump(proj_json, fp)

    LOGGER.info(f"Total rows in npm index document {proj_json['total_rows']}")
    proj_names = [p["id"] for p in proj_json["rows"]]  # 1_745_109 Sep 29 -> 1_907_047 March 03
    return proj_names


def download_all_docs():
    """Important: Downloading a data dump from NPM takes quite some time
    and space (at least 70GB of harddisk space)
    The advantage of downloading the dataset is that one does not have to send
    million requests to the NPM API, which would take even longer...
    """

    # 60G May 19 2021 69G Sep 30 2021 (10+ hours)
    if os.path.isfile(FULL_DOCS_FILE):
        LOGGER.info("Reusing earlier database dump...")
        return FULL_DOCS_FILE
    completely_downloaded = False
    while not completely_downloaded:
        LOGGER.info("Download NPM data dump, this may take 10+ hours...")

        if os.path.isfile(FULL_DOCS_FILE):
            os.remove(FULL_DOCS_FILE)
        try:
            LOGGER.info("Downloading database dump...")
            start_ts = datetime.now()
            with requests.get(FULL_DOCS_URL, stream=True) as r:
                r.raise_for_status()
                with open(FULL_DOCS_FILE, "wb") as fp:
                    for chunk in r.iter_content(8192, decode_unicode=False):
                        fp.write(chunk)
            completely_downloaded = True
        except Exception as e:
            LOGGER.error(f"Error when downloading database dump '{e}' on line {sys.exc_info()[-1].tb_lineno}")

    time_spent = datetime.now() - start_ts
    LOGGER.info(f"It took {str(time_spent)} to download the data dump...")
    return FULL_DOCS_FILE


def mine():
    pkgs = collect_pkg_names()
    LOGGER.info(f"Downloaded packages {len(pkgs)}")
    download_all_docs()
    LOGGER.info(f"Collected packages {len(pkgs)}")
    PKG_IDX = VERSION_IDX = 0
    CHUNK_SIZE = 3493;
    CDEP = 0
    CDEP_SKIP = 0
    CDEP_ERRORS = 0

    # populate the project index map
    PKG_IDX_MAP = {g: idx for idx, g in enumerate(pkgs)}
    packages_lst = []
    versions_lst = []
    dependencies_lst = []

    with open(FULL_DOCS_FILE, "r") as fi:
        pkg_json_objects = ijson.items(fi, "rows.item")

        for pkg_json_object in pkg_json_objects:
            pkg_doc = pkg_json_object["doc"]
            if not "name" in pkg_doc.keys():
                # A package without a name is likely broken, e.g., bb-mobile
                # https://www.npmjs.com/package/bb-mobile
                # so we skip it completely
                # Shall I do some sanety checking to avoid ??? in dependencies later?
                continue
            pkg_name = pkg_doc["name"]
            p = Package(PKG_IDX, pkg_name, "npm")
            packages_lst.append(p)

            # Write chunks to csv, and empty array to save memory
            if len(packages_lst) >= CHUNK_SIZE:
                _serialize_data_rows(packages_lst, PKGS_FILE)
                packages_lst = []

            for version_number, v_info in pkg_doc.get("versions", {}).items():
                repository = v_info.get("repository", {})

                if type(repository) == dict:
                    repo_url = repository.get("url", "")
                elif type(repo_url) == str:
                    repo_url = repository

                v = Version(
                    idx = VERSION_IDX,
                    pkg_idx = PKG_IDX,
                    name = pkg_name,
                    version = version_number,
                    license = v_info.get("license", ""),
                    description = v_info.get("description", ""),
                    homepage = v_info.get("homepage", ""),
                    repository = repo_url,
                    author = _extract_name_details(v_info.get("author", "")),
                    maintainer = _extract_name_details(v_info.get("maintainer", ""))
                )

                versions_lst.append(v)

                if len(versions_lst) >= CHUNK_SIZE:
                    _serialize_data_rows(versions_lst, VERSIONS_FILE)
                    versions_lst = []

                dep_kinds = {
                            "dependencies": "runtime",
                            "devDependencies": "dev",
                            "optionalDependencies": "optional",
                        }

                for dep_kind in dep_kinds.keys():
                    dep_docs = v_info.get(dep_kind, {})
                    if not dep_docs:
                        # Every now and then dependencies are set to `None`
                        dep_docs = {}
                        CDEP_SKIP += 1

                    try:
                        for target_name, v_constraint in dep_docs.items():
                            d = Dependency(
                                pkg_idx = PKG_IDX,
                                source_idx = VERSION_IDX,
                                target_idx = PKG_IDX_MAP.get(target_name, None),
                                source_name = pkg_name,
                                target_name = target_name,
                                source_version = version_number,
                                target_version = v_constraint,
                                kind = dep_kinds[dep_kind]
                                )
                            dependencies_lst.append(d)

                            if len(dependencies_lst) >= CHUNK_SIZE:
                                _serialize_data_rows(dependencies_lst, DEPENDENCIES_FILE)
                                CDEP += len(dependencies_lst)
                                dependencies_lst = []
                    except:
                        CDEP_ERRORS += 1
                        LOGGER.info(f"Package '{pkg_name}' version '{version_number}' does not provide dependency information")
                        pass

                VERSION_IDX += 1
            PKG_IDX += 1

            # # Break for tests
            # if PKG_IDX >= 100000:
            #     break

    # Write remaining chunks to CSV
    if packages_lst:
        print(f"Remaining package chunk is {len(packages_lst)}")
        _serialize_data_rows(packages_lst, PKGS_FILE)
    if versions_lst:
        print(f"Remaining versions chunk is {len(versions_lst)}")
        _serialize_data_rows(versions_lst, VERSIONS_FILE)
    if dependencies_lst:
        CDEP += len(dependencies_lst)
        print(f"Remaining dependencies chunk is {len(dependencies_lst)}")
        _serialize_data_rows(dependencies_lst, DEPENDENCIES_FILE)

    print(f"Total packages: {PKG_IDX}")
    print(f"Total versions: {VERSION_IDX}")
    print(f"Total dependencies: {CDEP}")
    print(f"Skipped dependencies: {CDEP_SKIP}")
    print(f"Error dependencies: {CDEP_ERRORS}")



if __name__ == "__main__":
    mine()
