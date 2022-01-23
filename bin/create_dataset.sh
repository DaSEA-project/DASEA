#!/usr/bin/env bash

# Runs long and remote, start it first?
vagrant up cargominer
bash bin/get_cargo.sh
vagrant destroy -f cargominer

poetry run dasea mine alire

# TODO: Mine on a 2004 or even newer to get the latest gcc version automatically
vagrant up ubuntu1804
vagrant ssh ubuntu1804 --command "cd /vagrant/ && poetry run dasea mine conan"
vagrant destroy -f ubuntu1804

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