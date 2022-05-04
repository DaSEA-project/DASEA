
## Create JSON file
rm ~/status.json
sudo apt install jq -y
echo '{"non_vagrant_complete": false, "conan_complete": false, "freebsd_complete": false, "netbsd_complete": false, "openbsd_complete": false, "nimble_complete": false,"clojars_complete": false, "rubygems_complete": false, "npm_complete": false, "pypi_complete": true}' | jq . >> ~/status.json

# Non-Vagrant Miners
bash bin/release/generate_dataset_scripts/non_vagrant_miners.sh > non_vagrant.out 2> non_vagrant.out < /dev/null &
NON_VAGRANT_MINERS_ID=$!
bash bin/release/background_check.sh $NON_VAGRANT_MINERS_ID 'Non Vagrant' 'non_vagrant_complete' &

# NetBSD
bash bin/release/generate_dataset_scripts/netbsd_miner.sh > netbsd.out 2> netbsd.out < /dev/null &
NETBDS_MINER_ID=$!
bash bin/release/background_check.sh $NETBDS_MINER_ID 'NetBSD' 'netbsd_complete' &

# FreeBSD
bash bin/release/generate_dataset_scripts/freebsd_miner.sh > freebsd.out 2> freebsd.out < /dev/null &
FREEBDS_MINER_ID=$!
bash bin/release/background_check.sh $FREEBDS_MINER_ID 'FreeBSD' 'freebsd_complete' &

# OpenBSD
bash bin/release/generate_dataset_scripts/openbsd_miner.sh > openbsd.out 2> openbsd.out < /dev/null &
OPENBDS_MINER_ID=$!
bash bin/release/background_check.sh $OPENBDS_MINER_ID 'OpenBSD' 'openbsd_complete' &

# Nimble
bash bin/release/generate_dataset_scripts/nimble_miner.sh > nimble.out 2> nimble.out < /dev/null &
NIMBLE_MINER_ID=$!
bash bin/release/background_check.sh $NIMBLE_MINER_ID 'Nimble' 'nimble_complete' &

# Clojars
bash bin/release/generate_dataset_scripts/clojars_miner.sh > clojars.out 2> clojars.out < /dev/null &
CLOJARS_MINER_ID=$!
bash bin/release/background_check.sh $CLOJARS_MINER_ID 'Clojars' 'clojars_complete' &

# RubyGems
bash bin/release/generate_dataset_scripts/rubygems_miner.sh > rubygems.out 2> rubygems.out < /dev/null &
RUBYGEMS_MINER_ID=$!
bash bin/release/background_check.sh $RUBYGEMS_MINER_ID 'RubyGems' 'rubygems_complete' &

# NPM
bash bin/release/generate_dataset_scripts/npm_miner.sh > npm.out 2> npm.out < /dev/null &
NPM_MINER_ID=$!
bash bin/release/background_check.sh $NPM_MINER_ID 'NPM' 'npm_complete' &

# # PyPI
# bash bin/release/generate_dataset_scripts/pypi_miner.sh > pypi.out 2> pypi.out < /dev/null &
# PYPI_MINER_ID=$!
# bash bin/release/background_check.sh $PYPI_MINER_ID 'PyPI' 'pypi_complete' &

# Check all miners are complete
bash bin/release/background_check_completion_status.sh &

echo "trigger_dataset_generation completed..."