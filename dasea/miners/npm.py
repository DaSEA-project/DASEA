import os
from struct import pack
import sys
import json
# from tkinter import Pack
import requests
import logging
from datetime import datetime
from dasea.common.datamodel import Package, Version, Dependency, Kind
from dasea.common.utils import _serialize_data



INDEX_DOC_URL = "https://replicate.npmjs.com/_all_docs"
INDEX_DOC_FILE = "data/tmp/npm/projects.json"
FULL_DOCS_URL = "https://replicate.npmjs.com/_all_docs?include_docs=true"
FULL_DOCS_FILE = "data/tmp/npm/full_npm_dump.json"

TODAY = datetime.today().strftime("%m-%d-%Y")
PKGS_FILE = f"data/out/npm/npm_packages_{TODAY}.csv"


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M"
)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

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

def _collect_packages(pkg_name_list):
    pkg_idx_map = {g: idx for idx, g in enumerate(pkg_name_list)}
    packages = []
    for pkg_name, idx in pkg_idx_map.items():
        p = Package(idx, pkg_name, "Npm")
        packages.append(p)
        
    return pkg_idx_map, packages



def mine():
    pkgs = collect_pkg_names()
    download_all_docs()
    LOGGER.info(f"Collected packages {len(pkgs)}")

    pkg_idx_map, packages_lst = _collect_packages(pkgs)

    _serialize_data(packages_lst, PKGS_FILE)

    print("EOF")

if __name__ == "__main__":
    mine()
