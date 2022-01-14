import requests
from dasea.datamodel import Package, Version, Dependency, Kind
from dasea.utils import _serialize_data


# The API documentation is here: https://formulae.brew.sh/docs/api/
#  It does not mention any rate limits
# Currently, we only mine MacOS formulae excluding casks. There would be two more URLs...
# https://formulae.brew.sh/api/formula-linux.json
# https://formulae.brew.sh/api/cask.json
BREW_FORMULA_URL = "https://formulae.brew.sh/api/formula.json"


PKGS_FILE = "data/out/homebrew/packages.csv"
VERSIONS_FILE = "data/out/homebrew/versions.csv"
DEPS_FILE = "data/out/homebrew/dependencies.csv"


def _collect_formulae():
    # Alternatively, they could also be cloned and parsed with Ruby from
    # https://github.com/Homebrew/homebrew-core/tree/master/Formula
    r = requests.get(BREW_FORMULA_URL)
    return r.json()


def _collect_packages(pkg_idx_map):
    packages = []
    for pkg_name, idx in pkg_idx_map.items():
        p = Package(idx, pkg_name, "Homebrew")
        packages.append(p)

    return packages


def _collect_versions(metadata_lst, pkg_idx_map):
    versions = []
    for version_idx, version_info in enumerate(metadata_lst):
        pkg_name = version_info["name"]
        v = Version(
            idx=version_idx,  # There is only one version per formula returned, the most recent one
            pkg_idx=pkg_idx_map.get(pkg_name, None),
            name=pkg_name,
            version=version_info["versions"]["stable"],
            license=version_info["license"],
            description=version_info["desc"],
            homepage=version_info["homepage"],
            repository=version_info["urls"]["stable"]["url"],
            author=None,
            maintainer=None,
        )
        versions.append(v)

    return versions


def _collect_dependencies(metadata_lst, pkg_idx_map):
    dep_kind_map = {
        "build_dependencies": Kind.BUILD,
        "recommended_dependencies": Kind.RECOMMEND,
        "optional_dependencies": Kind.OPTIONAL,
        "conflicts_with": Kind.CONFLICTS,
        "build": Kind.BUILD,
        "test": Kind.TEST,
    }

    deps = []
    for version_idx, version_info in enumerate(metadata_lst):
        pkg_name = version_info["name"]
        source_pkg_idx = pkg_idx_map.get(pkg_name, None)

        for dep_kind in [
            "dependencies",
            "build_dependencies",
            "recommended_dependencies",  # seem to be always empty currently
            "optional_dependencies",  # seem to be always empty currently
            # Requirements are not in formulae, i.e., there won't be an ID
            # therefore exclude them, see https://docs.brew.sh/Formula-Cookbook
            "conflicts_with",
        ]:

            for target_name in version_info[dep_kind]:
                kind = dep_kind_map.get(dep_kind, None)
                if kind:
                    kind_str = kind.name
                else:
                    kind_str = ""
                d = Dependency(
                    pkg_idx=source_pkg_idx,
                    source_idx=version_idx,
                    target_idx=pkg_idx_map.get(target_name, None),
                    source_name=pkg_name,
                    target_name=target_name,
                    source_version=version_info["versions"]["stable"],
                    target_version=None,  # Does not exist for dependencies, build_dependencies, etc.
                    kind=kind_str,
                )
                deps.append(d)

        for dep in version_info["uses_from_macos"]:
            if type(dep) == str:
                target_name = dep
                kind = Kind.USES_FROM_MACOS.name
            elif type(dep) == dict:
                target_name, kind = list(dep.items())[0]
                if type(kind) == list:
                    for el in kind:
                        if el == "build":
                            kind = Kind.USES_FROM_MACOS_BUILD
                        elif el == "test":
                            kind = Kind.USES_FROM_MACOS_TEST

                        d = Dependency(
                            pkg_idx=source_pkg_idx,
                            source_idx=version_idx,
                            target_idx=None,
                            source_name=pkg_name,
                            target_name=target_name,
                            source_version=version_info["versions"]["stable"],
                            target_version=None,  # Does not exist
                            kind=kind.name,
                        )
                        deps.append(d)
                    continue

            d = Dependency(
                pkg_idx=source_pkg_idx,
                source_idx=version_idx,
                target_idx=pkg_idx_map.get(target_name, None),
                source_name=pkg_name,
                target_name=target_name,
                source_version=version_info["versions"]["stable"],
                target_version=None,  # Does not exist
                kind=kind,
            )
            deps.append(d)

        # TODO: Consider if the requirements field should become part of the model in future
    return deps


def mine():
    formulae = _collect_formulae()

    pkg_idx_map = {f["name"]: idx for idx, f in enumerate(formulae)}

    packages_lst = _collect_packages(pkg_idx_map)
    versions_lst = _collect_versions(formulae, pkg_idx_map)
    deps_lst = _collect_dependencies(formulae, pkg_idx_map)

    _serialize_data(packages_lst, PKGS_FILE)
    _serialize_data(versions_lst, VERSIONS_FILE)
    _serialize_data(deps_lst, DEPS_FILE)


if __name__ == "__main__":
    mine()
