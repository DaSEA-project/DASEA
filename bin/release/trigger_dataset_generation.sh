
## Create JSON file
sudo apt install jq -y
echo '{"non_vagrant_complete": false, "vagrant_complete": false}' | jq . >> ~/status.json

## Execute in parallel with nohup
bash bin/release/generate_dataset_scripts/non_vagrant_miners.sh &
NON_VAGRANT_MINERS_ID=$!

# nohup bash bin/generate_dataset_scripts/vagrant_miners.sh &

## FreeBSD script... for all Vagrant

# COUNT=0

# nohup sh -c "while ps -p $NON_VAGRANT_MINERS_ID > /dev/null; do echo 'Non Vagrant Miners process is running' && sleep 5; done && $((COUNT++))" &
# put this while in own file so it can be sent to background
while ps -p $NON_VAGRANT_MINERS_ID > /dev/null
do
    echo "Non Vagrant Miners process is running"
    sleep 5
done
contents="$(jq '.non_vagrant_complete = true' ~/status.json)"
echo -E "${contents}" > ~/status.json

# ## Once done, trigger release and push to GitHub
# nohup sh -c "while [ $COUNT -lt 1 ]; do echo 'Mining is still running' && sleep 5; done && bash bin/release/release_dataset.sh" &


## Execute in parallel Vagrant miner

## Create a script to run in the background every 30 min to check if that file has state for all miners -> if done, release and destroy JSON and push to Github
# {
#   non_vagrant: Complete, Failed
# }

echo "trigger_dataset_generation completed..."