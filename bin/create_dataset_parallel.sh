#!/usr/bin/env bash

# poetry run dasea mine cargo
# poetry run dasea mine alire
# poetry run dasea mine fpm
# poetry run dasea mine vcpkg
# poetry run dasea mine homebrew
# poetry run dasea mine chromebrew

#vagrant up ubuntu2104
#vagrant up freebsd11
# vagrant up openbsd69
# vagrant up netbsd9
# vagrant up ubuntu2104oneway


# nohup vagrant ssh ubuntu2104 --command "cd /vagrant/ && poetry run dasea mine conan" &
# nohup bash bin/get_freebsd_ports.sh &

nohup poetry run dasea mine cargo &
CARGO_ID=$!
echo $CARGO_ID
nohup poetry run dasea mine alire &
ALIRE_ID=$!
echo $ALIRE_ID

# nohup sh -c 'while ps -p $CARGO_ID > /dev/null; echo "Process is running"; do sleep 10; done && mv $1 $1_done' vagrant destroy -f ubuntu2104 &
#nohup sh -c 'while ps -p $1 > /dev/null; do sleep 10; done && mv $2 $2_done' vagrant destroy -f freebsd11 &


# vagrant destroy -f ubuntu2104
# vagrant destroy -f freebsd11

# vagrant up ubuntu2104
# vagrant ssh ubuntu2104 --command "cd /vagrant/ && poetry run dasea mine conan"
# vagrant destroy -f ubuntu2104


# vagrant up freebsd11
# bash bin/get_freebsd_ports.sh
# vagrant destroy -f freebsd11

# vagrant up openbsd69
# # bash bin/get_openbsd_ports.sh
# vagrant destroy -f openbsd69

# # vagrant up netbsd9
# bash bin/get_netbsd_pkgsrc.sh # Takes a really long time, 2-3h
# vagrant destroy -f netbsd9

# # vagrant up ubuntu2104oneway
# bash bin/get_nimble_pkgs.sh
# vagrant destroy -f ubuntu2104oneway
