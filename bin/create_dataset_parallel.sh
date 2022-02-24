#!/usr/bin/env bash

# Run miners that run quicker
poetry run dasea mine alire
poetry run dasea mine cargo
poetry run dasea mine chromebrew
poetry run dasea mine fpm
poetry run dasea mine homebrew
poetry run dasea mine vcpkg

# Spin up all vagrant machines
vagrant up ubuntu2104
vagrant up freebsd11
vagrant up openbsd69
vagrant up netbsd9
vagrant up ubuntu2104oneway

# Run all processes in parallel
nohup vagrant ssh ubuntu2104 --command "cd /vagrant/ && poetry run dasea mine conan" &
CONAN_ID=$!

nohup bash bin/get_freebsd_ports.sh &
FREEBSD_ID=$!

nohup bash bin/get_openbsd_ports.sh &
OPENBSD_ID=$!

nohup bash bin/get_netbsd_ports.sh &
NETBSD_ID=$!

nohup bash bin/get_nimble_pkgs.sh
NIMBLE_ID=$!

COUNT=0

# Destroy all machines
nohup sh -c 'while ps -p $CONAN_ID > /dev/null; do echo "Conan process is running" && sleep 300; done && $COUNT++ && vagrant destroy -f ubuntu2104'
nohup sh -c 'while ps -p $FREEBSD_ID > /dev/null; do echo "FreeBSD process is running" && sleep 300; done && $COUNT++ &&  vagrant destroy -f freebsd11'
nohup sh -c 'while ps -p $OPENBSD_ID > /dev/null; do echo "OpenBSD process is running" && sleep 300; done && $COUNT++ &&  vagrant destroy -f openbsd69'
nohup sh -c 'while ps -p $NETBSD_ID > /dev/null; do echo "NetBSD process is running" && sleep 300; done && $COUNT++ &&  vagrant destroy -f netbsd9'
nohup sh -c 'while ps -p $NIMBLE_ID > /dev/null; do echo "Nimble process is running" && sleep 300; done && $COUNT++ &&  vagrant destroy -f ubuntu2104oneway'

# Check if mining is still running
while [ $COUNT -lt 5 ]; do
    echo "Waiting for all machines to be destroyed"
    sleep 3000
done

# Trigger release dataset
bash bin/release_dataset.sh

# Push to main repo