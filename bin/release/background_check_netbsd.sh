#! /bin/bash

while ps -p $1 > /dev/null
do
    echo "NetBDS Miner process is running"
    sleep 5
done
contents="$(jq '.netbsd_complete = true' ~/status.json)"
echo -E "${contents}" > ~/status.json
