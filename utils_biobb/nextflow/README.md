# Nextflow generator

Script for generating BioBB Nextflow modules for every package. Passing the BioBB package, the path to the modules JSON schema files of this package and the route where the modules must be saved, one Nextflow module (`<block>/main.nf`, `meta.yml` and `README.md`) will be automatically generated from the JSON schema of every package's module.

Each module runs the block command line inside the package biocontainer (or the bioconda package), with:

* One `tuple val(meta), path(...)` input with all the input files (required first, then optional). Optional files are passed as `[]`.
* One `tuple val(meta), path(...)` output channel per output file, named as the output argument. Output files are named `<prefix>_<role>.<extension>`, where `prefix` is `task.ext.prefix` or `meta.id`, and role is the output argument without `output_` and `_path`.
* A `versions_<package>` output sent to the `versions` topic.
* `task.ext.properties`: block properties, written to a `config.json` file. `raise_error` and `restart` are always set by the adapter.
* `task.ext.outputs`: map of output argument to extension. Required outputs use their first accepted format by default. Optional outputs are only requested when listed, as in the biobb Python API.
* A `stub` block creating every requested output.

Modules are named `<namespace>/<package>/<block>` (for example `bioexcel/biobb_gromacs/grompp`) and processes `<PACKAGE>_<BLOCK>` (for example `BIOBB_GROMACS_GROMPP`).
The `meta.yml` follows the [Nextflow module registry](https://docs.seqera.io/nextflow/modules/module-registry) schema (`nextflow module validate`), with the EDAM formats of the JSON schemas as ontologies.

## Execution steps

### Step 1: activate environment

Activate the environment where the BioBB package is loaded:

```Shell
conda activate biobb_env
```

### Step 2: execute script

Run the python script passing the BioBB package, the path to the modules JSON schema files of this package and the route where the Nextflow modules must be saved:

```Shell
python3 nextflow_generator.py -p biobb_package -i path/to/json_schemas -o path/to/biobb_adapters/biobb_adapters/nextflow/biobb_package
```

```Shell
python3 nextflow_generator.py --package biobb_package --input path/to/json_schemas --output path/to/biobb_adapters/biobb_adapters/nextflow/biobb_package --namespace bioexcel
```

Previously generated modules in the output folder are removed first, so there are no old/renamed modules.

When the package has a `test/conf.yml` (next to the json schemas folder, or given with `--conf`), the generator also writes a `tests` folder with a workflow that runs every block once with the inputs, properties and outputs of its conf.yml entry, writes `tests_report.tsv` and `tests_trace.tsv` in the launch folder, and fails if an expected output is missing. Test files are read from the package `test` folder of the local checkout, or from `--test_data`:

```Shell
nextflow run path/to/biobb_adapters/biobb_adapters/nextflow/biobb_package/tests/main.nf -profile docker
nextflow run path/to/biobb_adapters/biobb_adapters/nextflow/biobb_package/tests/main.nf -profile docker --test_data https://github.com/bioexcel/biobb_package/raw/master/biobb_package/test
```

### Step 3: check the modules

```Shell
nextflow lint path/to/biobb_adapters/biobb_adapters/nextflow/biobb_package
nextflow module validate path/to/biobb_adapters/biobb_adapters/nextflow/biobb_package/block
```

The `test` folder has a grompp -> mdrun workflow on the biobb_gromacs test data, run with the binaries of the current environment (or `-profile docker` / `-profile apptainer`) and `-stub`. Stub runs also need the biobb package or a container profile, because the version output is still evaluated:

```Shell
nextflow run test/main.nf
nextflow run test/main.nf -stub
```

## Copyright & Licensing
This software has been developed in the [MMB group](http://mmb.irbbarcelona.org) at the [BSC](http://www.bsc.es/) & [IRB](https://www.irbbarcelona.org/) for the [European BioExcel](http://bioexcel.eu/), funded by the European Commission (EU Horizon Europe [101093290](https://cordis.europa.eu/project/id/101093290), EU H2020 [823830](http://cordis.europa.eu/projects/823830), EU H2020 [675728](http://cordis.europa.eu/projects/675728)).

* (c) 2015-2026 [Barcelona Supercomputing Center](https://www.bsc.es/)
* (c) 2015-2026 [Institute for Research in Biomedicine](https://www.irbbarcelona.org/)

Licensed under the
[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0), see the file LICENSE for details.

![](https://bioexcel.eu/wp-content/uploads/2019/04/Bioexcell_logo_1080px_transp.png "Bioexcel")
