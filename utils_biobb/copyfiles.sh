#!/usr/bin/env bash

biobb_dir_path="/Users/pau/projects/"
cd $biobb_dir_path
for biobb in biobb_*; do
    echo $biobb
    cd $biobb_dir_path/$biobb
    ls .github/ISSUE_TEMPLATE/ &> /dev/null
    if [ $? -eq 0 ]; then
        echo "Exists"
    else
        read -p "Copy and push files [Y/n]? " continue_script
        if [ $continue_script == 'y' -o $continue_script == 'Y'  ]; then
            mkdir -p .github/workflows/
            cp -v /Users/pau/projects/biobb_chemistry/.github/workflows/inactive_issues.yml .github/workflows/
            cp -v -r /Users/pau/projects/biobb_chemistry/.github/ISSUE_TEMPLATE .github/
            git add .github/workflows/inactive_issues.yml
            git add .github/ISSUE_TEMPLATE/
            git commit -m "Adding inactive issues workflow and template"
            git push
        fi
    fi
    cd $biobb_dir_path
    echo " "
done