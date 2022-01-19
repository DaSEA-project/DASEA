import requests
import subprocess
from dataclasses import dataclass
from dasea.datamodel import Package, Version, Dependency, Kind
from dasea.utils import _serialize_data
from collections import defaultdict
from tqdm import tqdm


PKGS_FILE = "data/out/ubuntu/packages.csv"
VERSIONS_FILE = "data/out/ubuntu/versions.csv"
DEPS_FILE = "data/out/ubuntu/dependencies.csv"

VERSIONS_DB = "data/tmp/ubuntu/versions_db"


@dataclass
class APTPackage(Package):
    platform: str
    virtual: bool


@dataclass
class APTVersion(Version):
    original_maintainer: str
    architecture: str
    origin: str


def _get_platform_str():
    cmd = "uname -n"  # "lsb_release -sd"
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return r.stdout.strip()


# def _collect_binary_packages():
#     cmd = "apt list 2>/dev/null"
#     r = subprocess.run(cmd, shell=True, capture_output=True, text=True)

#     pkg_names = []
#     # Skip the first line since `apt` starts with printing a line saying `Listing...`
#     for l in r.stdout.splitlines()[1:]:
#         pkg_info = l.split()[0]
#         pkg_name = pkg_info.split("/")[0]
#         pkg_names.append(pkg_name)

#     return pkg_names


# def _collect_virtual_packages():
#     # https://www.debian.org/doc/manuals/aptitude/ch02s04s05.en.html
#     cmd = "aptitude --display-format '%p' search '?virtual'"
#     r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
#     # We keep the architecture field since this is what package versions use to refer to virtual pkgs
#     virt_pkg_names = [l.strip() for l in r.stdout.splitlines()]

#     return virt_pkg_names


# def _collect_source_packages():
#     # With the following, one finds many more source packages than by parsing the
#     # aptitude --display-format '%p' search '?source-package()'
#     # 106638
#     cmd = 'find /var/lib/apt/lists/ -type f -name "*Sources" -exec grep "Package: " {} \; 2>/dev/null | sort | uniq'
#     r = subprocess.run(cmd, shell=True, capture_output=True, text=True)

#     pkg_names = [l.replace("Package: ", "") for l in r.stdout.splitlines()]

#     return pkg_names  # 29299


# from collections import defaultdict


# def _collect_pkg_versions():
#     cmd = "apt list --all-versions 2>/dev/null"
#     r = subprocess.run(cmd, shell=True, capture_output=True, text=True)

#     pkg_version_map = defaultdict(dict)
#     # Skip the first line since `apt` starts with printing a line saying `Listing...`
#     for l in r.stdout.splitlines()[1:]:
#         if l:  # various versions are separated by line breaks
#             vals = l.split()
#             if len(vals) == 3:
#                 pkg_info, version, arch = vals
#             elif len(vals) > 3:
#                 pkg_info, version, arch = vals[:3]

#         pkg_name = pkg_info.split("/")[0]
#         pkg_version_map[pkg_name][version] = {}

#     return pkg_version_map


# fname = "/var/lib/apt/lists/archive.ubuntu.com_ubuntu_dists_bionic_main_binary-amd64_Packages"


def _split_apt_list_file(fname):
    with open(fname) as fp:
        block = []
        for line in fp:
            if line.strip():
                block.append(line.rstrip())
            else:
                yield block
                block = []


# def _parse_apt_list_file(fname, pkg_version_map):
#     with open(fname) as fp:
#         version_dict = {}
#         for line in fp:
#             if not line.strip():
#                 if pkg_version_map[version_dict["Package"]].get(version_dict["Version"], None):
#                     # TODO: compare it!
#                     # print(f'{version_dict["Package"]} {version_dict["Version"]} contains already data')
#                     # print(version_dict)
#                     # print("-------")
#                     # print(pkg_version_map[version_dict["Package"]][version_dict["Version"]])
#                     # break
#                     pass
#                 else:
#                     pkg_version_map[version_dict["Package"]][version_dict["Version"]] = version_dict
#                 version_dict = {}
#             elif line.startswith(" "):
#                 continue
#             else:
#                 try:
#                     key, value = line.split(": ", 1)
#                     version_dict[key] = value.strip()
#                     if key == "Package" and value == "xdg-desktop-portal-dev":
#                         print(version_dict)
#                 except Exception as e:
#                     # We ignore all fields with multiple values on multiple lines
#                     # These are for example Package-List, Files, Checksums-Sha1, Checksums-Sha256, etc.
#                     # in case of source packages
#                     continue
#     return pkg_version_map


def _parse_apt_block(lines, kind="binary"):
    if kind == "binary":
        key_set = BIN_PKG_KEYS
    elif kind == "source":
        key_set = SRC_PKG_KEYS

    version_dict = {}
    for line in lines:
        if line.startswith(" "):
            continue

        splitted_line = line.split(": ", 1)
        if len(splitted_line) > 1: 
            key, value = splitted_line
            if key in key_set:
                version_dict[key] = value

    return version_dict


def _parse_relation(rel_str):
    # can contain version constraints in (), architecture constraints in [], and other constraints in <>
    dep_els = rel_str.split(" ", 1)
    if len(dep_els) == 1:
        dep_target = dep_els[0]
    elif len(dep_els) > 1:
        if "(" in dep_els[1]:
            # contains version constraint
            pass
        elif "[" in dep_els[1]:
            # contains architecture constraint
            pass
        elif "<" in dep_els[1]:
            # contains other constraint
            pass
    
    dep_target = rel_str.split(" ", 1)



def _parse_relations(lst_str):
    deps_strs = lst_str.split(", ")
    for d in deps_strs:
        if "|" in d:
            # list of alternatives
            disjunction_dep_els = d.split("|")
            disjunction_dep_els = [d.strip() for d in disjunction_dep_els]
        else:
            
        


        if len(dep_els) == 1:
            dep_target = dep_els[0]
        if len(dep_els) == 1:

from glob import glob

LISTS_DIR = "/var/lib/apt/lists/"
    # There are 69 keywords in these files of which we keep the following for binary packages
BIN_PKG_KEYS = set([
    "Package",
    "Version",
    "Architecture",
    "Description",
    "Homepage",
    "Maintainer",
    "Original-Maintainer",
    "Original-Vcs-Git",
    # Relations
    "Depends",
    "Breaks",
    "Built-Using",
    "Conflicts",
    "Enhances",
    "Provides",
    "Recommends",
    "Replaces",
    "Suggests",
])

SRC_PKG_KEYS = set([
    "Package",
    "Version",
    "Architecture",
    "Homepage",
    "Maintainer",
    "Original-Maintainer",
    "Uploaders",
    # List of binaries that are created from it
    "Binary",
    # Relations
    "Build-Conflicts",
    "Build-Conflicts-Arch",
    "Build-Conflicts-Indep",
    "Build-Depends",
    "Build-Depends-Arch",
    "Build-Depends-Indep",
    "Build-Indep-Architecture",
    "Debian-Vcs-Bzr",
    "Debian-Vcs-Git",
    "Debian-Vcs-Svn",
    # "Dgit",
    "Orig-Vcs-Svn",
    "Original-Vcs-Bzr",
    "Original-Vcs-Git",
    "Upstream-Vcs-Bzr",  # appears only once on 18.04
    "Vcs-Arch",
    "Vcs-Bzr",
    "Vcs-Cvs",
    "Vcs-Darcs",
    "Vcs-Debian-Git",
    "Vcs-Git",
    "Vcs-Hg",
    "Vcs-Mtn",
    "Vcs-Svn",
    "Vcs-Upstream-Bzr",  # appears only once on 18.04
])

def _collect_apt_metadata():
    pkg_list_files = glob(LISTS_DIR + "*Packages")
    src_list_files = glob(LISTS_DIR + "*Sources")

    bin_blocks = [b for f in pkg_list_files for b in _split_apt_list_file(f)]
    src_blocks = [b for f in src_list_files for b in _split_apt_list_file(f)]

    # # get all keywords
    # keywords = set({})
    # for block in bin_blocks:
    #     for line in block:
    #         if not line.startswith(" "):
    #             keywords.add(line.split(": ", 1)[0])

    # TODO: This does not contain virtual packages yet...
    bin_blocks_dicts = [_parse_apt_block(bb) for bb in bin_blocks]
    src_blocks_dicts = [_parse_apt_block(sb, kind="source") for sb in src_blocks]

    # Multiple occurrences of source blocks with the same name are caused by various versions

    # Convert to map, TODO: do the same for bin_pkgs
    src_pkg_map = defaultdict(dict)
    for d in src_blocks_dicts:
        d_existing = src_pkg_map.get(d["Package"], {}).get(d["Version"], {})
        if not d == d_existing:
            src_pkg_map[d["Package"]][d["Version"]] = d


    bin_pkg_map = defaultdict(dict)
    for d in bin_blocks_dicts:
        d_existing = bin_pkg_map.get(d["Package"], {}).get(d["Version"], {})
        if d_existing and d["Architecture"] not in d_existing["Architecture"]:  # only difference is architecture
            bin_pkg_map[d["Package"]][d["Version"]]["Architecture"] += f' {d["Architecture"]}'






        if d == d_existing:
            bin_pkg_map[d["Package"]][d["Version"]] = d


In [113]: Counter([p["Package"] for p in bin_blocks_dicts]).most_common(10)
Out[113]:
[('linux-cloud-tools-common', 294),
 ('linux-doc', 294),
 ('linux-source-4.15.0', 294),
 ('linux-tools-common', 294),
 ('linux-tools-host', 294),
 ('linux-hwe-5.4-cloud-tools-common', 128),
 ('linux-hwe-5.4-source-5.4.0', 128),
 ('linux-hwe-5.4-tools-common', 128),
 ('linux-source-5.3.0', 108),
 ('linux-oem-osp1-tools-host', 106)]


    [f for f in src_blocks_dicts if f["Package"] == "rabbitmq-server"]








    pkg_version_map = _collect_pkg_versions()
    for fname in pkg_list_files:
        print(fname)
        print()
        pkg_version_map = _parse_apt_list_file(fname, pkg_version_map)
    return pkg_version_map
