import sys
import gzip
import os
import logging
import requests
import subprocess
import shutil
from datetime import datetime
from tqdm import tqdm
# from ratelimiter import RateLimiter
from dasea.common.datamodel import Package, Version, Dependency, Kind
from dasea.common.utils import _serialize_data

# Based on the documentation form here:
# https://guides.rubygems.org/rubygems-org-rate-limits/

RUBYGEMS_REGISTRY = "http://production.cf.rubygems.org/specs.4.8.gz"
TMP_REGISTRY_FILE = "./data/tmp/rubygems/rubygems_index"

PKG_URL = "https://rubygems.org/api/v1/gems/{pkg_name}.json"
VERSIONS_URL = "https://rubygems.org/api/v1/versions/{pkg_name}.json"
VERSION_URL = "https://rubygems.org/api/v2/rubygems/{pkg_name}/versions/{version}.json"

# RUBYGEMS_PACKAGE_URL =  "https://rubygems.org/api/v1/gems/{pkg_name}.json"
RUBYGEMS_VERSIONS_URL = "https://rubygems.org/api/v1/versions/{pkg_name}.json"
RUBYGEMS_VERSION_URL = "https://rubygems.org/api/v2/rubygems/{pkg_name}/versions/{version}.json"

HEADERS = {
    "User-Agent": "DaSEA Research Project (Please don't ban, https://dasea-project.github.io/DASEA)",
    "From": "daseaITU@gmail.com",
}

TODAY = datetime.today().strftime("%m-%d-%Y")
PKGS_FILE = f"data/out/rubygems/rubygems_packages_{TODAY}.csv"
VERSIONS_FILE = f"data/out/rubygems/rubygems_versions_{TODAY}.csv"
DEPS_FILE = f"data/out/rubygems/rubygems_dependencies_{TODAY}.csv"

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M"
)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)


def _collect_pkg_registry():
    if not os.path.isfile(TMP_REGISTRY_FILE):
        # Download and unpack index file
        r = requests.get(RUBYGEMS_REGISTRY, headers=HEADERS)
        content = gzip.decompress(r.content)
        with open(TMP_REGISTRY_FILE, "wb") as fp:
            fp.write(content)

    ## TODO: Maybe consider as Vagrant miner?
    # OBS, there needs to be a Ruby interpreter installed as `ruby` on the host
    ruby_prg = f'Marshal.load(File.read("{TMP_REGISTRY_FILE}")).each {{|el| puts el[0]}}'
    # OBS, there needs to `uniq` installed on the host
    cmd = f"ruby -e '{ruby_prg}' | uniq"
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    pkg_names = r.stdout.splitlines()

    return pkg_names



def _collect_packages(metadata_dict):
    pkg_idx_map = {}
    packages = []
    for idx, pkg_name in enumerate(metadata_dict):
        p = Package(idx, pkg_name, "RubyGems")
        packages.append(p)
        pkg_idx_map[pkg_name] = idx

    return pkg_idx_map, packages


# SEE: https://guides.rubygems.org/rubygems-org-rate-limits/
# FIXME: times out after a while
# @RateLimiter(max_calls=10, period=1) //
def _collect_versions_with_dependencies(metadata_dict, pkg_idx_map):
    versions = []
    dependencies = []
    version_idx = 0

    for pkg_name in tqdm(metadata_dict):
        # Request the package versions data
        pkg_url = RUBYGEMS_VERSIONS_URL.format(pkg_name=pkg_name)
        r = requests.get(pkg_url, headers=HEADERS)
        if not r.ok:
            LOGGER.error(r.status_code, "VERSION", pkg_name)
            continue

        version_numbers = [v["number"] for v in r.json()][::-1]
        for version_number in version_numbers:
            # Request the specific version data
            version_url = RUBYGEMS_VERSION_URL.format(pkg_name=pkg_name, version=version_number)
            req = requests.get(version_url, headers=HEADERS)
            if not req.ok:
                LOGGER.error(r.status_code, "VERSION", pkg_name, version_number)
                continue

            version_info = req.json()
            pkg_idx = pkg_idx_map.get(pkg_name, None)
            v = Version(
                    idx=version_idx,
                    pkg_idx=pkg_idx,
                    name=pkg_name,
                    version=version_number,
                    # licenses sometimes is an array, sometimes a string
                    license=','.join(version_info["licenses"]) if version_info["licenses"] else None,
                    description=version_info["description"],
                    homepage=version_info["homepage_uri"],
                    repository=version_info["source_code_uri"],
                    author=version_info["authors"],
                    maintainer=None # No such info in RubyGems
                )
            versions.append(v)

            for kind, deps in version_info["dependencies"].items():
                for d in deps:
                    target_name = d["name"]
                    version_constraint = d["requirements"]
                    target_idx = pkg_idx_map.get(target_name, None)

                d = Dependency(
                    pkg_idx=pkg_idx,
                    source_idx=version_idx,
                    target_idx=target_idx,
                    source_name=pkg_name,
                    target_name=target_name,
                    source_version=version_number,
                    target_version=version_constraint,
                    kind=kind,
                )
                dependencies.append(d)
            version_idx += 1

    return versions, dependencies

def mine():
    LOGGER.info("Collecting RubyGems registry")
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

    # delete tmp files
    shutil.rmtree(TMP_REGISTRY_FILE, ignore_errors=True)

if __name__ == "__main__":
    mine()