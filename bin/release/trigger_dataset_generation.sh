
## Create JSON file
rm ~/status.json
sudo apt install jq -y
echo '{"non_vagrant_complete": false, "conan_complete": false, "freebsd_complete": false, "netbsd_complete": false, "openbsd_complete": false, "nimble_complete": false}' | jq . >> ~/status.json

# Non-Vagrant Miners
bash bin/release/generate_dataset_scripts/non_vagrant_miners.sh &
NON_VAGRANT_MINERS_ID=$!

bash bin/release/background_check_non_vagrant.sh $NON_VAGRANT_MINERS_ID &

# Conan Miner
bash bin/release/generate_dataset_scripts/conan_miner.sh &
CONAN_MINER_ID=$!
bash bin/release/background_check_conan.sh $CONAN_MINER_ID &

# FreeBSD
bash bin/release/generate_dataset_scripts/freebsd_miner.sh &
FREEBDS_MINER_ID=$!
bash bin/release/background_check_freebsd.sh $FREEBDS_MINER_ID &

# NetBSD
bash bin/release/generate_dataset_scripts/netbsd_miner.sh &
NETBDS_MINER_ID=$!
bash bin/release/background_check_netbsd.sh $NETBDS_MINER_ID &

# OpenBSD
bash bin/release/generate_dataset_scripts/openbsd_miner.sh &
OPENBDS_MINER_ID=$!
bash bin/release/background_check_openbsd.sh $OPENBDS_MINER_ID &

# Nimble
bash bin/release/generate_dataset_scripts/nimble_miner.sh &
NIMBLE_MINER_ID=$!
bash bin/release/background_check_nimble.sh $NIMBLE_MINER_ID &

# Check all miners are complete
bash bin/release/background_check_completion_status.sh &

echo "trigger_dataset_generation completed..."