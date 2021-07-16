# Change directory to CMIP
cd ~/projects/CMIP/
# Activate environment
conda activate biobb
# Pull last changes
git pull
# Check the current version
conda search cmip --info
# Modify with the new version:
atom dist/doc/CMIP.man dist/src/main.F dist/src/obrirArx.F dist/src/CMIP.man src90/obrirArx.f
# Create new cmip.tar.gz
tar -cvzf cmip.tar.gz dat dist/doc dist/scripts dist/src src90 dist/tests dist/wrappers
# Create hash and copy it
shasum -a 256 cmip.tar.gz
# Push changes
git add . && git commit -m "CMIP new conda version" && git push
# Bioconda
cd ~/projects/bioconda-recipes/
git checkout -f master; git pull origin master
git branch -D cmip; git push origin --delete cmip; git checkout -b cmip
atom ~/projects/bioconda-recipes/recipes/cmip
git status; git add recipes/cmip/*
git commit -m "Update CMIP new version"
git push -u origin cmip
open https://github.com/bioconda/bioconda-recipes/pull/new/cmip

