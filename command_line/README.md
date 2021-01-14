# Command line generator

The creation of the command line documentation file is automatic and the data is taken from the path/to/biobb/package/json_schemas and path/to/biobb/package/test/data/config folders. The script will generate a single command line documentation file for each package.

## Configs generator

Script for the creation of the command line documentation file in Markdown.

### Execution steps

#### Step 1: activate environment

Activate the environment where the BioBB package is loaded:

```Shell
conda activate biobb_env
```

#### Step 2: execute script

Run the python script passing the path to the package *json_schemas/* folder, the package *configs/* folder, the package name and the path to the *command_line.md* file in the *docs/source/* folder:

```Shell
python3 command_line_doc_generator.py -j path/to/json_schemas_folder -c path/to/config_folder -b biobb_name -o path/to/docs/source/command_line.md
```

```Shell
python3 command_line_doc_generator.py --json_schemas_folder path/to/json_schemas_folder --config_folder path/to/config_folder --biobb_name biobb_name --output path/to/docs/source/command_line.md
```

## Copyright & Licensing
This software has been developed in the [MMB group](http://mmb.irbbarcelona.org) at the [BSC](http://www.bsc.es/) & [IRB](https://www.irbbarcelona.org/) for the [European BioExcel](http://bioexcel.eu/), funded by the European Commission (EU H2020 [823830](http://cordis.europa.eu/projects/823830), EU H2020 [675728](http://cordis.europa.eu/projects/675728)).

* (c) 2015-2020 [Barcelona Supercomputing Center](https://www.bsc.es/)
* (c) 2015-2020 [Institute for Research in Biomedicine](https://www.irbbarcelona.org/)

Licensed under the
[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0), see the file LICENSE for details.

![](https://bioexcel.eu/wp-content/uploads/2019/04/Bioexcell_logo_1080px_transp.png "Bioexcel")

