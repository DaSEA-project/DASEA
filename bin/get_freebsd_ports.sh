#!/usr/bin/env bash
vagrant ssh freebsd11 --command "cd /vagrant/ && $HOME/.local/bin/poetry run dasea mine ports"
# Requires the Vagrant SCP plugin to be installed
vagrant scp freebsd11:/vagrant/data/out/ports/freebsd11/packages.csv data/out/ports/freebsd11/
vagrant scp freebsd11:/vagrant/data/out/ports/freebsd11/versions.csv data/out/ports/freebsd11/
vagrant scp freebsd11:/vagrant/data/out/ports/freebsd11/dependencies.csv data/out/ports/freebsd11/
