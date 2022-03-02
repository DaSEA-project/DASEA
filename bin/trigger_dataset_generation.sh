
## Create JSON file

## Execute in parallel with nohup
nohup bash bin/generate_dataset_scripts/non_vagrant_miners.sh &
# NON_VAGRANT_MINERS_ID=$!

## FreeBSD script... for all Vagrant

# COUNT=0

# Destroy all machines
# nohup sh -c "while ps -p $NON_VAGRANT_MINERS_ID > /dev/null; do echo 'Non Vagrant Miners process is running' && sleep 5; done && $((COUNT++))" &

# ## Once done, trigger release and push to GitHub
# nohup sh -c "while [ $COUNT -lt 1 ]; do echo 'Mining is still running' && sleep 5; done && bash bin/release_dataset.sh" &

##### Script:

## Create JSON file

## Execute in parallel with nohup
nohup bash bin/generate_dataset_scripts/non_vagrant_miners.sh &

## Execute in parallel Vagrant miner

## Create a script to run in the background every 30 min to check if that file has state for all miners -> if done, release and destroy JSON and push to Github
# {
#   non_vagrant: Complete, Failed
# }
