"""DaSEA - Dataset for Software Ecosystem Analysis.

A tool to mine dependency networks from various software ecosystems.

Usage:
  dasea mine <pkgmanager>
  dasea release
  dasea push [--sandbox] <dataset>

Options:
  -h --help     Show this screen.
  --version     Show version.
"""
import sys
from docopt import docopt


def main():
    # TODO: Adjust version to what is given in pyproject.toml
    arguments = docopt(__doc__, version="0.1.0")

    # Imports are inlined below to allow for incomplete setups on remote miners
    if arguments["mine"]:
        if arguments["<pkgmanager>"] == "fpm":
            from core.miners.fpm import mine as fpm_mine

            fpm_mine()
        elif arguments["<pkgmanager>"] == "conan":
            from core.miners.conan import mine as conan_mine

            conan_mine()
        elif arguments["<pkgmanager>"] == "cargo":
            from core.miners.cargo import mine as cargo_mine

            cargo_mine()
        elif arguments["<pkgmanager>"] == "vcpkg":
            from core.miners.vcpkg import mine as vcpkg_mine

            vcpkg_mine()
        elif arguments["<pkgmanager>"] == "alire":
            from core.miners.alire import mine as alire_mine

            alire_mine()
        elif arguments["<pkgmanager>"] == "maven":
            from core.miners.maven import mine as maven_mine

            maven_mine()
        elif arguments["<pkgmanager>"] == "nimble":
            from core.miners.nimble import mine as nimble_mine

            nimble_mine()
        elif arguments["<pkgmanager>"] == "apt":
            from core.miners.apt import mine as apt_mine

            apt_mine()
        elif arguments["<pkgmanager>"] == "ports":
            from core.miners.ports import mine as ports_mine

            ports_mine()
        elif arguments["<pkgmanager>"] == "pkgsrc":
            from core.miners.ports import mine as pkgsrc_mine

            pkgsrc_mine()
        elif arguments["<pkgmanager>"] == "homebrew":
            from core.miners.homebrew import mine as brew_mine

            brew_mine()

        elif arguments["<pkgmanager>"] == "chromebrew":
            from core.miners.chromebrew import mine as chromebrew_mine

            chromebrew_mine()
        else:
            print(f'No miner for {arguments["<pkgmanager>"]} implemented', file=sys.stderr)
            sys.exit(127)

    elif arguments["release"]:
        from core.common.release_dataset import create_compressed_archive

        create_compressed_archive()
    elif arguments["push"]:
        from core.common.release_dataset import push_dataset_to_zenodo

        push_dataset_to_zenodo(arguments["<dataset>"], sandbox=arguments["--sandbox"])


if __name__ == "__main__":
    main()
