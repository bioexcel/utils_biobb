mamba create -n dev38 python=3.8 pyyaml requests biopython
mamba activate dev38

# Copy the Python paths file
cp /Users/pau/projects/utils_biobb/utils_biobb/environment/biobb.pth /Users/pau/mambaforge/envs/dev38/lib/python3.8/site-packages/


# Just for development vscode
mamba install -y mypy

# Development tests
mamba install -y pillow imagehash

mamba install -y pytest pytest-cov pytest-html flake8 pip

# biobb_gromacs
mamba install -y pocl gromacs==2022.2

# biobb_cmip
mamba install -y mdanalysis

# biobb_model
mamba install -y xmltodict

# biobb_pmx
mamba install -y pmx_biobb

# Install tensorflow breaks everything best to keep it in a different env biobb_ml
# mamba install -y tensorflow

# Create the bin files
python /Users/pau/projects/utils_biobb/utils_biobb/environment/create_bin_softlinks.py -p all -o /Users/pau/mambaforge/envs/dev38/bin/

# Release new version pypi
mamba install -y twine keyring
