
## Apt update and upgrade
sudo apt update -y

## Install Python
sudo apt install python3.9

## Install Pip
sudo apt install python3-pip

## Install Virtualenv
sudo pip3 install virtualenv

##  Make a folder for virtual enviornments
mkdir env

## Install Poetry
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -

## Source profile
source ~/.profile

## Create virtual enviornment
virtualenv --python=/usr/bin/python3.9 env/dasea

## Activate the virtual enviornment
source env/dasea/bin/activate

## TODO: Install virtualbox

## Enter dasea project
cd dasea-tool

## Install dependencies
poetry install
