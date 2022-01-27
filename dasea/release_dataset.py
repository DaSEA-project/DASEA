import os
import sys
import json
import requests
import subprocess
from glob import glob
from pathlib import Path
from datetime import datetime, timedelta


TODAY = datetime.today().strftime("%m-%d-%Y")
DATA_DIR = "data/out/"


def create_compressed_archive():
    glob_pattern = f"{DATA_DIR}**/*.csv"
    data_files = glob(glob_pattern, recursive=True)
    data_files = [d.replace(DATA_DIR, "") for d in data_files]

    archive_file = f"dasea_{TODAY}.tar.bz2"
    cmd = f"tar -cvjf {archive_file} {' '.join(data_files)}"
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=DATA_DIR)
    if r.returncode != 0:
        print(f"Cannot create archive {archive_file}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"Created {archive_file}")
    return archive_file
    # headers = {"Content-Type": "application/json", "Authorization": f"Bearer {zenodo_api_key}"}
    # r = requests.get(f"{BASE_URL}", headers=headers)
    # print(r.status_code)
    # print(json.dumps(r.json(), indent=2))


def update_homepage(new_dataset_url):
    filename = "homepage/datasets.json"
    file = open(filename, "r+")
    file_data = json.load(file)
    print(file_data)

    latest_release = {"date": TODAY, "url": new_dataset_url}

    file_data["datasets"].append(latest_release)

    file.seek(0)
    json.dump(file_data, file, indent=4)


def push_dataset_to_zenodo(dataset_path, sandbox=False):
    # API Documentation is here:
    # https://developers.zenodo.org/?python#quickstart-upload
    release_date_str = Path(dataset_path).name.replace("dasea_", "").split(".")[0]
    # TODO: Move that to another place once the package gets distributed via PyPI
    metadata_config_file = "dataset_conf.json"

    try:
        zenodo_api_token = os.environ["ZENODO_API_TOKEN"]
    except:
        print(f"Cannot find ZENODO_API_TOKEN in environment", file=sys.stderr)
        sys.exit(1)

    if sandbox:
        api_url = "https://sandbox.zenodo.org/api/"
    else:
        api_url = "https://zenodo.org/api/"
    deposit_url = f"{api_url}deposit/depositions"
    params = {"access_token": zenodo_api_token}

    # A continuously updated dataset of software dependencies covering various package manager ecosystems. Read more on https://<organization>.github.io/DASEA/
    modification_time = datetime.fromtimestamp(os.stat(metadata_config_file)[-2])
    if datetime.now() - modification_time > timedelta(minutes=3):
        print(f"Be sure to update the dataset metadata in {metadata_config_file} before push!", file=sys.stderr)
        sys.exit(1)
    with open(metadata_config_file) as fp:
        metadata = json.load(fp)

    metadata["title"] += f" {release_date_str}"
    metadata = {"metadata": metadata}

    print("Creating a bucket for the dataset...")
    r = requests.post(deposit_url, params=params, json=metadata)
    if not r.ok:
        print(r.json())
    r.raise_for_status()

    bucket_url = r.json()["links"]["bucket"]
    publish_url = r.json()["links"]["publish"]
    discard_url = r.json()["links"]["discard"]
    deposit_url = r.json()["links"]["html"]

    # Upload the dataset to the bucket
    print("Uploading the dataset to the bucket...")
    with open(dataset_path, "rb") as fp:
        # TODO: when dataset gets bigger, convert that to streaming of data
        r = requests.put(f"{bucket_url}/{Path(dataset_path).name}", data=fp, params=params)
    if not r.ok:
        print(r.json())
    r.raise_for_status()

    print(f"Double check all information on {deposit_url}")
    answer = input("Are you sure that you want to finally publish the dataset? [y/N] ")
    if answer == "y":
        print("Publishing the dataset...")
        r = requests.post(publish_url, params=params)
        r.raise_for_status()
        final_url = r.json()["links"]["latest_html"]
        update_homepage(final_url)

        print(f"Published dataset to {final_url}")
    else:
        print("Discarding the dataset...")
        r = requests.post(discard_url, params=params)
        if not r.ok:
            print(r.json())
        r.raise_for_status()
