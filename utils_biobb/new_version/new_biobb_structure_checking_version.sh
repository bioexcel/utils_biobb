#!/usr/bin/env bash

#Usage: ./new_py_version.sh
#Activate conda
ide=atom
path_user=/Users/pau/
path_biobb=/Users/pau/projects/
path_json_schemas=/Users/pau/projects/utils_biobb/utils_biobb/json/
conda=biobb
echo "******************************************************"
echo "Be sure of having activated $conda conda environment!"
echo "******************************************************"
read -p "Repository name ie biobb_md : " REPOSITORY
read -p "Version number ie 0.1.2 : " version
read -p "Commit message ie 2019.4 : " message
echo "Repository: $REPOSITORY"
echo "Version: $version"
echo "Message: $message"
read -p "Add new version number to CHANGELOG and constants.py Press any key to continue..." -n1 -s
echo ""
$ide /Users/pau/projects/biobb_structure_checking/biobb_structure_checking/constants.py /Users/pau/projects/biobb_structure_checking/CHANGELOG.md
read -p "Before opening setup.py remember to check if some dependency has changed. Press any key to continue..." -n1 -s
echo ""
$ide $path_biobb$REPOSITORY/setup.py
read -p "Modify setup.py with the new version number and press any key..." -n1 -s
echo ""
$ide $path_biobb$REPOSITORY/README.md
read -p "Modify README.md with the new version number (in version and instructions) and press any key..." -n1 -s
echo ""
$ide $path_biobb$REPOSITORY/$REPOSITORY/docs/source/conf.py
read -p "Modify conf.py with the new version number..." -n1 -s
echo ""
$ide $path_biobb$REPOSITORY/$REPOSITORY/docs/source/changelog.md
read -p "Modify changelog.md with the new version..." -n1 -s
echo ""
$ide $path_biobb$REPOSITORY/$REPOSITORY/docs/source/schema.html
read -p "Modify schema.html with the new version number..." -n1 -s
echo ""
cd $path_biobb$REPOSITORY
cp -v $path_biobb$REPOSITORY/README.md $path_biobb$REPOSITORY/$REPOSITORY/docs/source/readme.md
git status
git add .
git commit -m "$message"
git push
git tag -a v$version -m "$message"
git push origin v$version
python3 setup.py sdist bdist_wheel; python3 -m twine upload dist/* <<< andriopau
rm -rfv $REPOSITORY.egg-info dist build

# Conda skeleton
# rm -rf $path_user$REPOSITORY 2> /dev/null
# retval=1
# while [ $retval -ne 0 ]
# do
#   echo "Sleeping for 5 seconds..."
#   sleep 5
#   cd ~; conda skeleton pypi $REPOSITORY --version $version
#   retval=$?
# done
# $ide $path_user$REPOSITORY/meta.yaml
# read -p "Copy the headers (lines that starts with {%) from  ~/$REPOSITORY/meta.yaml and press any key..." -n1 -s
# echo ""


# https://pypi.org/project/biobb-structure-checking/#copy-hash-modal-735762e9-48f7-451f-8481-ce6f4981b9bc
read -p "Copy the hash of the tgz file and press any key..." -n1 -s
open https://pypi.org/project/$REPOSITORY
#Bioconda
cd ${path_biobb}bioconda-recipes/
git checkout -f master; git pull origin master
git branch -D $REPOSITORY; git push origin --delete $REPOSITORY; git checkout -b $REPOSITORY
$ide ${path_biobb}bioconda-recipes/recipes/$REPOSITORY
read -p "Modify recipes/$REPOSITORY/build.sh and press any key..." -n1 -s
echo ""
read -p "Modify recipes/$REPOSITORY/meta.yaml paste the headers and check if some dependency has changed from ~/$REPOSITORY/meta.yaml and press any key..." -n1 -s
echo ""
git status; git add recipes/$REPOSITORY/*
git commit -m "$message"
git push -u origin $REPOSITORY
# open in chrome
#google-chrome https://github.com/bioconda/bioconda-recipes/pull/new/$REPOSITORY
# open in safari
open https://github.com/bioconda/bioconda-recipes/pull/new/$REPOSITORY
