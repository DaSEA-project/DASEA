filepath='~/status.json'

non_vagrant=$(cat ~/status.json | jq '.non_vagrant_complete')
echo $non_vagrant

# freebds=$(cat ~/status.json | jq '.free_bds_complete')
# echo $freebds

while [ $(cat ~/status.json | jq '.non_vagrant_complete') = false ]
do
    echo "Miners processes still running"
    sleep 50
done
echo "All tasks complete"

# release dataset
echo "Releasing dataset"
bash bin/release/release_dataset.sh

# push to github
echo "Pushing to GitHub"
git config --global user.email "daseaITU@gmail.com"
git config --global user.name "daseaOrg"
git checkout gh-pages
git add .
git commit -m "DaSEA release - $(date)"
git push

# delete DASEA folder
echo "Deleting DASEA folder"
rm -rf DASEA
