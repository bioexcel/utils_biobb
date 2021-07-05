# Change directory to CMIP
cd /Users/pau/projects/CMIP/
# Activate environment
conda activate biobb
# Change branch to bioconda
git checkout bioconda
# Merge or pull changes
# Check the current version
conda search cmip --info
# Modify with the new version:
#  doc/CMIP.man
#  src/main.F add to change_log at the beginning of the file
#  src/obrirArx.F
#  src/CMIP.man
#  src90/obrirArx.f
# Create new cmip.tar.gz
tar -cvzf cmip.tar.gz *
# Create hash and copy it
shasum -a 256 cmip.tar.gz
# Push changes
git add . && git commit -m "CMIP new conda version" && git push
# Bioconda
cd /Users/pau/projects/bioconda-recipes/
git checkout -f master; git pull origin master
git branch -D cmip; git push origin --delete cmip; git checkout -b cmip
atom /Users/pau/projects/bioconda-recipes/recipes/cmip
read -p "Modify recipes/cmip/build.sh and press any key..." -n1 -s
echo ""
read -p "Modify recipes/cmip/meta.yaml paste the headers and check if some dependency has changed from ~/cmip/meta.yaml and press any key..." -n1 -s
echo ""
git status; git add recipes/cmip/*
git commit -m "Update CMIP new version"
git push -u origin cmip
open https://github.com/bioconda/bioconda-recipes/pull/new/cmip

