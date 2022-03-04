#! /bin/bash

while ps -p $1 > /dev/null
do
    echo "Nimble Miner process is running"
    sleep 5
done
echo "Nimble Miner has completed"

contents="$(jq '.nimble_complete = true' ~/status.json)"
echo -E "${contents}" > ~/status.json
