"""Naval Fate.

Usage:
  dasea mine <pkgmanager>
  dasea release <zenodo_api_key>

Options:
  -h --help     Show this screen.
  --version     Show version.
"""
from docopt import docopt


def main():
    # TODO: Adjust version to what is given in pyproject.toml
    arguments = docopt(__doc__, version="0.1.0")

    # Imports are inlined below to allow for incomplete setups on remote miners
    if arguments["mine"]:
        if arguments["<pkgmanager>"] == "fpm":
            from dasea.fpm import mine as fpm_mine

            fpm_mine()
        elif arguments["<pkgmanager>"] == "conan":
            from dasea.conan import mine as conan_mine

            conan_mine()
        elif arguments["<pkgmanager>"] == "vcpkg":
            from dasea.vcpkg import mine as vcpkg_mine

            vcpkg_mine()
        elif arguments["<pkgmanager>"] == "alire":
            from dasea.alire import mine as alire_mine

            alire_mine()
        elif arguments["<pkgmanager>"] == "maven":
            from dasea.maven import mine as maven_mine

            maven_mine()
        elif arguments["<pkgmanager>"] == "nimble":
            from dasea.nimble import mine as nimble_mine

            nimble_mine()
        elif arguments["<pkgmanager>"] == "apt":
            if arguments["<platform>"] == "ubuntu1804":
                from dasea.apt import mine as apt_mine

                apt_mine(arguments["<platform>"])
        elif arguments["<pkgmanager>"] == "ports":
            from dasea.ports import mine as ports_mine

            ports_mine()
    elif arguments["release"]:
        from dasea.release_dataset import main as release_dataset

        release_dataset(arguments["<zenodo_api_key>"])


if __name__ == "__main__":
    main()
