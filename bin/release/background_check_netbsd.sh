#! /bin/bash

NetBSD_ID = $1

while ps -p $NetBSD_ID > /dev/null
do
    echo "NetBDS Miner process is running"
    sleep 5
done
contents="$(jq '.netbsd_complete = true' ~/status.json)"
echo -E "${contents}" > ~/status.json
