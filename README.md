# Utils BioBB

## Introduction
In this repository can be found the utils created for Bioxcel building Blocks:

### Documentation

- [json](json/): Scripts for generating and validating JSON Schemas for every package.
- [cwl](cwl/): Scripts for generating CWL files for every package.
- [configs](configs/): Scripts for generating config files for every package.
- [command_line](command_line/): Scripts for generating command line documentation for every package.
- [changelog](changelog/): Scripts for generating changelogs for every package.

#### Execution order for documentation scripts

1. [json_generator.py](json#json-generator)

2. [json_validator.py](json#json-validator)

3. [cwl_generator.py](cwl/)

4. [command_line_doc_generator.py](command_line)

5. [changelog_generator.py](changelog)

### Bioconda package generation

- [new_version](new_version/): Scripts for creating a new package or updating an existing one.

## Copyright & Licensing
This software has been developed in the [MMB group](http://mmb.irbbarcelona.org) at the [BSC](http://www.bsc.es/) & [IRB](https://www.irbbarcelona.org/) for the [European BioExcel](http://bioexcel.eu/), funded by the European Commission (EU H2020 [823830](http://cordis.europa.eu/projects/823830), EU H2020 [675728](http://cordis.europa.eu/projects/675728)).

* (c) 2015-2020 [Barcelona Supercomputing Center](https://www.bsc.es/)
* (c) 2015-2020 [Institute for Research in Biomedicine](https://www.irbbarcelona.org/)

Licensed under the
[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0), see the file LICENSE for details.

![](https://bioexcel.eu/wp-content/uploads/2019/04/Bioexcell_logo_1080px_transp.png "Bioexcel")
