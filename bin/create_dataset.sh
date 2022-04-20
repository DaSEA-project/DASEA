#!/usr/bin/env bash

poetry run dasea mine cargo
poetry run dasea mine alire
poetry run dasea mine fpm
poetry run dasea mine vcpkg
poetry run dasea mine homebrew
poetry run dasea mine chromebrew
poetry run dasea mine npm # takes very long time
poetry run dasea mine pypi # takes very long time
poetry run dasea mine clojars
poetry run dasea mine rubygems # takes very long time
poetry run dasea mine conan

vagrant up freebsd11
bash bin/get_freebsd_ports.sh
vagrant destroy -f freebsd11

vagrant up openbsd69
bash bin/get_openbsd_ports.sh
vagrant destroy -f openbsd69

vagrant up netbsd9
bash bin/get_netbsd_pkgsrc.sh # Takes a really long time, 2-3h
vagrant destroy -f netbsd9

vagrant up ubuntu2104oneway
bash bin/get_nimble_pkgs.sh
vagrant destroy -f ubuntu2104oneway
