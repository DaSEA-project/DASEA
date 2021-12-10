import sys
import csv
import logging
import requests
import subprocess
from glob import glob
from pathlib import Path
from shutil import which
from dataclasses import dataclass
from urllib.parse import urlparse
from dasea.datamodel import Package, Version, Dependency, Kind
from dasea.utils import _serialize_data

NIMBLE_MINE_DIR = "data/tmp/nimble"
NIMBLE_REGISTRY = "https://raw.githubusercontent.com/nim-lang/packages/master/packages.json"
PKGS_FILE = "data/out/nimble/packages.csv"
VERSIONS_FILE = "data/out/nimble/versions.csv"
DEPS_FILE = "data/out/nimble/dependencies.csv"

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M"
)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

# Nimble package manager has to be available
if not which("nimble"):
    LOGGER.error("Nimble package manager has to be installed and on PATH.")
    sys.exit(1)


@dataclass
class NimblePackage(Package):
    repository: str
    description: str
    license: str
    homepage: str


def _collect_pkg_registry():
    r = requests.get(NIMBLE_REGISTRY)
    if not r.ok:
        raise IOError("Cannot download Nimble registry.")
    return r.json()


def _collect_packages(pkgs_lst):
    pkg_idx_map = {}
    packages = []
    alias_packages = []
    pkg_idx = 0
    for pkg_info in pkgs_lst:
        if pkg_info.get("alias", ""):
            alias_packages.append((pkg_info["name"], pkg_info["alias"]))
        else:
            p = NimblePackage(
                pkg_idx,
                name=pkg_info["name"],
                pkgman="Nimble",
                platform="Nim",
                repository=pkg_info.get("url", ""),
                description=pkg_info.get("description", ""),
                license=pkg_info.get("license", ""),
                homepage=pkg_info.get("web", ""),
            )
            packages.append(p)
            pkg_idx_map[pkg_info["name"]] = pkg_idx
            pkg_idx += 1

    # Let aliases point to the original package
    for pkg_alias_name, pkg_name in alias_packages:
        pkg_idx_map[pkg_alias_name] = pkg_idx_map[pkg_name]

    return pkg_idx_map, packages


def _collect_versions(pkgs_lst, pkg_idx_map):
    for pkg_info in pkgs_lst:
        if pkg_info.get("alias", ""):
            continue  # Don't collect anything for an alias to a package

        repo_url = pkg_info.get("url", "")
        if not repo_url:
            continue  # Do nothing for non-existing repositories.

        if pkg_info["method"] != "git":
            # Since bitbucket stopped hosting HG repositories, there are only
            # Git repositories left.
            continue

        outpath = Path(NIMBLE_MINE_DIR, Path(urlparse(repo_url).path).stem)
        if outpath.is_dir():
            continue
            # cmd = f"git -C {str(outpath)} pull"
        else:
            pr = urlparse(repo_url)
            if pr.query:
                repo_url = f"{pr.scheme}://{pr.netloc}/{pr.path}"
            cmd = f"git clone -c http.sslVerify=false --depth=1 {repo_url} {str(outpath)}"

        if not repo_url.startswith("git@"):
            r = requests.get(repo_url, verify=False)
            if not r.ok:
                # Only clone the repository if it still seems to be there
                continue

        r = subprocess.run(cmd, shell=True)
        if r.returncode != 0:
            LOGGER.warn(f"Cannot clone {repo_url}.")

    glob_pattern = f"{NIMBLE_MINE_DIR}/**/*.nimble"
    metadata_files_lst = glob(glob_pattern, recursive=True)

    versions = []
    deps = []
    for version_idx, m in enumerate(metadata_files_lst):
        cmd = f"nimble dump {m}"
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        metadata_lines = r.stdout.splitlines()
        pkg_name = version = author = desc = license = requirements = ""
        reqs_lst = []
        for line in metadata_lines:
            if line.startswith("name: "):
                # remove Nim string delimiters with indexing
                pkg_name = line.replace("name: ", "")[1:-1]
            elif line.startswith("version: "):
                version = line.replace("version: ", "")[1:-1]
            elif line.startswith("author: "):
                author = line.replace("author: ", "")[1:-1]
            elif line.startswith("desc: "):
                desc = line.replace("desc: ", "")[1:-1]
            elif line.startswith("license: "):
                license = line.replace("license: ", "")[1:-1]
            elif line.startswith("requires: "):
                requirements = line.replace("requires: ", "")[1:-1]
                if requirements:
                    reqs_lst = [(r.split()[0], " ".join(r.split()[1:])) for r in requirements.split(",")]

        v = Version(
            idx=version_idx,
            pkg_idx=pkg_idx_map.get(pkg_name, None),
            name=pkg_name,
            version=version,
            license=license,
            description=desc,
            homepage="",
            repository="",
            author=author,
            maintainer="",
        )
        versions.append(v)

        for req_name, req_version_constraint in reqs_lst:
            d = Dependency(
                pkg_idx=pkg_idx_map.get(pkg_name, None),
                source_idx=version_idx,
                target_idx=pkg_idx_map.get(req_name, None),
                source_name=pkg_name,
                target_name=req_name,
                source_version=version,
                target_version=req_version_constraint,
                kind=Kind.BUILD.name,
            )
            deps.append(d)

    return versions, deps


def mine():
    try:
        metadata_lst = _collect_pkg_registry()
    except IOError as e:
        LOGGER.error(e)
        sys.exit(1)

    pkg_idx_map, packages_lst = _collect_packages(metadata_lst)
    versions_lst, deps_lst = _collect_versions(metadata_lst, pkg_idx_map)

    _serialize_data(packages_lst, PKGS_FILE)
    _serialize_data(versions_lst, VERSIONS_FILE)
    _serialize_data(deps_lst, DEPS_FILE)


if __name__ == "__main__":
    mine()
