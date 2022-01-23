import os
import csv
import json
import logging
import requests
import subprocess
from datetime import datetime
from dataclasses import dataclass
from dasea.datamodel import Package, Version, Dependency, Kind


# Based on the documentation form here:
CRATES_URL = "https://crates.io/api/v1/crates?page={page_idx}&per_page=100"
CRATE_URL = "https://crates.io/api/v1/crates/{name}"
VERSION_URL = "https://crates.io/api/v1/crates/{name}/{version}/dependencies"
INDEX_FILE = "data/tmp/cargo/crates_index.json"


TODAY = datetime.today().strftime("%m-%d-%Y")
PKGS_FILE = f"data/out/cargo/cargo_packages_{TODAY}.csv"
VERSIONS_FILE = f"data/out/cargo/cargo_versions_{TODAY}.csv"
DEPS_FILE = f"data/out/cargo/cargo_dependencies_{TODAY}.csv"
DONE_FILE = "data/tmp/cargo/done"


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
            LOGGER.info(page_idx)
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


def get_remote_data(url, pkg_name, version_num=None):
    if version_num:
        url = url.format(name=pkg_name, version=version_num)
    else:
        url = url.format(name=pkg_name)
    while True:
        # Or better go for a Retry object???
        # https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests
        try:
            r = requests.get(url)
            break
        except requests.exceptions.ConnectionError:
            LOGGER.info("Connection refused. I will try again in 5 secs...")
            sleep(5)
            continue
        except requests.exceptions.ConnectionResetError:
            LOGGER.info("Connection refused. I will try again in 5 secs...")
            sleep(5)
            continue
        except Exception as e:
            LOGGER.error(e)
            sleep(5)
            continue

    if not r.ok:
        if version_num:
            LOGGER.warning(f"{r.status_code} VERSION {pkg_name} {version_num}")
        else:
            LOGGER.warning(f"{r.status_code} PKG {pkg_name}")

    return r


def iterative_data_collection(pkgs_lst):
    dep_kind_map = {
        "normal": Kind.NORMAL.name,
        "dev": Kind.DEV.name,
        "build": Kind.BUILD.name,
    }
    pkg_idx_map = {p["name"]: idx for idx, p in enumerate(pkgs_lst)}

    version_idx = 0

    with open(PKGS_FILE, "a") as fp, open(VERSIONS_FILE, "a") as fv, open(DEPS_FILE, "a") as fd:
        pkgs_csv_writer = csv.writer(fp)
        versions_csv_writer = csv.writer(fv)
        deps_csv_writer = csv.writer(fd)

        pkgs_csv_writer.writerow(CargoPackage(None, None, None, None, None, None).__dict__.keys())
        versions_csv_writer.writerow(
            CargoVersion(
                None, None, None, None, None, None, None, None, None, None, None, None, None, None
            ).__dict__.keys()
        )
        deps_csv_writer.writerow(
            CargoDependency(None, None, None, None, None, None, None, None, None, None, None).__dict__.keys()
        )

        for pkg_idx, pkg_info in enumerate(pkgs_lst):
            pkg_name = pkg_info["name"]

            pkg = CargoPackage(
                idx=pkg_idx,
                name=pkg_name,
                pkgman="Cargo",
                description=pkg_info["description"],
                homepage=pkg_info["homepage"],
                repository=pkg_info["repository"],
            )
            pkgs_csv_writer.writerow(pkg.__dict__.values())
            fp.flush()
            os.fsync(fp)

            r = get_remote_data(CRATE_URL, pkg_name)
            for version_info in r.json()["versions"]:
                crate = {}
                if type(version_info["crate"]) == dict:
                    crate = version_info["crate"]
                published_by = {}
                if version_info["published_by"]:
                    published_by = version_info["published_by"]
                version_num = version_info["num"]
                v = CargoVersion(
                    idx=version_idx,
                    pkg_idx=pkg_idx_map.get(pkg_name, None),
                    name=pkg_name,
                    version=version_num,
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

                versions_csv_writer.writerow(v.__dict__.values())
                fp.flush()
                os.fsync(fv)
                version_idx += 1

                r = get_remote_data(VERSION_URL, pkg_name, version_num)
                for dep_info in r.json().get("dependencies", []):
                    d = CargoDependency(
                        pkg_idx=pkg_idx_map.get(pkg_name, None),
                        source_idx=version_idx,
                        target_idx=pkg_idx_map[dep_info["crate_id"]],
                        source_name=pkg_name,
                        target_name=dep_info["crate_id"],
                        source_version=version_idx,
                        target_version=dep_info["req"],
                        kind=dep_kind_map.get(dep_info["kind"], None),
                        kind_str=dep_info["kind"],
                        optional=dep_info["optional"],
                        target=dep_info["target"],
                    )
                    deps_csv_writer.writerow(d.__dict__.values())
                    fp.flush()
                    os.fsync(fd)


def mine():
    pkg_metadata_dict = _collect_pkg_metadata()
    pkgs_lst = _parse_crates(pkg_metadata_dict)
    LOGGER.info(f"There should be {len(pkgs_lst)} pkgs in the end.")

    iterative_data_collection(pkgs_lst)

    # Poor mans way to communicate to remote host that mining is complete
    cmd = "hostname -I"
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    host_ip = r.stdout.split()[0]
    with open(DONE_FILE, "w") as fp:
        fp.write(f"http://{host_ip}:8080/{PKGS_FILE}\n")
        fp.write(f"http://{host_ip}:8080/{VERSIONS_FILE}\n")
        fp.write(f"http://{host_ip}:8080/{DEPS_FILE}")

    cmd = "nohup python -m http.server 8080 --directory /vagrant/data/out/cargo/ &"
    subprocess.run(cmd, shell=True)
    # os.remove(INDEX_FILE)


if __name__ == "__main__":
    mine()
