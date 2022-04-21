"""DaSEA - Dataset for Software Ecosystem Analysis.

A tool to mine dependency networks from various software ecosystems.

Usage:
  dasea mine <pkgmanager>
  dasea release
  dasea push [--sandbox] [--no-verify] <dataset>

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
            from dasea.miners.fpm import mine as fpm_mine

            fpm_mine()
        elif arguments["<pkgmanager>"] == "conan":
            from dasea.miners.conan import mine as conan_mine

            conan_mine()
        elif arguments["<pkgmanager>"] == "cargo":
            from dasea.miners.cargo import mine as cargo_mine

            cargo_mine()
        elif arguments["<pkgmanager>"] == "vcpkg":
            from dasea.miners.vcpkg import mine as vcpkg_mine

            vcpkg_mine()
        elif arguments["<pkgmanager>"] == "alire":
            from dasea.miners.alire import mine as alire_mine

            alire_mine()
        # elif arguments["<pkgmanager>"] == "maven":
        #     from dasea.miners.maven import mine as maven_mine

        #     maven_mine()
        elif arguments["<pkgmanager>"] == "nimble":
            from dasea.miners.nimble import mine as nimble_mine

            nimble_mine()
        # elif arguments["<pkgmanager>"] == "apt":
        #     from dasea.miners.apt import mine as apt_mine

        #     apt_mine()
        elif arguments["<pkgmanager>"] == "ports":
            from dasea.miners.ports import mine as ports_mine

            ports_mine()
        # elif arguments["<pkgmanager>"] == "pkgsrc":
        #     from dasea.miners.ports import mine as pkgsrc_mine

        #     pkgsrc_mine()
        elif arguments["<pkgmanager>"] == "homebrew":
            from dasea.miners.homebrew import mine as brew_mine

            brew_mine()
        elif arguments["<pkgmanager>"] == "chromebrew":
            from dasea.miners.chromebrew import mine as chromebrew_mine

            chromebrew_mine()
        elif arguments["<pkgmanager>"] == "npm":
            from dasea.miners.npm import mine as npm_mine

            npm_mine()
        elif arguments["<pkgmanager>"] == "clojars":
            from dasea.miners.clojars import mine as clojars_mine

            clojars_mine()
        elif arguments["<pkgmanager>"] == "rubygems":
            from dasea.miners.rubygems import mine as rubygems_mine

            rubygems_mine()
        elif arguments["<pkgmanager>"] == "pypi":
            from dasea.miners.pypi import mine as pypi_mine

            pypi_mine()
        elif arguments["<pkgmanager>"] == "luarocks":
            from dasea.miners.luarocks import mine as luarocks_mine

            luarocks_mine()
        else:
            print(f'No miner for {arguments["<pkgmanager>"]} implemented', file=sys.stderr)
            sys.exit(127)

    elif arguments["release"]:
        from dasea.common.release_dataset import create_compressed_archive

        create_compressed_archive()
    elif arguments["push"]:
        from dasea.common.release_dataset import push_dataset_to_zenodo

        push_dataset_to_zenodo(arguments["<dataset>"], sandbox=arguments["--sandbox"], no_verify=arguments["--no-verify"])

if __name__ == "__main__":
    main()
