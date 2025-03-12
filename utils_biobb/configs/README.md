# Configuration files

The creation of the configuration files is automatic and the data is taken from the path/to/biobb/package/test/conf.yml file. The script will generate a JSON and a YAML config files for each module with *properties* defined in its parameters.

## Configs generator

Script for the creation of JSON / YAML config files

### Execution steps

#### Step 1: activate environment

Activate the environment where the BioBB package is loaded:

```Shell
conda activate biobb_env
```
#### Step 2: create config/ folder

Create the folder *config/* for storing all the config files:

```Shell
path/to/biobb_package/biobb_package/test/data/config
```

#### Step 3: execute script

Run the python script passing the path to the *conf.yml* file and the path to the configs folder:

```Shell
python3 configs_generator.py -i path/to/testconffile/conf.yml -o path/to/outputdir
```

```Shell
python3 configs_generator.py --input_conf_yaml path/to/testconffile/conf.yml --output path/to/outputdir
```

## Copyright & Licensing
This software has been developed in the [MMB group](http://mmb.irbbarcelona.org) at the [BSC](http://www.bsc.es/) & [IRB](https://www.irbbarcelona.org/) for the [European BioExcel](http://bioexcel.eu/), funded by the European Commission (EU Horizon Europe [101093290](https://cordis.europa.eu/project/id/101093290), EU H2020 [823830](http://cordis.europa.eu/projects/823830), EU H2020 [675728](http://cordis.europa.eu/projects/675728)).

* (c) 2015-2024 [Barcelona Supercomputing Center](https://www.bsc.es/)
* (c) 2015-2024 [Institute for Research in Biomedicine](https://www.irbbarcelona.org/)

Licensed under the
[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0), see the file LICENSE for details.

![](https://bioexcel.eu/wp-content/uploads/2019/04/Bioexcell_logo_1080px_transp.png "Bioexcel")
