#!/usr/bin/env bash

vagrant ssh cargominer --command "cd /vagrant/ && nohup poetry run dasea mine cargo > /tmp/cargo.log 2>&1 &"

remote_ip=`vagrant ssh cargominer --command "hostname -I | cut -d' ' -f1" | head -1`
remote_url=`python -c "print('http://${remote_ip//[$'\t\r\n ']}:8080/done')"`

#TODO: Make this script run in background to not block other mining tasks?
# Mining Cargo takes currently around a day...
while true
do
    is_done=`curl -s -o /dev/null -I -w "%{http_code}" ${remote_url}`
    if [ ${is_done} == '404' ]
    then
        echo 'I will try again in an hour'
        sleep 3600
    elif [ ${is_done} == '200' ]
    then
        cd data/out/cargo/
        while IFS= read -r line
        do
            curl -O ${line}
        done < <(curl -s ${remote_url})
        cd -
        break
    else
        # Should never happen???
        echo "Got ${is_done} error code..."
        sleep 3600
    fi   
done
