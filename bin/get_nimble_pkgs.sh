#!/usr/bin/env bash
vagrant ssh ubuntu2104oneway --command "cd /vagrant/ && poetry run dasea mine nimble"
# Requires the Vagrant SCP plugin to be installed
vagrant scp 'ubuntu2104oneway:/vagrant/data/out/nimble/*packages*.csv' data/out/nimble/
vagrant scp 'ubuntu2104oneway:/vagrant/data/out/nimble/*versions*.csv' data/out/nimble/
vagrant scp 'ubuntu2104oneway:/vagrant/data/out/nimble/*dependencies*.csv' data/out/nimble/
