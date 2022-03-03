#! /bin/bash

FreeBSD_ID = $1

while ps -p $FreeBSD_ID > /dev/null
do
    echo "FreeBDS Miner process is running"
    sleep 5
done
contents="$(jq '.freebsd_complete = true' ~/status.json)"
echo -E "${contents}" > ~/status.json
