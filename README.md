# Utils BioBB

## Introduction
In this repository can be found the utils created for Bioxcel building Blocks:

### Documentation

- [json](utils_biobb/json/): Scripts for generating and validating JSON Schemas for every package.
- [cwl](utils_biobb/cwl/): Scripts for generating CWL files for every package.
- [configs](utils_biobb/configs/): Scripts for generating config files for every package.
- [command_line](utils_biobb/command_line/): Scripts for generating command line documentation for every package.
- [changelog](utils_biobb/changelog/): Scripts for generating changelogs for every package.

#### Execution order for documentation scripts

1. [JSON generator](utils_biobb/json#json-generator)

2. [JSON validator](utils_biobb/json#json-validator)

3. [CWL generator](utils_biobb/cwl#cwl-generator)

4. [Configs generator](utils_biobb/configs#configuration-files)

5. [Command line generator](utils_biobb/command_line#command-line-generator)

6. [Changelog generator](utils_biobb/changelog#changelog-generator)

### Bioconda package generation

- [new_version](utils_biobb/new_version/): Scripts for creating a new package or updating an existing one.

## Copyright & Licensing
This software has been developed in the [MMB group](http://mmb.irbbarcelona.org) at the [BSC](http://www.bsc.es/) & [IRB](https://www.irbbarcelona.org/) for the [European BioExcel](http://bioexcel.eu/), funded by the European Commission (EU H2020 [823830](http://cordis.europa.eu/projects/823830), EU H2020 [675728](http://cordis.europa.eu/projects/675728)).

* (c) 2015-2020 [Barcelona Supercomputing Center](https://www.bsc.es/)
* (c) 2015-2020 [Institute for Research in Biomedicine](https://www.irbbarcelona.org/)

Licensed under the
[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0), see the file LICENSE for details.

![](https://bioexcel.eu/wp-content/uploads/2019/04/Bioexcell_logo_1080px_transp.png "Bioexcel")
