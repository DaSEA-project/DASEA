## Spin up a DO droplet
doctl compute droplet create --image 102629764 --size s-4vcpu-8gb --region ams3 --wait --ssh-keys 33315393 DASEA-tool-clojars-miner

## Sleep while the droplet boots up
sleep 45

## Get the droplet's IP address
IP_ADDRESS=$(doctl compute droplet get --format "PublicIPv4" --no-header DASEA-tool-clojars-miner)

## Add to the hosts file
echo "Add to the hosts file"
ssh-keyscan -H $IP_ADDRESS >> ~/.ssh/known_hosts

## Copy ssh keys into droplet
echo "Copying SSH keys into droplet..."
scp -i ~/.ssh/dasea ~/.ssh/id_rsa root@$IP_ADDRESS:/root/.ssh/

## SSH into the droplet, Execute Clojars miner, SCP back data to STEVE
echo "SSH into the droplet..."
doctl compute ssh DASEA-tool-clojars-miner --ssh-key-path ~/.ssh/dasea --ssh-command "
ssh-keyscan -H 157.245.70.200 >> ~/.ssh/known_hosts &&
source ~/.profile && git clone https://github.com/dependulum/DASEA.git &&
cd DASEA && poetry install &&
poetry run dasea mine clojars &&
scp -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa -r ./data/out root@steve.dasea.org:/root/DASEA/data"

## Destroy droplet
echo "Destroying droplet..."
doctl compute droplet delete DASEA-tool-clojars-miner --force

echo "Completed Clojars Miner"
