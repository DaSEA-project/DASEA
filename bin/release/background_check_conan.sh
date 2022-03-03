#! /bin/bash
echo $1

while ps -p $1 > /dev/null
do
    echo "Conan process is running"
    sleep 900
done
contents="$(jq '.conan_complete = true' ~/status.json)"
echo -E "${contents}" > ~/status.json