# JSON

## JSON generator

Script for generating BioBB JSON Schemas for every package. Passing the name of the package and the absolute route to it, all the JSON files will be automatically generated from the documentation of every package's module.

### Execution steps

#### Step 1: activate environment

Activate the environment where the BioBB package is loaded:

```Shell
conda activate biobb_env
```

#### Step 2: execute script

Run the python script passing the BioBB package to be parsed and the folder where the JSON files will be saved:

```Shell
python3 json_generator.py -p biobb_package -o path/to/biobb_package/biobb_package
```

```Shell
python3 json_generator.py --package biobb_package --output path/to/biobb_package/biobb_package
```

### Files structure

The structure of a biobb package must be:

* biobb_package/
	* biobb_package/
		* **\_\_init\_\_.py**
		* block/
			* **\_\_init\_\_.py**
			* module 1
			* module 2
		* docs/
		* **json_schemas/**
		* test/
			* data/
			* reference/
				* **config/**
				* block 1/
				* block 2/
			* unitests/
			* conf.yml
	* .gitignore
	* Dockerfile
	* LICENSE
	* README.md
	* setup.py
	* Singularity.latest

#### \_\_init\_\_.py files

The *\_\_init\_\_.py* file in the first level must have the following structure:

```Python
name = "biobb_package"
__all__ = ["block1", "block2", ..., "blockn"]
```

The *\_\_init\_\_.py* file in the second level must have the following structure:

```Python
name = "block1"
__all__ = ["module1", "module2", ..., "modulen"]
```

In the *\_\_all\_\_* list we have to put all the modules for which we want to generate a JSON schema.

#### json_schemas folder

The *json_schemas* folder must exist before executing the script. The file *biobb_package.json* won't be affected by the script's execution.

#### config folder

The *config* folder must exist before executing the script. All the JSON config files will be saved in this folder.

### Docs specifications

All the docs must be written in correct [Google Style Python Docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) format and they must be properly indented. Example of documentation:

```rst
Description of the module.

Args:
    arg_name1 (arg_type): Description for argument 1. File type: input / output. `Sample file <url_to_sample_file1>`_. Accepted formats: format1 (edam:format_XXXX), format2 (edam:format_XXXX), format3 (edam:format_XXXX). 
    arg_name2 (arg_type) (Optional): Description for argument 2. File type: input / output. `Sample file <url_to_sample_file2>`_. Accepted formats: format1 (edam:format_XXXX), format2 (edam:format_XXXX).
    properties (dic):
        * **property1** (*prop_type*) - (property1_default) [min-max|step] [WF property] Property 1 description. Values: value1 (description for value1), value2 (description for value2), value3 (description for value3).
        * **property2** (*prop_type*) - (property2_default) Property 2 description. 
        * **property3** (*dic*) - (None) Property 3 description.
            * **parameter1** (*param_type*) - (parameter1_default) Parameter 1 description. Values: value1 (description for value1), value2 (description for value2), value3 (description for value3).
```

#### Arguments

The arguments must have the next format:

```rst
arg_name (arg_type) (Optional): Description. File type: input / output. `Sample file <url_to_sample_file1>`_. Accepted formats: format1 (edam:format_XXXX), format2 (edam:format_XXXX), format3 (edam:format_XXXX).
```

The *argument type* must be between brackets. Argument types: *str* (string), *dic* (dictionary).

If the argument is optional, the *(Optional)* expression must be right next the *argument type* separated by a single space.

*Description* is a string descriving the functionality of the argument.

*File type* must be **input** or **output**. Although it's highly recommended to name the input files as *input_something* and the output files as *output_something*, with this parameter we ensure which type the file is.

*Sample file* is a link to a sample file for this argument. It's recommended to put the file used for unitest integrated in the same repository:

* **biobb_package/biobb_package/test/data/block/input_file**: for input files.
* **biobb_package/biobb_package/test/reference/block/reference_file**: for output files.

The format of the *Sample file* link must be in **reStructuredText** (RST) format: `` Sample file <url_to_sample_file>`_``

Preceded by the **Accepted formats:** expression, it's mandatory to create a list with the formats for each argument. The [edam format](http://bioportal.bioontology.org/ontologies/EDAM?p=summary) for each format type must be added following the next pattern:  *format1 (**edam:format_XXXX**)*.

#### Properties

The properties must have the next format:

```rst
* **property** (*prop_type*) - (property_default) [min-max|step] [WF property] Property description. Values: value1 (description for value1), value2 (description for value2), value3 (description for value3).
```

The *property name* must be a list item in markdown bold (between double asterisks).

The *property type* must be between brackets and in markdown italic (between asterisks). Property types: *str* (string), *dic* (dictionary), *int* (integer), *float*, *bool* (boolean).

The *property default* must be between brackets. If it's a text it's highly recommendable to put it between double quotes instead of single ones.

The *property range* (only for integer or float properties) must be between square brackets following the next pattern: *[min-max|step]*.

The *WF property* indicates if this is a Workflow property. It must be between square brackets and it's optional.

*Description* is a string descriving the functionality of the property.

Preceded by the **Values:** expression, there can be a list with the possible value for each property. The patther must be the following (value description is not mandatory):  *value (description for value)*.

#### Parameters

The parameters must have the next format:

```rst
* **parameter** (*prop_type*) - (property_default) [min-max|step] Property description. Values: value1 (description for value1), value2 (description for value2), value3 (description for value3).
```

The *parameter name* must be a list item in markdown bold (between double asterisks).

The *parameter type* must be between brackets and in markdown italic (between asterisks). Property types: *str* (string), *dic* (dictionary), *int* (integer), *float*, *bool* (boolean).

The *parameter default* must be between brackets. If it's a text it's highly recommendable to put it between double quotes instead of single ones.

The *parameter range* (only for integer or float parameters) must be between square brackets following the next pattern: *[min-max|step]*.

*Description* is a string descriving the functionality of the parameter.

Preceded by the **Values:** expression, there can be a list with the possible value for each parameter. The patther must be the following (value description is not mandatory):  *value (description for value)*.

## JSON validator

Script for validating BioBB JSON Schemas for every package. Passing the name of the package, the absolute path to the JSON files of this package and the route to the JSON schema, all the JSON files will be automatically validated.

### Execution steps

#### Step 1: activate environment

Activate the environment where the BioBB package is loaded:

```Shell
conda activate biobb_env
```

#### Step 2: execute script

Run the python script passing the BioBB package to be parsed, the folder where the JSON files are stored and the path to the JSON schema:

```Shell
json_validator.py -p biobb_package -i path/to/json_files -s path/to/json_schema
```

```Shell
json_validator.py --package biobb_package --input path/to/json_files --schema path/to/json_schema
```

## Copyright & Licensing
This software has been developed in the [MMB group](http://mmb.irbbarcelona.org) at the [BSC](http://www.bsc.es/) & [IRB](https://www.irbbarcelona.org/) for the [European BioExcel](http://bioexcel.eu/), funded by the European Commission (EU H2020 [823830](http://cordis.europa.eu/projects/823830), EU H2020 [675728](http://cordis.europa.eu/projects/675728)).

* (c) 2015-2020 [Barcelona Supercomputing Center](https://www.bsc.es/)
* (c) 2015-2020 [Institute for Research in Biomedicine](https://www.irbbarcelona.org/)

Licensed under the
[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0), see the file LICENSE for details.

![](https://bioexcel.eu/wp-content/uploads/2019/04/Bioexcell_logo_1080px_transp.png "Bioexcel")