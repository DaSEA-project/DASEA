import os
import json
import requests
import logging


INDEX_DOC_URL = "https://replicate.npmjs.com/_all_docs"
INDEX_DOC_FILE = "data/tmp/npm/test.json"

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

    # print(proj_json)
    LOGGER.info("Total rows in npm index document: %s", proj_json['total_rows'])
    proj_names = [p["id"] for p in proj_json["rows"]]  # 1_745_109 Sep 29 -> 1_907_047 March 03
    LOGGER.info("Collected packages: %s", len(proj_names))
    return proj_names


def mine():
    print(collect_pkg_names())
    print("EOF")

if __name__ == "__main__":
    mine()
