#!/usr/bin/env bash


#Usage: ./all.sh [names_of_biobb_packages]
#Activate conda

want_to_exit(){
  if [ $1 -ne 0 ]; then
      read -p "Last command has failed do you want to continue [Y/n]? " continue_script
      if [ $continue_script == 'y' -o $continue_script == 'Y'  ]; then
	        exit 1
      fi
  fi
}


ide=code # (VSCode) Change to your preferred IDE.
conda=biobb_all
path_user=$HOME
biobb_dir=$path_user/repo/biobb/biobb_all/biobb  # PATH TO YOUR BIOBB REPOSITORIES
utils_biobb=$biobb_dir/utils_biobb/utils_biobb # PATH TO YOUR UTILS_BIOBB REPOSITORY
biobb_adapters_path=$biobb_dir/biobb_adapters/  # PATH TO YOUR biobb_adapters REPOSITORY 
export PYTHONPATH=$biobb_dir/utils_biobb/:$PYTHONPATH
# json_paths
path_json_schemas=$utils_biobb/json/
json_generator_script_path=$path_json_schemas/json_generator.py
json_validator_script_path=$path_json_schemas/json_validator.py
json_master_schema_path=$path_json_schemas/schema/master_schema.json
# configs
configs_generator_script_path=$utils_biobb/configs/configs_generator.py
# command_line
command_line_generator_script_path=$utils_biobb/command_line/command_line_doc_generator.py
# cwl adapters
cwl_generator_script_path=$utils_biobb/cwl/cwl_generator.py
# pycompss adapters
pycompss_generator_script_path=$utils_biobb/pycompss/pycompss_generator.py
pycompss_template_path=$utils_biobb/pycompss/pycompss_wrapper.tmpl
# horus adapters
horus_generator_script_path=$utils_biobb/horus/horus_generator.py
# galaxy adapters
galaxy_generator_script_path=$utils_biobb/galaxy/galaxy_generator.py

# list of biobbs to be executed
if [ $# -gt 0 ]; then
    biobb_list="$@"
else
    # biobb_common
    # biobb_template
    # biobb_structure_checking
    # biobb_ml
    # utils_biobb
    biobb_list="biobb_amber biobb_analysis biobb_chemistry biobb_cmip biobb_cp2k biobb_dna biobb_flexdyn biobb_flexserv biobb_godmd biobb_gromacs biobb_haddock biobb_io biobb_mem biobb_model biobb_pdb_tools biobb_pmx biobb_pytorch biobb_structure_utils biobb_vs"

fi
echo "List of packages where the script will be executed:"
echo "$biobb_list"

echo "******************************************************"
echo "Be sure of having activated $conda conda environment!"
echo "******************************************************"
for biobb in ${biobb_list}
 do
  echo "Processing ${biobb}:"
  biobb_path=${biobbs_dir}/${biobb}
  echo "  cd ${biobb_path}"
  cd ${biobb_path}

#   # GIT
#   echo "  ${biobb} Updating project:"
#   echo "    git config pull.rebase false"
#   git config pull.rebase false
#   echo "    git pull"
#   git pull
#   want_to_exit $?

  # JSON
  echo ""
  echo "  ${biobb} Create jsons:"
  echo "    python3 ${json_generator_script_path} -p ${biobb} -o ${biobb_path}/${biobb}/"
  python3 ${json_generator_script_path} -p ${biobb} -o ${biobb_path}/${biobb}/
  want_to_exit $?
  echo ""
  echo "    python3 ${json_validator_script_path} -p ${biobb} -i ${biobb_path}/${biobb}/json_schemas/ -s ${json_master_schema_path}"
  python3 ${json_validator_script_path} -p ${biobb} -i ${biobb_path}/${biobb}/json_schemas/ -s ${json_master_schema_path}
  want_to_exit $?

  # CONFIGS
  echo ""
  echo "  ${biobb} Create configs:"
  echo "    python3 ${configs_generator_script_path} -i ${biobb_path}/${biobb}/test/conf.yml -o ${biobb_path}/${biobb}/test/data/config/"
  python3 ${configs_generator_script_path} -i ${biobb_path}/${biobb}/test/conf.yml -o ${biobb_path}/${biobb}/test/data/config/
  want_to_exit $?

  # COMMAND_LINE.MD
  echo ""
  echo "  ${biobb} Create command_line.md:"
  echo "    python3 ${command_line_generator_script_path} -j ${biobb_path}/${biobb}/json_schemas/ -c ${biobb_path}/${biobb}/test/data/config/ -b ${biobb} -o ${biobb_path}/${biobb}/docs/source/command_line.md"
  python3 ${command_line_generator_script_path} -j ${biobb_path}/${biobb}/json_schemas/ -c ${biobb_path}/${biobb}/test/data/config/ -b ${biobb} -o ${biobb_path}/${biobb}/docs/source/command_line.md
  want_to_exit $?

  # CWL
  echo ""
  echo "  ${biobb} Create CWL adapters:"
  echo "    python3 ${cwl_generator_script_path} -p ${biobb} -i ${biobb_path}/${biobb}/json_schemas/ -o ${biobb_adapters_path}/biobb_adapters/cwl/${biobb}"
  python3 ${cwl_generator_script_path} -p ${biobb} -i ${biobb_path}/${biobb}/json_schemas/ -o ${biobb_adapters_path}/biobb_adapters/cwl/${biobb}
  want_to_exit $?

  # PYCOMPSS
  echo ""
  echo "  ${biobb} Create pycompss adapters:"
  echo "    python3 ${pycompss_generator_script_path} -p ${biobb} -o ${biobb_adapters_path}/biobb_adapters/pycompss/"
  python3 ${pycompss_generator_script_path} -p ${biobb} -o ${biobb_adapters_path}/biobb_adapters/pycompss/
  want_to_exit $?

  # Horus
  echo ""
  echo "  ${biobb} Create Horus adapters:"
  echo "    python3 ${horus_generator_script_path} -p ${biobb} -o ${biobb_adapters_path}/biobb_adapters/horus/"
  python3 ${horus_generator_script_path} -p ${biobb} -o ${biobb_adapters_path}/biobb_adapters/horus/
  want_to_exit $?

  # Galaxy
  echo ""
  echo "  ${biobb} Create Galaxy adapters:"
  echo "    python3 ${galaxy_generator_script_path} -p ${biobb} -o ${biobb_adapters_path}/biobb_adapters/galaxy/"
  python3 ${galaxy_generator_script_path} -p ${biobb} -o ${biobb_adapters_path}/biobb_adapters/galaxy/
  want_to_exit $?


 done

