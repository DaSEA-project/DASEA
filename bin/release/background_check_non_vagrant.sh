#! /bin/bash

# NON_VAGRANT_MINERS_ID=$1
echo $1

while ps -p $1 > /dev/null
do
    echo "Non Vagrant Miners process is running"
    sleep 5
done
contents="$(jq '.non_vagrant_complete = true' ~/status.json)"
echo -E "${contents}" > ~/status.json
