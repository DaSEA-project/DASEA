# Steve setup

## Install doct

https://docs.digitalocean.com/reference/doctl/how-to/install/

## Clone DASEA

git clone https://github.com/dependulum/DASEA.git

## Setup SHH key for doctl

### Copy ssh keys into a variable

SSH_KEY=$(cat ~/.ssh/id_rsa.pub)
echo $SSH_KEY

### Add SHH key to doctl

doctl compute ssh-key create steve_id_rsa_ssh_key --public-key "$(echo $SSH_KEY)"
