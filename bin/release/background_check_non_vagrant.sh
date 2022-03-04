#! /bin/bash
echo $1

while ps -p $1 > /dev/null
do
    echo "Non Vagrant Miners process is running"
    sleep 5
done
echo "Non Vagrant Miner has completed"

contents="$(jq '.non_vagrant_complete = true' ~/status.json)"
echo -E "${contents}" > ~/status.json
