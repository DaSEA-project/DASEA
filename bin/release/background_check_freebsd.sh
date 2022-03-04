#! /bin/bash

while ps -p $1 > /dev/null
do
    echo "FreeBDS Miner process is running"
    sleep 5
done
echo "FreeBDS Miner has completed"

contents="$(jq '.freebsd_complete = true' ~/status.json)"
echo -E "${contents}" > ~/status.json
