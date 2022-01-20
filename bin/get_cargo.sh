#!/usr/bin/env bash
vagrant ssh cargominer --command "cd /vagrant/ && nohup poetry run dasea mine cargo > /tmp/cargo.log 2>&1 &"
#TODO: Add something that checks every hour if data was completely created and first then copy files

# Requires the Vagrant SCP plugin to be installed
vagrant scp 'cargominer:/vagrant/data/out/cargo/*packages*.csv' data/out/cargo/
vagrant scp 'cargominer:/vagrant/data/out/cargo/*versions*.csv' data/out/cargo/
vagrant scp 'cargominer:/vagrant/data/out/cargo/*dependencies*.csv' data/out/cargo/
