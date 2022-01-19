#!/usr/bin/env bash

poetry run dasea mine alire
poetry run dasea mine conan
poetry run dasea mine fpm
poetry run dasea mine nimble
poetry run dasea mine vcpkg
poetry run dasea mine homebrew

vagrant up freebsd11
bash bin/get_freebsd_ports.sh
vagrant destroy -f freebsd11

vagrant up openbsd69
bash bin/get_openbsd_ports.sh
vagrant destroy -f openbsd69

vagrant up netbsd9
bash bin/get_netbsd_pkgsrc.sh
vagrant destroy -f netbsd9


poetry run dasea release
poetry run dasea push