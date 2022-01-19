#!/usr/bin/env bash
vagrant ssh openbsd69 --command 'cd /vagrant/ && $HOME/.local/bin/poetry run dasea mine ports'
# The OpenBSD VM does not support virtualbox two-way synced folders, therefore manual collection of results
# Requires the Vagrant SCP plugin to be installed
vagrant scp 'openbsd69:/vagrant/data/out/ports/openbsd69/*packages*.csv' data/out/ports/openbsd69/
vagrant scp 'openbsd69:/vagrant/data/out/ports/openbsd69/*versions*.csv' data/out/ports/openbsd69/
vagrant scp 'openbsd69:/vagrant/data/out/ports/openbsd69/*dependencies*.csv' data/out/ports/openbsd69/
