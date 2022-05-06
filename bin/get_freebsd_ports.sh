#!/usr/bin/env bash
vagrant ssh freebsd12 --command 'cd /vagrant/ && $HOME/.local/bin/poetry run dasea mine ports'
# Requires the Vagrant SCP plugin to be installed
vagrant scp 'freebsd12:/vagrant/data/out/ports/freebsd12/*packages*.csv' data/out/ports/freebsd12/
vagrant scp 'freebsd12:/vagrant/data/out/ports/freebsd12/*versions*.csv' data/out/ports/freebsd12/
vagrant scp 'freebsd12:/vagrant/data/out/ports/freebsd12/*dependencies*.csv' data/out/ports/freebsd12/
