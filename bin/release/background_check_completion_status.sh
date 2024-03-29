filepath='~/status.json'

while [ $(cat ~/status.json | jq '.non_vagrant_complete') == false ] || [ $(cat ~/status.json | jq '.freebsd_complete') == false ] || [ $(cat ~/status.json | jq '.netbsd_complete') == false ] || [ $(cat ~/status.json | jq '.openbsd_complete') == false ] || [ $(cat ~/status.json | jq '.nimble_complete') == false ] || [ $(cat ~/status.json | jq '.rubygems_complete') == false ] || [ $(cat ~/status.json | jq '.clojars_complete') == false ] || [ $(cat ~/status.json | jq '.npm_complete') == false ]
do
    echo "Miners processes still running"
    sleep 900
done
echo "All tasks complete"

# release dataset
echo "Releasing dataset"
bash bin/release/release_dataset.sh

# push to github
echo "Pushing to GitHub"
git config --global user.email "daseaITU@gmail.com"
git config --global user.name "daseaOrg"
git add homepage/datasets.json
git commit -m "DaSEA release - $(date)"
git push origin main

# delete DASEA folder
# echo "Deleting DaSEA folder"
# cd ..
# rm -rf ~/DASEA
