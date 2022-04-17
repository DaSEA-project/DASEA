
## Create JSON file
rm ~/status.json
sudo apt install jq -y
echo '{"non_vagrant_complete": false, "conan_complete": false, "freebsd_complete": false, "netbsd_complete": false, "openbsd_complete": false, "nimble_complete": false,"clojars_complete": false}, "rubygems_complete": false, "npm_complete": false, "pypi_complete": false}' | jq . >> ~/status.json

# Non-Vagrant Miners
bash bin/release/generate_dataset_scripts/non_vagrant_miners.sh &
NON_VAGRANT_MINERS_ID=$!
bash bin/release/background_check.sh $NON_VAGRANT_MINERS_ID 'Non Vagrant' 'non_vagrant_complete' &

# NetBSD
bash bin/release/generate_dataset_scripts/netbsd_miner.sh &
NETBDS_MINER_ID=$!
bash bin/release/background_check.sh $NETBDS_MINER_ID 'NetBSD' 'netbsd_complete' &

# Conan Miner
bash bin/release/generate_dataset_scripts/conan_miner.sh &
CONAN_MINER_ID=$!
bash bin/release/background_check.sh $CONAN_MINER_ID 'Conan' 'conan_complete' &

# FreeBSD
bash bin/release/generate_dataset_scripts/freebsd_miner.sh &
FREEBDS_MINER_ID=$!
bash bin/release/background_check.sh $FREEBDS_MINER_ID 'FreeBSD' 'freebsd_complete' &

# OpenBSD
bash bin/release/generate_dataset_scripts/openbsd_miner.sh &
OPENBDS_MINER_ID=$!
bash bin/release/background_check.sh $OPENBDS_MINER_ID 'OpenBSD' 'openbsd_complete' &

# Nimble
bash bin/release/generate_dataset_scripts/nimble_miner.sh &
NIMBLE_MINER_ID=$!
bash bin/release/background_check.sh $NIMBLE_MINER_ID 'Nimble' 'nimble_complete' &

# Clojars
bash bin/release/generate_dataset_scripts/clojars_miner.sh &
CLOJARS_MINER_ID=$!
bash bin/release/background_check.sh $CLOJARS_MINER_ID 'Clojars' 'clojars_complete' &

# RubyGems
bash bin/release/generate_dataset_scripts/rubygems_miner.sh &
RUBYGEMS_MINER_ID=$!
bash bin/release/background_check.sh $RUBYGEMS_MINER_ID 'RubyGems' 'rubygems_complete' &

# NPM
bash bin/release/generate_dataset_scripts/npm_miner.sh &
NPM_MINER_ID=$!
bash bin/release/background_check.sh $NPM_MINER_ID 'NPM' 'npm_complete' &

# NPM
bash bin/release/generate_dataset_scripts/pypi_miner.sh &
PYPI_MINER_ID=$!
bash bin/release/background_check.sh $PYPI_MINER_ID 'PyPi' 'pypi_complete' &

# Check all miners are complete
bash bin/release/background_check_completion_status.sh &

echo "trigger_dataset_generation completed..."