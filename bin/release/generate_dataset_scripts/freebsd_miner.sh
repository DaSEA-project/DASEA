## Spin up a DO droplet
doctl compute droplet create --image 102629764 --size s-4vcpu-8gb --region ams3 --wait --ssh-keys 33315393 DASEA-tool-freeBSD-miner

## Sleep while the droplet boots up
sleep 45

## Get the droplet's IP address
IP_ADDRESS=$(doctl compute droplet get --format "PublicIPv4" --no-header DASEA-tool-freeBSD-miner)

## Add to the hosts file
echo "Add to the hosts file"
ssh-keyscan -H $IP_ADDRESS >> ~/.ssh/known_hosts

## Copy ssh keys into droplet
echo "Copying SSH keys into droplet..."
scp -i ~/.ssh/dasea ~/.ssh/id_rsa root@$IP_ADDRESS:/root/.ssh/

## SSH into the droplet, Execute all miners sequentially, SCP back data to STEVE
echo "SSH into the droplet..."
doctl compute ssh DASEA-tool-freeBSD-miner --ssh-key-path ~/.ssh/dasea --ssh-command "
ssh-keyscan -H 157.245.70.200 >> ~/.ssh/known_hosts &&
source ~/.profile && git clone https://github.com/DaSEA-project/DASEA.git &&
cd DASEA && poetry install &&
vagrant up freebsd11
bash bin/get_freebsd_ports.sh
vagrant destroy -f freebsd11
scp -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa -r ./data/out/ports/freebsd11 root@steve.dasea.org:/root/DASEA/data/out/ports"

## Destroy droplet
echo "Destroying droplet..."
doctl compute droplet delete DASEA-tool-freeBSD-miner --force

echo "Completed FreeBDS Miner"
