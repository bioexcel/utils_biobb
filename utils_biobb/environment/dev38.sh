# source /Users/pau/mambaforge/etc/profile.d/conda.sh
# source /Users/pau/mambaforge/etc/profile.d/mamba.sh
# mamba create -n dev38 python=3.8 pyyaml requests biopython
# mamba activate dev38

# Copy the Python paths file
cp /Users/pau/projects/utils_biobb/utils_biobb/environment/biobb.pth /Users/pau/mambaforge/envs/dev38/lib/python3.8/site-packages/

# Install pip
mamba install -y pip

# Release new version pypi
mamba install -y twine keyring

# Create
mamba install -y jupyter

# Just for development vscode
mamba install -y mypy

# Development tests
mamba install -y pillow
mamba install -y imagehash
mamba install -y jsonschema
mamba install -y pytest
mamba install -y pytest-cov
mamba install -y pytest-html
mamba install -y flake8
mamba install -y pip


# biobb_amber
mamba install -y ambertools==22.5
mamba install -y gfortran

# biobb_analysis

# biobb_chemistry
mamba install -y openbabel
mamba install -y acpype

# biobb_cmip
mamba install -y mdanalysis
mamba install -y cmip

# biobb_cp2k
mamba install -y cp2k

# biobb_dna
mamba install -y pandas
mamba install -y scikit-learn
mamba install -y curves

# biobb_flexdyn
mamba install -y imods
mamba install -y prody
mamba install -y concoord
mamba install -y nolb

# biobb_flexserv
mamba install -y perl
mamba install -y flexserv
mamba install -y pcasuite

# biobb_godmd
mamba install -y godmd
mamba install -y emboss

# biobb_gromacs
mamba install -y pocl
mamba install -y gromacs==2022.2

# biobb_haddock
mamba install -y haddock_biobb

# biobb_io

# biobb_model
mamba install -y xmltodict
mamba install -y -c salilab modeller

# biobb_pdb_tools
pip install pdb-tools

# biobb_pmx
mamba install -y pmx_biobb

# biobb_pytorch
mamba install -y pytorch

# biobb_structure_utils

# biobb_vs
mamba install -y vina
mamba install -y fpocket

# Install tensorflow breaks everything best to keep it in a different env biobb_ml
# mamba install -y tensorflow


# Create the bin files
python /Users/pau/projects/utils_biobb/utils_biobb/environment/create_bin_softlinks.py -p all -o /Users/pau/mambaforge/envs/dev38/bin/
ln -s /Users/pau/projects/biobb_structure_checking/biobb_structure_checking/check_structure.py /Users/pau/mambaforge/envs/dev38/bin/check_structure