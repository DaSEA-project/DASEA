filepath='~/status.json'

while [ $(cat ~/status.json | jq '.non_vagrant_complete') == false ] || [ $(cat ~/status.json | jq '.conan_complete') == false ]
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
git add .
git commit -m "DaSEA release - $(date)"
git push origin main

# delete DASEA folder
echo "Deleting DASEA folder"
rm -rf DASEA
