
## Create JSON file
rm ~/status.json
sudo apt install jq -y
echo '{"non_vagrant_complete": false, "freebsd_complete": false, "netbsd_complete": false, "openbsd_complete": false, "nimble_complete": false,"clojars_complete": false, "rubygems_complete": false, "npm_complete": false, "pypi_complete": false}' | jq . >> ~/status.json

# Non-Vagrant Miners
bash bin/release/generate_dataset_scripts/non_vagrant_miners.sh > logs/non_vagrant.out &
NON_VAGRANT_MINERS_ID=$!
bash bin/release/background_check.sh $NON_VAGRANT_MINERS_ID 'Non Vagrant' 'non_vagrant_complete' &

# FreeBSD
bash bin/release/generate_dataset_scripts/freebsd_miner.sh > logs/freebsd.out &
FREEBDS_MINER_ID=$!
bash bin/release/background_check.sh $FREEBDS_MINER_ID 'FreeBSD' 'freebsd_complete' &

# NetBSD
bash bin/release/generate_dataset_scripts/netbsd_miner.sh > logs/netbsd.out &
NETBDS_MINER_ID=$!
bash bin/release/background_check.sh $NETBDS_MINER_ID 'NetBSD' 'netbsd_complete' &

# OpenBSD
bash bin/release/generate_dataset_scripts/openbsd_miner.sh > logs/openbsd.out &
OPENBDS_MINER_ID=$!
bash bin/release/background_check.sh $OPENBDS_MINER_ID 'OpenBSD' 'openbsd_complete' &

# Nimble
bash bin/release/generate_dataset_scripts/nimble_miner.sh > logs/nimble.out &
NIMBLE_MINER_ID=$!
bash bin/release/background_check.sh $NIMBLE_MINER_ID 'Nimble' 'nimble_complete' &

# Clojars
bash bin/release/generate_dataset_scripts/clojars_miner.sh > logs/clojars.out &
CLOJARS_MINER_ID=$!
bash bin/release/background_check.sh $CLOJARS_MINER_ID 'Clojars' 'clojars_complete' &

# RubyGems
bash bin/release/generate_dataset_scripts/rubygems_miner.sh > logs/rubygems.out &
RUBYGEMS_MINER_ID=$!
bash bin/release/background_check.sh $RUBYGEMS_MINER_ID 'RubyGems' 'rubygems_complete' &

# NPM
bash bin/release/generate_dataset_scripts/npm_miner.sh > logs/npm.out &
NPM_MINER_ID=$!
bash bin/release/background_check.sh $NPM_MINER_ID 'NPM' 'npm_complete' &

# # PyPI
# bash bin/release/generate_dataset_scripts/pypi_miner.sh > logs/pypi.out &
# PYPI_MINER_ID=$!
# bash bin/release/background_check.sh $PYPI_MINER_ID 'PyPI' 'pypi_complete' &

# Check all miners are complete
bash bin/release/background_check_completion_status.sh &

echo "trigger_dataset_generation completed..."