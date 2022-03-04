#! /bin/bash

while ps -p $1 > /dev/null
do
    echo "OpenBDS Miner process is running"
    sleep 5
done
echo "OpenBDS Miner has completed"

contents="$(jq '.openbsd_complete = true' ~/status.json)"
echo -E "${contents}" > ~/status.json
