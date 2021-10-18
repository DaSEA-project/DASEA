#!/bin/bash

mkdir repo; cd repo
URL=https://github.com/conan-io/conan-center-index

if [ -d src/recipes ]
    then
        echo "Pulled git repository"
        git pull
    else
        echo "Cloned git repository"
        git clone -v $URL src
fi

# End