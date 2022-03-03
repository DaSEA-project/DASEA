#! /bin/bash

while ps -p $1 > /dev/null
do
    echo "FreeBDS Miner process is running"
    sleep 5
done
contents="$(jq '.freebsd_complete = true' ~/status.json)"
echo -E "${contents}" > ~/status.json
