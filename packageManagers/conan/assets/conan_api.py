"""
    Script experimenting with the Conan API to try and extract packages
    Simulating `$ conan search "poco" -r=all > out.txt`
"""

from conans.client.conan_api import Conan

def main():
    # Packages in the conan ecosystem
    ZLIP = "zlib/1.2.11@"
    POCO = "poco/1.9.4@"        # {'error': False, 'results': [{'remote': 'conancenter', 'items': [{'recipe': {'id': 'poco/1.9.4'}}]}]}
    WILD = "po/1.9@"            # Wildcards don't work

    # ConanAPIV1
    conan, _, _ = Conan.factory()
    result = conan.search_recipes(POCO, "all", False) 

    print(result)

if __name__ == "__main__":
    main()