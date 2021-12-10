"""Naval Fate.

Usage:
  dasea mine <ecosystem>
  dasea release <zenodo_api_key>

Options:
  -h --help     Show this screen.
  --version     Show version.
"""
from docopt import docopt
from dasea.fpm import mine as fpm_mine
from dasea.conan import mine as conan_mine
from dasea.vcpkg import mine as vcpkg_mine
from dasea.alire import mine as alire_mine
from dasea.maven import mine as maven_mine
from dasea.nimble import mine as nimble_mine
from dasea.release_dataset import main as release_dataset


def main():
    # TODO: Adjust version to what is given in pyproject.toml
    arguments = docopt(__doc__, version="0.1.0")

    if arguments["mine"]:
        if arguments["<ecosystem>"] == "fpm":
            fpm_mine()
        elif arguments["<ecosystem>"] == "conan":
            conan_mine()
        elif arguments["<ecosystem>"] == "vcpkg":
            vcpkg_mine()
        elif arguments["<ecosystem>"] == "alire":
            alire_mine()
        elif arguments["<ecosystem>"] == "maven":
            maven_mine()
        elif arguments["<ecosystem>"] == "nimble":
            nimble_mine()
    elif arguments["release"]:
        release_dataset(arguments["<zenodo_api_key>"])


if __name__ == "__main__":
    main()
