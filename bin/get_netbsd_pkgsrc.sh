#!/usr/bin/env bash
vagrant ssh netbsd9 --command "cd /vagrant/ && python -m core.miners.ports"

# The NetBSD VM does not support virtualbox two-way synced folders, therefore manual collection of results
# Requires the Vagrant SCP plugin to be installed
vagrant scp 'netbsd9:/vagrant/data/out/ports/netbsd9/*packages*.csv' data/out/ports/netbsd9/
vagrant scp 'netbsd9:/vagrant/data/out/ports/netbsd9/*versions*.csv' data/out/ports/netbsd9/
vagrant scp 'netbsd9:/vagrant/data/out/ports/netbsd9/*dependencies*.csv' data/out/ports/netbsd9/
