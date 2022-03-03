## Spin up a DO droplet
doctl compute droplet create --image 102629764 --size s-4vcpu-8gb --region ams3 --wait --ssh-keys 33315393 DASEA-tool-miner-1

## Sleep while the droplet boots up
sleep 45

## Get the droplet's IP address
IP_ADDRESS=$(doctl compute droplet get --format "PublicIPv4" --no-header DASEA-tool-miner-1)

## Add to the hosts file
echo "Add to the hosts file"
ssh-keyscan -H $IP_ADDRESS >> ~/.ssh/known_hosts

## Switch identity
# echo "Switching identity..."
# exec ssh-agent bash
# ssh-add ~/.ssh/id_rsa

## Copy ssh keys into droplet
echo "Copying SSH keys into droplet..."
# scp -i ~/.ssh/id_rsa ~/.ssh/miner1.pub root@$IP_ADDRESS:/root/.ssh/
scp -i ~/.ssh/dasea ~/.ssh/id_rsa root@$IP_ADDRESS:/root/.ssh/


## SSH into the droplet, Execute all miners sequentially, SCP back data to STEVE
echo "SSH into the droplet..."
doctl compute ssh DASEA-tool-miner-1 --ssh-key-path ~/.ssh/dasea --ssh-command "
ssh-keyscan -H 157.245.70.200 >> ~/.ssh/known_hosts &&
source ~/.profile && git clone https://github.com/dependulum/DASEA.git &&
cd DASEA && poetry install &&
poetry run dasea mine alire &&
scp -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa -r ./data/out root@steve.dasea.org:/root/DASEA/data"

## Destroy droplet
echo "Destroying droplet..."
doctl compute droplet delete DASEA-tool-miner-1 --force

echo "Completed..."
