#! /bin/bash

## Argument explanation
# $1: ID of background process
# $2: Miner name
# $3: Status variable in JSON

echo $1

while ps -p $1 > /dev/null
do
    echo "$2 process is running"
    sleep 900
done
echo "$2 Miner has completed"

contents="$(jq '.'$3' = true' ~/status.json)"
echo -E "${contents}" > ~/status.json
