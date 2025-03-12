# Workflows generator

## CWL WF generator

Script for generating BioBB CWL workflows. Passing the pure pyhon workflow YAML and Python files paths and the route to the biobb_adapters, the CWL version for the workflow will be automatically generated in the output folder.

### Step 1: connect to VPN

In some occasions, the VPN must be connected in order to connect to MongoDB.

### Step 2: activate environment

Activate an environment with **pymongo**:

```Shell
conda activate biobb_env
```

### Step 3: execute script

Run the python script passing the pure pyhon workflow YAML and Python files paths, the route to the biobb_adapters and the route where the CWL and YAML files must be saved:

```Shell
python3 cwl_wf_generator.py -y path/to/yaml/workflow -p path/to/python/workflow -a path/to/biobb_adapters -o path/to/cwl/workflow
```

```Shell
python3 cwl_wf_generator.py --yml_in path/to/yaml/workflow --python_in path/to/python/workflow --adapters path/to/biobb_adapters --output path/to/cwl/workflow
```

## Copyright & Licensing
This software has been developed in the [MMB group](http://mmb.irbbarcelona.org) at the [BSC](http://www.bsc.es/) & [IRB](https://www.irbbarcelona.org/) for the [European BioExcel](http://bioexcel.eu/), funded by the European Commission (EU Horizon Europe [101093290](https://cordis.europa.eu/project/id/101093290), EU H2020 [823830](http://cordis.europa.eu/projects/823830), EU H2020 [675728](http://cordis.europa.eu/projects/675728)).

* (c) 2015-2023 [Barcelona Supercomputing Center](https://www.bsc.es/)
* (c) 2015-2023 [Institute for Research in Biomedicine](https://www.irbbarcelona.org/)

Licensed under the
[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0), see the file LICENSE for details.

![](https://bioexcel.eu/wp-content/uploads/2019/04/Bioexcell_logo_1080px_transp.png "Bioexcel")
