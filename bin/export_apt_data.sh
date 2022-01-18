#!/usr/bin/env bash

# Exporting all the package records takes quite some time!!! (Multiple hours)

mkdir -p $HOME/pkginfo/bin/
mkdir -p $HOME/pkginfo/src/

# The process parallelization pattern comes from this SO entry:
# https://unix.stackexchange.com/questions/103920/parallelize-a-bash-for-loop
NOPROCS=4

# Skip the header line
tail -n +2 data/out/ubuntu/packages.csv | \
# Get only the package names
cut -d"," -f2,5 | \
while read line 
do
    ((i=i%NOPROCS)); ((i++==0)) && wait
    
    IFS=, read pkgname virtual <<< $line
    if [ "$virtual" = "False" ]; then
        # Only ask apt-cache for non-virtual packages
        if [ ! -f $HOME/pkginfo/bin/$pkgname ]; then
            apt-cache show $pkgname > $HOME/pkginfo/bin/$pkgname &
        fi
        if [ ! -f $HOME/pkginfo/bin/$pkgname ]; then
            apt-cache showsrc $pkgname > $HOME/pkginfo/src/$pkgname &
        fi
    fi

done