#!/usr/bin/env bash

#Usage: ./new_conda_version.sh
#Activate conda
ide=code
path_user=/Users/pau/
path_biobb=/Users/pau/projects/
path_json_schemas=/Users/pau/projecs/projects/utils_biobb/utils_biobb/json/
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
read -p "Do you want to run tests for this repository [Y/n]? " test
if [ $test == 'y' -o $test == 'Y'  ]
then
	nosetests -s $path_biobb$REPOSITORY/$REPOSITORY/test/unitests
fi
read -p "Do you want to generate json schemas for this repository [Y/n]? " json_schemas
if [ $json_schemas == 'y' -o $json_schemas == 'Y'  ]
then
	python3 ${path_json_schemas}json_generator.py -p $REPOSITORY -o $path_biobb$REPOSITORY/$REPOSITORY
fi

read -p "Before opening setup.py remember to check if some dependency has changed. Press any key to continue..." -n1 -s
echo ""
$ide $path_biobb$REPOSITORY/setup.py
read -p "Modify setup.py with the new version number and press any key..." -n1 -s
echo ""
$ide $path_biobb$REPOSITORY/.github/env.yaml
read -p "Modify env.yaml with the new dependencies versions and press any key..." -n1 -s
echo ""
$ide $path_biobb$REPOSITORY/$REPOSITORY/__init__.py
read -p "Modify __init__.py adding the new version number: __version__ = \"$version\"" -n1 -s
echo ""
$ide $path_biobb$REPOSITORY/README.md
read -p "Modify README.md with the new version number (in version and instructions) and press any key..." -n1 -s
echo ""
$ide $path_biobb$REPOSITORY/$REPOSITORY/json_schemas/$REPOSITORY.json
read -p "Modify $REPOSITORY.json with the new version number and the check if some dependency has changed..." -n1 -s
echo ""
$ide $path_biobb$REPOSITORY/$REPOSITORY/docs/source/conf.py
read -p "Modify conf.py with the new version number..." -n1 -s
echo ""
$ide $path_biobb$REPOSITORY/$REPOSITORY/docs/source/change_log.md
read -p "Modify change_log.md with the new version..." -n1 -s
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

read -p "Copy the sha256 hash of the tgz file and press any key..." -n1 -s
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
git commit -m "[$REPOSITORY] update $version"
git push -u origin $REPOSITORY
# open in chrome
# google-chrome https://github.com/bioconda/bioconda-recipes/pull/new/$REPOSITORY
# open in safari
open https://github.com/bioconda/bioconda-recipes/pull/new/$REPOSITORY
