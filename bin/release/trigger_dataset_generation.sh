
## Create JSON file
rm ~/status.json
sudo apt install jq -y
echo '{"non_vagrant_complete": false, "vagrant_complete": false}' | jq . >> ~/status.json

## Execute in parallel with nohup
bash bin/release/generate_dataset_scripts/non_vagrant_miners.sh &
NON_VAGRANT_MINERS_ID=$!

# put this while in own file so it can be sent to background
bash bin/release/background_check_non_vagrant.sh $NON_VAGRANT_MINERS_ID &

bash bin/release/background_check_completion_status.sh # &

echo "trigger_dataset_generation completed..."