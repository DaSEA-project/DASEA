import apt
import csv
import sys


def _get_pkg_names(fname):
    with open(fname) as fp:
        csv_reader = csv.reader(fp)
        next(csv_reader)
        
        pkg_names = [row[1] for row in csv_reader]

    return pkg_names


def main(fname):
    # fname = "data/out/ubuntu/packages.csv"
    pkg_names = _get_pkg_names(fname)

    c = apt.Cache()
    for p in pkg_names:
        # not all packages seem to be in the cache. For example `python3-pexpect` is in there but `python3-pexpect:i386` is not
        apt_pkg = c.get(p, None)
        break

        if not apt_pkg:
            continue

        for v in apt_pkg.versions:



    apt_pkg.PackageRecords(apt_pkg.Cache())

if __name__ == '__main__':
    main()