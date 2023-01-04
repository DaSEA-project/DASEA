import logging
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from shutil import which

from dasea.common.datamodel import Dependency, Kind, Package, Version
from dasea.common.utils import _serialize_data

OPAM_REGISTRY = "https://github.com/ocaml/opam-repository.git"
TMP_DIR = "./data/tmp/opam"

TODAY = datetime.today().strftime("%m-%d-%Y")
PKGS_FILE = f"data/out/opam/opam_packages_{TODAY}.csv"
VERSIONS_FILE = f"data/out/opam/opam_versions_{TODAY}.csv"
DEPS_FILE = f"data/out/opam/opam_dependencies_{TODAY}.csv"

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M"
)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

if not which("opam"):
    LOGGER.error("OPAM package manager needs to be installed and on PATH.")
    sys.exit(1)

METADATA_FIELDS = (
    "opam-version",
    "name",
    "version",
    "maintainer",
    "authors",
    "license",
    "homepage",
    "doc",
    "bug-reports",
    "dev-repo",
    "tags",
    "depends",
    "depopts",
    "conflicts",
    "conflict-class",
    "depexts",
    "synopsis",
    "description",
    "url",
)


@dataclass
class OPAMVersion(Version):
    opam_version: str
    doc: str
    bug_reports: str
    tags: str
    pkg_src_url: str

    depends: str
    depopts: str
    conflicts: str
    conflict_class: str
    depexts: str
    synopsis: str


def _collect_pkg_registry():
    if Path(TMP_DIR).is_dir():
        cmd = f"git -C {TMP_DIR} pull"
    else:
        cmd = f"git clone -v {OPAM_REGISTRY} {TMP_DIR}"
    print(cmd)
    r = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if r.returncode != 0:
        raise IOError("Cannot clone/update OPAM registry.")


def _get_pkg_names():
    pkg_names = []
    dir_names = Path(TMP_DIR, "packages").iterdir()

    for dir_name in dir_names:
        pkg_names.append(dir_name.name)

    return pkg_names


def _collect_packages(pkg_names: list):
    pkg_idx_map = {}
    packages = []
    for idx, pkg_name in enumerate(pkg_names):
        p = Package(idx, pkg_name, "OPAM")
        packages.append(p)
        pkg_idx_map[pkg_name] = idx

    return pkg_idx_map, packages


def get_opam_contents(opam_metadata_file):
    with open(opam_metadata_file) as fp:
        contents = fp.readlines()
    return contents


def _retrieve_opam_metadata():
    opam_metadata_files = [p for p in Path(TMP_DIR, "packages").glob("**/*opam") if p.is_file()]
    metadata_dict = {}
    for opam_metadata_file in opam_metadata_files:
        pkg_name = opam_metadata_file.parts[4]
        pkg_version = opam_metadata_file.parts[5].replace(pkg_name + ".", "")

        if metadata_dict.get(pkg_name, {}):
            metadata_dict[pkg_name][pkg_version] = {el: "" for el in METADATA_FIELDS}
        else:
            metadata_dict[pkg_name] = {pkg_version: {el: "" for el in METADATA_FIELDS}}

        cmd = f'opam info --normalise --field={",".join(METADATA_FIELDS)} --just-file {opam_metadata_file}'

        r = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if r.returncode != 0:
            raise IOError(f"Cannot get metadata from {opem_file_path}.")

        for field, line in zip(METADATA_FIELDS, r.stdout.decode().splitlines()):
            metadata_dict[pkg_name][pkg_version][field] = line.replace(f"{field}:", "").strip()

    return metadata_dict


def _parse_opam_string_info(pkg_name, pkg_version, metadata_dict):
    metadata_fields_excluded_from_parsing = (
        "depends",
        "depopts",
        "conflicts",
        "conflict-class",
        "depexts",
    )

    metadata_fields = set(METADATA_FIELDS) - set(metadata_fields_excluded_from_parsing)
    # Keep all the other fields to dump them unparsed to CSV files.
    for field in metadata_fields:
        value = metadata_dict[pkg_name][pkg_version][field]
        if not value:
            continue
        if value[0] == "[" and value[-1] == "]":
            # Parse lists of string values
            metadata_dict[pkg_name][pkg_version][field] = eval(value.replace('" "', '", "'))
        else:
            # Parse values to strings
            metadata_dict[pkg_name][pkg_version][field] = eval(value)


def _reference_string_list_to_tuple(value, field="depends"):
    dependency_specs = []
    if not value:
        return dependency_specs

    deps_str = value[1:-1]
    deps_str = deps_str.replace('" "', ",").replace('} "', "},").replace('" {', " {")

    if deps_str[-1] == '"':
        deps_str = deps_str[:-1]

    deps = deps_str[1:].split(",")

    for dep in deps:
        if dep[-1] == "}":  # contains a constraint
            dep_target, constraint = dep.split(" ", 1)

            if field == "conflicts":
                kind = Kind.CONFLICTS.name
            else:
                if "build" in constraint:
                    kind = Kind.BUILD.name
                elif "with-test" in constraint:
                    kind = Kind.TEST.name
                elif "with-doc" in constraint:
                    kind = Kind.DOC.name
                elif "with-dev-setup" in constraint:
                    kind = Kind.DEV.name
                else:
                    kind = Kind.RUN.name

        else:  # plain dependency
            dep_target, constraint = dep, None
            if field == "conflicts":
                kind = Kind.CONFLICTS.name
            else:
                kind = Kind.RUN.name

        dependency_specs.append((dep_target, constraint, kind))
    return dependency_specs


def _parse_opam_dependency_info(pkg_name, pkg_version, metadata_dict):
    value = metadata_dict[pkg_name][pkg_version]["depends"]
    dependency_specs = _reference_string_list_to_tuple(value)

    value = metadata_dict[pkg_name][pkg_version]["conflicts"]
    dependency_specs += _reference_string_list_to_tuple(value, field="conflicts")
    return dependency_specs


def _collect_versions(pkg_idx_map, metadata_dict):
    versions = []
    version_idx = 0

    for pkg_name, pkg_metadata in metadata_dict.items():
        for pkg_version in pkg_metadata.keys():

            # Convert all stringy fields into proper strings or list of strings.
            # Leave all other more complex fields untouched.
            _parse_opam_string_info(pkg_name, pkg_version, metadata_dict)

            v = OPAMVersion(
                idx=version_idx,
                pkg_idx=pkg_idx_map.get(pkg_name, None),
                name=pkg_name,
                version=pkg_version,
                description=metadata_dict[pkg_name][pkg_version]["description"],
                homepage=metadata_dict[pkg_name][pkg_version]["homepage"],
                license=metadata_dict[pkg_name][pkg_version]["license"],
                repository=metadata_dict[pkg_name][pkg_version]["dev-repo"],
                author=metadata_dict[pkg_name][pkg_version]["authors"],
                maintainer=metadata_dict[pkg_name][pkg_version]["maintainer"],
                pkg_src_url=metadata_dict[pkg_name][pkg_version]["url"],
                # The following fields are unparsed from the original metadata
                depends=metadata_dict[pkg_name][pkg_version]["depends"],
                depopts=metadata_dict[pkg_name][pkg_version]["depopts"],
                conflicts=metadata_dict[pkg_name][pkg_version]["conflicts"],
                depexts=metadata_dict[pkg_name][pkg_version]["depexts"],
                synopsis=metadata_dict[pkg_name][pkg_version]["synopsis"],
                opam_version=metadata_dict[pkg_name][pkg_version]["opam-version"],
                doc=metadata_dict[pkg_name][pkg_version]["doc"],
                tags=metadata_dict[pkg_name][pkg_version]["tags"],
                bug_reports=metadata_dict[pkg_name][pkg_version]["bug-reports"],
                conflict_class=metadata_dict[pkg_name][pkg_version]["conflict-class"],
            )
            versions.append(v)
            version_idx += 1
    return versions


def _collect_dependencies(pkg_idx_map, metadata_dict):
    deps = []
    version_idx = 0

    for pkg_name, pkg_metadata in metadata_dict.items():
        for pkg_version in pkg_metadata.keys():

            pkg_idx = pkg_idx_map.get(pkg_name, None)

            dependency_specs = _parse_opam_dependency_info(pkg_name, pkg_version, metadata_dict)

            for dep_name, dep_constraint, kind in dependency_specs:
                source_pkg_idx = pkg_idx_map.get(pkg_name, None)
                target_pkg_idx = pkg_idx_map.get(dep_name, None)

                d = Dependency(
                    pkg_idx=source_pkg_idx,
                    source_idx=version_idx,
                    target_idx=target_pkg_idx,
                    source_name=pkg_name,
                    target_name=dep_name,
                    source_version=pkg_version,
                    target_version=dep_constraint,
                    kind=kind,
                )
                deps.append(d)
            version_idx += 1

    return deps


def mine():
    LOGGER.info("Collecting OPAM data...")
    try:
        _collect_pkg_registry()
    except IOError as e:
        LOGGER.error(str(e))
        sys.exit(1)

    pkg_names_lst = _get_pkg_names()

    LOGGER.info("Creating DaSEA packages...")
    pkg_idx_map, packages_lst = _collect_packages(pkg_names_lst)

    LOGGER.info("Creating DaSEA versions...")
    metadata_dict = _retrieve_opam_metadata()
    versions_lst = _collect_versions(pkg_idx_map, metadata_dict)

    LOGGER.info("Creating DaSEA dependencies...")
    deps_lst = _collect_dependencies(pkg_idx_map, metadata_dict)

    _serialize_data(packages_lst, PKGS_FILE)
    _serialize_data(versions_lst, VERSIONS_FILE)
    _serialize_data(deps_lst, DEPS_FILE)


if __name__ == "__main__":
    mine()
