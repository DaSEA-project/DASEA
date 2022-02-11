import os
import shutil
import logging
import tarfile
import requests
import pandas as pd
from glob import glob
from pathlib import Path
from datetime import datetime
from core.common.datamodel import Kind


TODAY = datetime.today().strftime("%m-%d-%Y")
PKGS_FILE = f"data/out/cargo/cargo_packages_{TODAY}.csv"
VERSIONS_FILE = f"data/out/cargo/cargo_versions_{TODAY}.csv"
DEPS_FILE = f"data/out/cargo/cargo_dependencies_{TODAY}.csv"
DONE_FILE = "data/out/cargo/done"

CARGO_DB_DUMP_URL = "https://static.crates.io/db-dump.tar.gz"
TMP_DIR = "data/tmp/cargo/"


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M"
)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)


def _collect_packages(crates_csv):
    df = pd.read_csv(crates_csv)
    df.fillna("", inplace=True)
    df["pkgman"] = "Cargo"

    df = df[["id", "name", "pkgman", "description", "homepage", "repository"]]
    df.to_csv(PKGS_FILE, index=False)


def _collect_versions(crates_csv, versions_csv, users_csv):
    cdf = pd.read_csv(crates_csv)
    cdf = cdf[["id", "name", "description", "homepage", "repository"]]
    cdf.fillna("", inplace=True)
    cdf.rename(columns={"id": "pkg_idx"}, inplace=True)

    vdf = pd.read_csv(versions_csv)
    vdf = vdf[
        [
            "crate_id",
            "id",
            "license",
            "num",
            "published_by",
            "created_at",
            "updated_at",
            "downloads",
        ]
    ]
    vdf.rename(columns={"crate_id": "pkg_idx"}, inplace=True)
    vdf = pd.merge(cdf, vdf, how="inner", on="pkg_idx")
    vdf.rename(
        columns={
            "id": "idx",
            "downloads": "no_downloads",
            "published_by": "owner_id",
            "num": "version",
        },
        inplace=True,
    )

    udf = pd.read_csv(users_csv)
    udf.rename(
        columns={
            "id": "owner_id",
            "gh_login": "author_github_nick",
            "name": "author",
        },
        inplace=True,
    )
    vdf = pd.merge(udf, vdf, how="right", on="owner_id")

    vdf["maintainer"] = ""

    vdf = vdf[
        [
            "idx",
            "pkg_idx",
            "name",
            "version",
            "license",
            "description",
            "homepage",
            "repository",
            "author",
            "maintainer",
            "author_github_nick",
            "created_at",
            "updated_at",
            "no_downloads",
        ]
    ]
    vdf.fillna("", inplace=True)
    vdf.to_csv(VERSIONS_FILE, index=False)


def _collect_dependencies(crates_csv, versions_csv, deps_csv):
    cdf = pd.read_csv(crates_csv)
    cdf = cdf[["id", "name", "description", "homepage", "repository"]]
    cdf.fillna("", inplace=True)
    cdf.rename(columns={"id": "pkg_idx"}, inplace=True)

    vdf = pd.read_csv(versions_csv)
    vdf = vdf[
        [
            "crate_id",
            "id",
            "license",
            "num",
            "published_by",
            "created_at",
            "updated_at",
            "downloads",
        ]
    ]
    vdf.rename(columns={"crate_id": "pkg_idx"}, inplace=True)
    vdf = pd.merge(cdf, vdf, how="inner", on="pkg_idx")
    vdf.rename(
        columns={
            "id": "version_id",
            "downloads": "no_downloads",
            "published_by": "owner_id",
            "num": "version",
        },
        inplace=True,
    )

    ddf = pd.read_csv(deps_csv)
    ddf = ddf[["crate_id", "kind", "optional", "req", "target", "version_id"]]
    ddf.rename(
        columns={
            "crate_id": "target_idx",
            "req": "target_version",
        },
        inplace=True,
    )
    ddf = pd.merge(ddf, vdf[["pkg_idx", "name", "version", "version_id"]], how="left", on="version_id")

    ddf.rename(
        columns={"name": "source_name", "version_id": "source_idx", "version": "source_version", "kind": "kind_code"},
        inplace=True,
    )

    short_cdf = cdf[["pkg_idx", "name"]].copy()
    short_cdf.rename(
        columns={
            "pkg_idx": "target_idx",
            "name": "target_name",
        },
        inplace=True,
    )
    ddf = pd.merge(ddf, short_cdf, how="left", on="target_idx")

    ddf["kind"] = ""
    ddf.loc[ddf.kind_code == 0, "kind"] = Kind.NORMAL.name
    ddf.loc[ddf.kind_code == 1, "kind"] = Kind.BUILD.name
    ddf.loc[ddf.kind_code == 2, "kind"] = Kind.DEV.name

    ddf.loc[ddf.optional == "t", "optional"] = True
    ddf.loc[ddf.optional == "f", "optional"] = False

    ddf = ddf[
        [
            "pkg_idx",
            "source_idx",
            "target_idx",
            "source_name",
            "target_name",
            "source_version",
            "target_version",
            "kind",
            "optional",
            "target",
        ]
    ]
    ddf.fillna("", inplace=True)
    ddf.to_csv(DEPS_FILE, index=False)

def cleanup():
    filelist = glob(os.path.join(TMP_DIR, "*"))
    for f in filelist:
        if not f.endswith(".gitkeep"):
            shutil.rmtree(f)

def mine():
    LOGGER.info("Downloading database dump...")
    dump_file = Path(TMP_DIR, "db_dump.tar.gz")
    with open(dump_file, "wb") as fp:
        r = requests.get(CARGO_DB_DUMP_URL)
        fp.write(r.content)
    LOGGER.info("Extracting database dump...")
    with tarfile.open(dump_file) as fp:
        fp.extractall(TMP_DIR)

    os.remove(dump_file)
    dataset_dir = glob(TMP_DIR + "*")[0]  # TODO: is it always the last?
    dataset_dir = Path(dataset_dir, "data")

    crates_csv = Path(dataset_dir, "crates.csv")
    versions_csv = Path(dataset_dir, "versions.csv")
    users_csv = Path(dataset_dir, "users.csv")
    deps_csv = Path(dataset_dir, "dependencies.csv")

    LOGGER.info("Converting packages to core...")
    _collect_packages(crates_csv)
    LOGGER.info("Converting versions to core...")
    _collect_versions(crates_csv, versions_csv, users_csv)
    LOGGER.info("Converting dependencies to core...")
    _collect_dependencies(crates_csv, versions_csv, deps_csv)

    cleanup()    
    


if __name__ == "__main__":
    mine()
