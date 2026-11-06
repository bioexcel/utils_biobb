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

When the package has a `test/conf.yml` (next to the json schemas folder, or given with `--conf`), the generator also writes a `tests` folder with a workflow that runs every block once with the inputs, properties and outputs of its conf.yml entry, writes `tests_report.tsv` and `tests_trace.tsv` in the launch folder, and fails if an expected output is missing. Blocks whose test can't run in their biocontainer (licensed software, listed in `SKIP_TESTS`) are skipped with a comment. Test files are read from the package `test` folder of the local checkout, or from `--test_data`:

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

## Workflow generator

`nextflow_wf_generator.py` translates a pure python workflow of [biobb_workflows](https://github.com/bioexcel/biobb_workflows) (`python/workflow.yml` and `python/workflow.py`) to a Nextflow workflow, as `cwl_wf_generator.py` does for CWL:

* `main.nf`: one step per `workflow.py` call, running the module of its block under the step name (`include { BIOBB_GROMACS_GROMPP as STEP9_GROMPP_MIN }`). `file:` inputs become samplesheet columns and `dependency/<step>/<output>` paths the output channel of that step, joined by `meta` in the module input order.
* `samplesheet.csv` (`--input`): one row per system, all of them run in parallel. The default one has a row with the python workflow inputs, which are copied next to it.
* `nextflow.config`: the `ext.properties` and `ext.outputs` (extensions of the `workflow.yml` file names and optional outputs) of every step, CPUs of the multithreaded blocks and `docker`, `apptainer`, `singularity` and `conda` profiles.
* `README.md` and the modules used, copied from biobb_adapters into `modules/bioexcel/<package>/<block>`.
* The MPI properties (`mpi_bin`, `mpi_np`, ...) and the `binary_path` of their steps (`sander.MPI`) are left out, because the biocontainers have no MPI.
* Steps under `if conf.properties['global_properties'][<flag>]` in `workflow.py` only run when the `--<flag>` param is true.
* Other python logic is not supported, and the generator stops with "port this workflow by hand" when it finds it: steps inside loops or other conditions, blocks not called as `<block>(**global_paths[<step>], properties=global_prop[<step>])`, or changes of the step paths or properties (`paths = global_paths[...]`, `global_prop[...][...] = ...`). Python code that does not call blocks (helper functions, files written with Biopython...) can't be detected: check the generated `main.nf` against `workflow.py`.
* Results are published to `results/<id>/<step>/`.
* `../tests/nextflow/run_test.sh`: the e2e test of the workflow, with the conventions of the other biobb_workflows flavours (see its `docs/testing.md`). It runs the workflow with a copy of `nextflow.config` cut by the per-workflow `TEST_SETTINGS` (the runtime reductions of the python CI) and checks every output of every step.

Generated files are overwritten when regenerating, unless they were edited by hand (no generated mark). `samplesheet.csv` is only written when it doesn't exist.

Workflows ported by hand (a `main.nf` without the generated mark, as the 7 biobb_workflows with python logic) are not regenerated: the generator only refreshes the modules of `modules/bioexcel` that their `main.nf` includes, so new module versions reach them with the same command. Their other files, `modules/local` (python logic as small processes) and `tests/nextflow/run_test.sh` are kept.

```Shell
python3 nextflow_wf_generator.py -y path/to/biobb_wf_name/python/workflow.yml -p path/to/biobb_wf_name/python/workflow.py -a path/to/biobb_adapters/biobb_adapters/nextflow -o path/to/biobb_wf_name/nextflow
nextflow lint path/to/biobb_wf_name/nextflow
nextflow run path/to/biobb_wf_name/nextflow -profile docker
```

## Copyright & Licensing
This software has been developed in the [MMB group](http://mmb.irbbarcelona.org) at the [BSC](http://www.bsc.es/) & [IRB](https://www.irbbarcelona.org/) for the [European BioExcel](http://bioexcel.eu/), funded by the European Commission (EU Horizon Europe [101093290](https://cordis.europa.eu/project/id/101093290), EU H2020 [823830](http://cordis.europa.eu/projects/823830), EU H2020 [675728](http://cordis.europa.eu/projects/675728)).

* (c) 2015-2026 [Barcelona Supercomputing Center](https://www.bsc.es/)
* (c) 2015-2026 [Institute for Research in Biomedicine](https://www.irbbarcelona.org/)

Licensed under the
[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0), see the file LICENSE for details.

![](https://bioexcel.eu/wp-content/uploads/2019/04/Bioexcell_logo_1080px_transp.png "Bioexcel")
