
## Copy ssh keys into a variable
SSH_KEYS=$(cat ~/.ssh/dasea.pub)
echo $SSH_KEYS

## Spin up a DO droplet
doctl compute droplet create --image 102629764 --size s-4vcpu-8gb --region ams3 --wait --ssh-keys 33315393 DASEA-tool-miner-1

## Get the droplet's IP address
IP_ADDRESS=$(doctl compute droplet list --format PublicIPv4Address | grep -v null)

## Add to the hosts file
ssh-keyscan -H $IP_ADDRESS >> ~/.ssh/known_hosts

## Switch identity
exec ssh-agent bash
ssh-add ~/.ssh/dasea

## SSH into the droplet
# doctl compute ssh DASEA-tool-miner-1 --ssh-command "source ~/.profile && git clone https://github.com/dependulum/DASEA.git && cd DASEA && poetry install && poetry run dasea mine alire"

doctl compute ssh DASEA-tool-miner-1 --ssh-command "source ~/.profile && cd DASEA && poetry install && poetry run dasea mine alire && scp -r ./data/out root@157.245.70.200:/root/DASEA/data/out"

## Execute all miners sequentially

## SCP back data to STEVE

## Destroy droplet