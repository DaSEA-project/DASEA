## Spin up a DO droplet
doctl compute droplet create --image ubuntu-20-04-x64 --size s-1vcpu-1gb --region ams3 --wait --ssh-keys 33315393 kols-test

## Sleep while the droplet boots up
sleep 45

## Get the droplet's IP address
IP_ADDRESS=$(doctl compute droplet get --format "PublicIPv4" --no-header kols-test)

## Add to the hosts file
echo "Add to the hosts file"
ssh-keyscan -H $IP_ADDRESS >> ~/.ssh/known_hosts


## SSH into the droplet, Execute all miners sequentially, SCP back data to STEVE
echo "SSH into the droplet..."
doctl compute ssh kols-test --ssh-command "
whoami"

echo "Completed..."

## Persist in json file this miner has completed


## Destroy droplet
