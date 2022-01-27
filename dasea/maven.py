"""
This program is expensive to run! Identification of all POM files from the 
remote server takes 1.5 to two weeks. There are more than 1.6 millions of these.
The POM identification process writes also quite a bit to disc! On every step, 
i.e., for parsing of each website, all links that remain to be mined are newly 
stored to the REMAINING_URLS_FILE. The reason for that is to be able to continue the process in case of a failure.

On every sent request REQUESTS_COUNTER_FILE is overwritten with a new value.

This program drew inspiration from https://github.com/yegor256/scrape-maven-central/blob/master/scrape.rb

TODO: Keep the POM files around so that in future only a "delta" has to be mined
and downloaded. That requires a bit of a rewrite of the logic under `get_pom_links()` and `download_pom(path)`.

WARNING: Before running this program against the Maven central repository, 
contact the team since it is not in accordance with their terms of service 
https://repo1.maven.org/terms.html.

Since this program is running for more than a week it is best started with:
$ nohup dasea mine maven >> data/tmp/maven/maven.log 2>&1 &
"""
import os
import csv
import sys
import lxml
import signal
import pathlib
import sqlite3
import logging
import requests
from glob import glob
from time import sleep
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from dataclasses import dataclass
from dasea.datamodel import Package, Version, Dependency, Kind
from dasea.utils import _serialize_data

# 22773
# TODO: Switch to:
# https://maven.apache.org/repository/central-index.html
# https://github.com/borisbaldassari/maven-index-exporter
# https://stackoverflow.com/questions/5776519/how-to-parse-unzip-unpack-maven-repository-indexes-generated-by-nexus


# BASE_URL = "https://repo1.maven.org/maven2/"
BASE_URL = "https://repo.maven.apache.org/maven2/"  # Apache mirror

MAVEN_MINE_DIR = "data/tmp/maven"
PKGS_FILE = "data/out/maven/packages.csv"
VERSIONS_FILE = "data/out/maven/versions.csv"
DEPS_FILE = "data/out/maven/dependencies.csv"

STATE_DB = "data/tmp/maven/pom_mining_state.db"
if not Path(STATE_DB).is_file():
    # Initialize the database in case it does not exist yet
    CONNECTION = sqlite3.connect(STATE_DB)
    cursor = CONNECTION.cursor()
    cursor.execute("CREATE TABLE pom_urls (url TEXT UNIQUE)")
    # Since SQLite dos not have a BOOLEAN type, 0 in seen are False and 1 are True
    cursor.execute("CREATE TABLE remote_links (url TEXT UNIQUE, seen INTEGER)")
    cursor.execute("CREATE TABLE request_count (count INTEGER)")
    cursor.execute("INSERT INTO request_count VALUES (0)")
    CONNECTION.commit()
else:
    CONNECTION = sqlite3.connect(STATE_DB)

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M"
)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

START_TS = datetime.now()
POM_URLS_FILE = "/vagrant/data/tmp/maven/pom_urls.txt"


def _inc_req_count():
    cursor = CONNECTION.cursor()
    rows = cursor.execute("SELECT count FROM request_count LIMIT 1").fetchall()
    req_count = rows[0][0] + 1
    cursor.execute("UPDATE request_count SET count = ?", (req_count,))
    cursor.close()
    CONNECTION.commit()
    if req_count % 1000 == 0:
        t_diff = datetime.now() - START_TS
        print(f"{req_count} requests took {t_diff}", flush=True)


def _store_pom_link(pom_url):
    cursor = CONNECTION.cursor()
    cursor.execute("INSERT OR IGNORE INTO pom_urls VALUES (?)", (pom_url,))
    cursor.close()
    CONNECTION.commit()


def _store_links_state(links):
    cursor = CONNECTION.cursor()
    # TODO: Remove this loop by inserting the values via the query
    for link in links:
        cursor.execute("INSERT OR IGNORE INTO remote_links VALUES (?, ?)", (link, 0))
    cursor.close()
    CONNECTION.commit()


def _pop_next_link():
    cursor = CONNECTION.cursor()
    rows = cursor.execute("SELECT url FROM remote_links WHERE seen = 0 LIMIT 1").fetchall()
    cursor.close()
    if rows:
        return rows[0][0]
    else:
        return None


def _toggle_seen(link):
    cursor = CONNECTION.cursor()
    cursor.execute("UPDATE remote_links SET seen = ? WHERE url = ?", (1, link))
    cursor.close()
    CONNECTION.commit()


def _seen_any_links():
    cursor = CONNECTION.cursor()
    rows = cursor.execute("SELECT COUNT (*) FROM remote_links").fetchall()
    cursor.close()
    return rows[0][0]


def contains_link_to_pom(links):
    """Extract links to POM files from a collection of links.

    Args:
        links (collection): A collection of URL strings

    Returns:
        str: In case a link to a POM file is present on a Maven repository page,
             then a string representing its URL is returned.
             In case a page from a Maven repository does only contain links to
             subdirectories, other meta-data, etc. but no link to a POM file,
             then this function returns always an empty string.
    """

    for l in links:
        if os.path.splitext(l)[1] == ".pom":
            return l
    return ""


def get_links_from_page(path):
    """"""
    url = BASE_URL + path

    while True:
        # Or better go for a Retry object???
        # https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests
        try:
            r = requests.get(url)
            _inc_req_count()
            break
        except requests.exceptions.ConnectionError:
            LOGGER.info("Connection refused. I will try again in 5 secs...")
            sleep(5)
            continue

    # r = requests.get(url)
    # _inc_req_count()
    if r.ok:
        soup = BeautifulSoup(r.content, features="html5lib")
        links = [path + a.get("href") for a in soup.find_all("a") if not a.get("href") == "../"]
        return links
    elif r.status_code == 404:
        LOGGER.error(f"Calling {url} returned {r.status_code}")
        return []
    else:
        LOGGER.error(f"Calling {url} returned {r.status_code}")
        sys.exit(1)
        return []


def get_pom_links():
    """Function to extract all links to POM files from the remote directory tree"""
    # The first step of link extraction collects all top-level directory links
    # from the main page at BASE_URL
    # A result may look like in the following
    # links = set(['excalibur-pool/'])  #, 'jersey/', 'commons-util/', 'se/', 'classworlds/'])
    path = ""
    if not _seen_any_links():
        # Get original links from start page
        links = [l for l in get_links_from_page(path) if l.endswith("/")]
        _store_links_state(links)

    while True:
        l = _pop_next_link()
        if not l:
            break

        # print(l)
        links_from_page = get_links_from_page(l)
        link_to_pom = contains_link_to_pom(links_from_page)

        if link_to_pom:
            _store_pom_link(link_to_pom)
        else:
            # Filter metadata file links and checksums of these
            links_from_page = [l for l in links_from_page if l.endswith("/")]
            _store_links_state(links_from_page)
        _toggle_seen(l)


def pom_files():
    with open(POM_URLS_FILE) as fp:
        links = fp.readlines()
    links = [l.strip() for l in links]
    return links


def download_poms():
    for p in pom_files():
        download_pom(p)


def download_pom(path):
    out_path = Path(MAVEN_MINE_DIR, Path(path).parent)
    out_file = Path(MAVEN_MINE_DIR, path)
    if not out_path.is_dir():
        pathlib.Path(out_path).mkdir(parents=True, exist_ok=True)

    if not out_file.is_file():
        url = BASE_URL + str(path)
        r = requests.get(url)
        if r.ok:
            with open(out_file, "wb") as fp:
                fp.write(r.content)
        else:
            LOGGER.error(f"Downloading {url} returned {r.status_code}")
            sys.exit(1)


def _parse_dependency(dep_xml):
    group_id = dep_xml.find("groupid").text  # soup.find("groupId").text
    artifactid_id = dep_xml.find("artifactid").text  # soup.find("groupId").text
    version = dep_xml.find("version").text
    scope = dep_xml.find("scope")
    if scope:
        scope = scope.text
    else:
        scope = ""
    dep_type = soup.find("type")
    if dep_type:
        dep_type = dep_type.text
    else:
        dep_type = "jar"
    optional = soup.find("optional")
    if optional:
        optional = True
    else:
        optional = False

    # What about exclusions?

    return group_id, artifactid_id, version


def _parse_dependency(dep_xml):
    return None


def parse_pom(pom_path):
    # Read this for parsing the XML file
    # https://maven.apache.org/pom.html
    with open(pom_path) as fp:
        soup = BeautifulSoup(fp, "lxml")

        # Does the LXML parser map all cases to lower case?
        group_id = soup.find("groupid").text  # soup.find("groupId").text
        artifactid_id = soup.find("artifactid").text  # soup.find("groupId").text
        version = soup.find("version").text

        packaging = soup.find("packaging")
        if packaging:
            packaging = packaging.text
        else:
            packaging = "jar"

        # TODO: what to do about inheritance, superpackages, etc.?
        deps = soup.find_all("dependency")
        for dep_xml in deps:
            pass
            # print(_parse_dependency(dep_xml))
    return {
        "group_id": group_id,
        "artifactid_id": artifactid_id,
        "version": version,
        "packaging": packaging,
    }


def _collect_packages(pkg_lst):
    pkg_idx_map = {d["Name"]: idx for idx, d in enumerate(pkg_lst)}
    packages = []
    for pkg_name, idx in pkg_idx_map.items():
        p = Package(idx, pkg_name, "Maven", "JVM")
        packages.append(p)

    return pkg_idx_map, packages


def signal_handler(signal, frame):
    CONNECTION.commit()
    CONNECTION.close()
    LOGGER.info("Somebody killed me...")
    sys.exit(0)


def mine():
    # try:
    #     paths = get_pom_links()
    #     CONNECTION.commit()
    #     CONNECTION.close()
    # except Exception as e:
    #     LOGGER.error(e)
    #     CONNECTION.commit()
    #     CONNECTION.close()
    for path in paths:
        download_pom(path)

    # pkg_config_files = [Path(MAVEN_MINE_DIR, p) for p in pom_files]

    # # Check if this fits in RAM with all POM files
    # metadata_lst = [parse_pom(p) for p in pkg_config_files]
    # pkg_names = [f'{m["group_id"]}:{m["artifactid_id"]}' for m in metadata_lst]

    # pkg_idx_map, packages_lst = _collect_packages(metadata_lst)
    # _serialize_data(packages_lst, PKGS_FILE)
    # del packages_lst
    # versions_lst = _collect_versions(metadata_lst, pkg_idx_map)
    # deps_lst = _collect_dependencies(metadata_lst, pkg_idx_map)

    # _serialize_data(versions_lst, VERSIONS_FILE)
    # _serialize_data(deps_lst, DEPS_FILE)

    # for path in paths:
    #     parse_pom(path)


signal.signal(signal.SIGINT, signal_handler)
if __name__ == "__main__":
    mine()
