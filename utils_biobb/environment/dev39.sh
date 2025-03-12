condabin="conda"
envpath=/opt/anaconda3/envs/dev39
projects=/Users/pau/projects/
utils_biobb=${projects}/utils_biobb/
biobb_structure_checking=${projects}/biobb_structure_checking/

# $condabin create -n dev39 python=3.9
# $condabin activate dev39

# Copy the Python paths file
cp ${utils_biobb}/utils_biobb/environment/biobb.pth ${envpath}/lib/python3.9/site-packages/

$condabin install -y -c conda-forge libiconv
$condabin install -y -c conda-forge accelerate


# Release new version pypi
$condabin install -y twine keyring

# Create
$condabin install -y jupyter

# Just for development vscode
$condabin install -y mypy
$condabin install -y types-setuptools
$condabin install -y types-pyyaml

# Development tests
$condabin install -y pillow
$condabin install -y imagehash
$condabin install -y jsonschema
$condabin install -y pytest
$condabin install -y pytest-cov
$condabin install -y pytest-html
$condabin install -y flake8
$condabin install -y pip

# biobb_common
$condabin install -y pyyaml
$condabin install -y requests
$condabin install -y biopython

# biobb_amber
$condabin install -y ambertools==22.5
$condabin install -y gfortran

# biobb_analysis

# biobb_chemistry
$condabin install -y openbabel
$condabin install -y acpype

# biobb_cmip
$condabin install -y mdanalysis
$condabin install -y cmip

# biobb_cp2k
$condabin install -y cp2k

# biobb_dna
# $condabin install -y pandas
# $condabin install -y scikit-learn
# $condabin install -y curves

# biobb_flexdyn
$condabin install -y imods
$condabin install -y prody
$condabin install -y concoord
$condabin install -y nolb

# biobb_flexserv
$condabin install -y perl
$condabin install -y flexserv
$condabin install -y pcasuite

# biobb_godmd
$condabin install -y godmd
$condabin install -y emboss

# biobb_gromacs
$condabin install -y gromacs

# biobb_haddock
$condabin install -y haddock_biobb

# biobb_io

# biobb_model
$condabin install -y xmltodict
$condabin install -y -c salilab modeller

# biobb_pdb_tools
pip install pdb-tools

# biobb_pmx
$condabin install -y pmx_biobb

# biobb_pytorch
$condabin install -y pytorch

# biobb_structure_utils

# biobb_vs
$condabin install -y vina
$condabin install -y fpocket

# Install tensorflow breaks everything best to keep it in a different env biobb_ml
# $condabin install -y tensorflow

# Create the bin files
python ${utils_biobb}/utils_biobb/environment/create_bin_softlinks.py -p all -o ${envpath}/bin/
ln -s ${biobb_structure_checking}/biobb_structure_checking/check_structure.py ${envpath}/bin/check_structure