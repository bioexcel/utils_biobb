import argparse
import json
import yaml
import re
from importlib import import_module
from pathlib import Path, PurePath
from os import walk

class literal_unicode(str): pass

class CWLGenerator():

    def __init__(self, package, input_path, output_path, **kwargs):

        self.package = package

        # check if output_path exists
        if not Path(input_path).exists():
            raise SystemExit('Unexisting input path')

        self.input_path = input_path

        # check if output_path exists
        if not Path(output_path).exists():
            raise SystemExit('Unexisting output path')

        self.output_path = output_path
    
    def getJSONSchemas(self):
        """ returns all the JSON Schemas files of the package and the package json file """

        # get all files in json_schemas folder
        json_files = []
        for (dirpath, dirnames, filenames) in walk(self.input_path):
            json_files.extend(filenames)
            break

        if(self.package + '.json' in json_files): 
            json_pckg = self.package + '.json'
            json_files.remove(json_pckg)

        return json_pckg, json_files

    def parseJSON(self, json_file_path):
        """ parses json to python object """

        with open(json_file_path) as json_file: 
            schema = json.load(json_file) 

        return schema

    def getFormat(self, ff):
        flist = []
        aflist = []
        
        for frmt in ff:
            gr = re.match('\.\*\\\\\.(.*)\$', frmt['extension'])
            aflist.append(gr.groups()[0])
            flist.append("edam:" + frmt['edam'])

        return flist, aflist

    def returnInputs(self, tool_schema):

        inputs_required = {}
        inputs_optional = {}

        for attr, value in tool_schema['properties'].items():
            if attr != 'properties': 
                if attr in tool_schema['required']:
                    inputs_required[attr] = value
                else:
                    inputs_optional[attr] = value

        inputs = {}

        # TODO: put the content of the 2 fors in a new function and check if required or not

        position = 1
        for attr, value in inputs_required.items():
            
            if value['filetype'] == "input":
                tp = "File"
            else:
                tp = "string"

            formats, accepted_formats = self.getFormat(value['file_formats'])

            inputs[attr] = {
                "label": value['description'],
                "doc": literal_unicode(value['description'] + "\n"
                    + "Type: " + value['type'] + "\n"
                    + "File type: " + value['filetype'] + "\n"
                    + "Accepted formats: " + ', '.join(accepted_formats) + "\n"
                    + "Example file: " + value['sample']
                    ),
                "type": tp,
                "format": formats,
                "inputBinding": {
                    "position": position,
                    "prefix": "--" + attr
                }
            }
            
            position = position + 1

        for attr, value in inputs_optional.items():
            
            if value['filetype'] == "input":
                tp = "File?"
            else:
                tp = "string"

            formats, accepted_formats = self.getFormat(value['file_formats'])

            sample = value['sample'] if value['sample'] else "null"

            inputs[attr] = {
                "label": value['description'],
                "doc": literal_unicode(value['description'] + "\n"
                    + "Type: " + value['type'] + "\n"
                    + "File type: " + value['filetype'] + "\n"
                    + "Accepted formats: " + ', '.join(accepted_formats) + "\n"
                    + "Example file: " + sample
                    ),
                "type": tp,
                "format": formats,
                "inputBinding": {
                    "prefix": "--" + attr
                }
            }

        #print(inputs_required)
        #print(inputs_optional)

        return inputs

        #print(json.dumps(inputs, indent=4))

        """label: Path to GRO file
            doc: |
              Path to the input GROMACS structure GRO file.
              Type: str
              File type: input
              Accepted formats: gro
              Example file:
                https://github.com/bioexcel/biobb_md/raw/master/biobb_md/test/data/gromacs/grompp.gro
            type: File
            format: edam:format_GROMACS_GRO
            inputBinding:
              position: 1
              prefix: --input_gro_path"""



    def literal_unicode_representer(self, dumper, data):
        return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')

    def generateCWL(self, tool_schema, pckg_schema, basename):
        """ generates cwl """

        #print(pckg_schema['tools'])

        object_cwl = {
            "tprcwlVersion": "v1.0",
            "class": "CommandLineTool",
            "label": tool_schema['title'],
            "doc": literal_unicode(tool_schema['description']),
            "baseCommand": basename,
            "hints": {
                "DockerRequirement": {
                    "dockerPull": 'quay.io/biocontainers/' + pckg_schema['_id'] + ':' + pckg_schema['version'] + '--py_0'
                }
            },
            "inputs": self.returnInputs(tool_schema),
            "outputs": [],
            "$namespaces": {
                "edam": "http://edamontology.org/"
            },
            "$schemas": [
                "https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl"
            ]
        }

        yaml.add_representer(literal_unicode, self.literal_unicode_representer)

        #print(object_cwl)

        # get cwl output file path
        path = PurePath(self.output_path).joinpath(basename + '.cwl')

        # save object to cwl file
        with open(path, 'w+') as yml_file:
            yml_file.write('#!/usr/bin/env cwl-runner\n')
            yaml.dump(object_cwl, yml_file, sort_keys=False)


    def launch(self):
        """ launch function for CWLGenerator """

        # get json schemas
        json_pckg, json_files = self.getJSONSchemas()
        json_pckg_path = PurePath(self.input_path).joinpath(json_pckg)
        pckg_schema = self.parseJSON(json_pckg_path)

        for json_file in json_files:
            json_file_path = PurePath(self.input_path).joinpath(json_file)

            ###########################
            # HARCODED!!!!!
            if 'grompp' in str(json_file_path):
                tool_schema = self.parseJSON(json_file_path)
                self.generateCWL(tool_schema, pckg_schema, PurePath(json_file_path).stem)
            ##########################

        #print(package)
        exit()

        # Opening SINGLE JSON file (TODO FOR EACH SCHEMA IN PACKAGE)
        







        exit()

        # TODO FOR EACH SCHEMA IN PACKAGE
        basename = PurePath(self.input_package).stem

        path = PurePath(self.output_path).joinpath(basename + '.yaml')

        yml_file = open(path, 'w+')

        yaml.dump(schema, yml_file, allow_unicode=True)



def main():
    parser = argparse.ArgumentParser(description="Creates CWL adapters from given json schema.", 
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999),
                                     epilog='''Examples: \ncwl_generator.py -p biobb_package -i path/to/json_schemas -o path/to/cwl_adapters\ncwl_generator.py --package biobb_package --input path/to/json_schemas --output path/to/cwl_adapters''')
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--package', '-p', required=True, help='BioBB package from where the json schemas will be taken.')
    required_args.add_argument('--input', '-i', required=True, help='Path to the folder from where the json schemas will be taken.')
    required_args.add_argument('--output', '-o', required=True, help='Output path to the CWL adapters folder.')

    args = parser.parse_args()

    CWLGenerator(package=args.package, input_path=args.input, output_path=args.output).launch()


if __name__ == '__main__':
    main()
