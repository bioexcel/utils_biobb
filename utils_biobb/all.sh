#!/usr/bin/env bash

#Usage: ./all.sh [names_of_biobb_packages]
#Activate conda
ide=atom
path_user=/Users/pau/
biobbs_dir=/Users/pau/projects/
path_json_schemas=/Users/pau/projects/utils_biobb/utils_biobb/json/
conda=biobb
# json_paths
json_generator_script_path=/Users/pau/projects/utils_biobb/utils_biobb/json/json_generator.py
json_validator_script_path=/Users/pau/projects/utils_biobb/utils_biobb/json/json_validator.py
json_master_schema_path=/Users/pau/projects/utils_biobb/utils_biobb/json/schema/master_schema.json
# configs
configs_generator_script_path=/Users/pau/projects/utils_biobb/utils_biobb/configs/configs_generator.py
# command_line
command_line_generator_script_path=/Users/pau/projects/utils_biobb/utils_biobb/command_line/command_line_doc_generator.py
# biobb_adapters
biobb_adapters_path=/Users/pau/projects/biobb_adapters/
# cwl adapters
cwl_generator_script_path=/Users/pau/projects/utils_biobb/utils_biobb/cwl/cwl_generator.py
# pycompss adapters
pycompss_generator_script_path=/Users/pau/projects/utils_biobb/utils_biobb/pycompss/pycompss_generator.py
pycompss_template_path=/Users/pau/projects/utils_biobb/utils_biobb/pycompss/pycompss_wrapper.tmpl

# list of biobbs to be executed
if [ $# -gt 0 ]; then
    biobb_list="$@"
else
    biobb_list="biobb_analysis biobb_chemistry biobb_cmip biobb_io biobb_gromacs biobb_model biobb_pmx biobb_structure_utils biobb_vs biobb_ml biobb_amber biobb_dna"
fi
echo "List of packages where the script will be executed:"
echo "$biobb_list"

echo "******************************************************"
echo "Be sure of having activated $conda conda environment!"
echo "******************************************************"
for biobb in ${biobb_list}
 do
  echo "Processing ${biobb}:"
  biobb_path=${biobbs_dir}${biobb}
  echo "  cd ${biobb_path}"
  cd ${biobb_path}

  # GIT
  echo "  ${biobb} Updating projetct:"
  echo "    git config pull.rebase false"
  git config pull.rebase false
  echo "    git pull"
  git pull

  # JSON
  echo ""
  echo "  ${biobb} Create jsons:"
  echo "    python3 ${json_generator_script_path} -p ${biobb} -o ${biobb_path}/${biobb}/"
  python3 ${json_generator_script_path} -p ${biobb} -o ${biobb_path}/${biobb}/
  echo ""
  echo "    python3 ${json_validator_script_path} -p ${biobb} -i ${biobb_path}/${biobb}/json_schemas/ -s ${json_master_schema_path}"
  python3 ${json_validator_script_path} -p ${biobb} -i ${biobb_path}/${biobb}/json_schemas/ -s ${json_master_schema_path}

  # CONFIGS
  echo ""
  echo "  ${biobb} Create configs:"
  echo "    python3 ${configs_generator_script_path} -i ${biobb_path}/${biobb}/test/conf.yml -o ${biobb_path}/${biobb}/test/data/config/"
  python3 ${configs_generator_script_path} -i ${biobb_path}/${biobb}/test/conf.yml -o ${biobb_path}/${biobb}/test/data/config/

  # COMMAND_LINE.MD
  echo ""
  echo "  ${biobb} Create command_line.md:"
  echo "    python3 ${command_line_generator_script_path} -j ${biobb_path}/${biobb}/json_schemas/ -c ${biobb_path}/${biobb}/test/data/config/ -b ${biobb} -o ${biobb_path}/${biobb}/docs/source/command_line.md"
  python3 ${command_line_generator_script_path} -j ${biobb_path}/${biobb}/json_schemas/ -c ${biobb_path}/${biobb}/test/data/config/ -b ${biobb} -o ${biobb_path}/${biobb}/docs/source/command_line.md

  # CWL
  echo ""
  echo "  ${biobb} Create CWL adapters:"
  echo "    python3 ${cwl_generator_script_path} -p ${biobb} -i ${biobb_path}/${biobb}/json_schemas/ -o ${biobb_adapters_path}/biobb_adapters/cwl/${biobb}"
  python3 ${cwl_generator_script_path} -p ${biobb} -i ${biobb_path}/${biobb}/json_schemas/ -o ${biobb_adapters_path}/biobb_adapters/cwl/${biobb}

  # PYCOMPSS
  echo ""
  echo "  ${biobb} Create pycompss adapters:"
  echo "    python3 ${pycompss_generator_script_path} -p ${biobb} -o ${biobb_adapters_path}/biobb_adapters/pycompss/"
  python3 ${pycompss_generator_script_path} -p ${biobb} -o ${biobb_adapters_path}/biobb_adapters/pycompss/

 done

