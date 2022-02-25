
## Copy ssh keys into a variable
SSH_KEYS=$(cat ~/.ssh/dasea.pub)
echo $SSH_KEYS

## Spin up a DO droplet
doctl compute droplet create --image 102629764 --size s-4vcpu-8gb --region ams3 --wait --ssh-keys 33315393 DASEA-tool-miner-1

## Get the droplet's IP address
IP_ADDRESS=$(doctl compute droplet get --format "PublicIPv4" --no-header DASEA-tool-miner-1)

## Add to the hosts file
echo "Add to the hosts file"
ssh-keyscan -H $IP_ADDRESS >> ~/.ssh/known_hosts

## Switch identity
echo "Switching identity..."
# exec ssh-agent bash
ssh-add ~/.ssh/dasea

## Copy ssh keys into droplet
echo "Copying SSH keys into droplet..."
scp -i ~/.ssh/dasea ~/.ssh/miner1.pub root@$IP_ADDRESS:/root/.ssh/

## SSH into the droplet
echo "SSH into the droplet..."
doctl compute ssh DASEA-tool-miner-1 --ssh-command -v "source ~/.profile && git clone git@github.com:dependulum/DASEA.git && cd DASEA && poetry install && poetry run dasea mine alire && scp -i ~/.ssh/miner1 -r ./data/out root@157.245.70.200:/root/DASEA/data/out"

echo "Completed..."

## Execute all miners sequentially

## SCP back data to STEVE

## Destroy droplet