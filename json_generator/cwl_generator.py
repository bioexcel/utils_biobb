import argparse
import json
import yaml
import re
from importlib import import_module
from pathlib import Path, PurePath
from os import walk
from enum import Enum

class literal_unicode(str): pass

class MyDumper(yaml.Dumper):
    # HACK: insert blank lines between top-level objects
    # inspired by https://stackoverflow.com/a/44284819/3786245
    def write_line_break(self, data=None):
        
        super().write_line_break(data)

        if len(self.indents) == 1:
            super().write_line_break()

    def write_indent(self):
        indent = self.indent or 0
        if not self.indention or self.column > indent or (self.column == indent and not self.whitespace):
            self.write_line_break()

        if indent == 2:
            self.write_line_break()

        if self.column < indent:
            self.whitespace = True
            data = u' '*(indent-self.column)
            self.column = indent
            if self.encoding:
                data = data.encode(self.encoding)

            self.stream.write(data)

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
        """ gets formats in type list """

        flist = []
        aflist = []
        
        for frmt in ff:
            gr = re.match('\.\*\\\\\.(.*)\$', frmt['extension'])
            aflist.append(gr.groups()[0])
            flist.append("edam:" + frmt['edam'])

        return flist, aflist

    def getOutputDefault(self, accepted_formats):
        """ returns default output according to the accepted_formats list """

        return "system." + accepted_formats[0]

    def setConfText(self, conf_label, conf_dict):
        """ formats config texts """

        output = conf_label
        for attr, value in conf_dict.items():
            output = re.sub(r'\#\#' + attr + '\#\#', value, output)

        return output


    def formatInputs(self, inputs_dict, typ):
        """ returns CWL inputs properly formatted """

        inputs = {}

        position = 1
        for attr, value in inputs_dict.items():
            
            if value['filetype'] == "input":
                tp = "File" if typ == "req" else "File?"
            else:
                tp = "string"
            formats, accepted_formats = self.getFormat(value['file_formats'])

            sample = value['sample'] if value['sample'] else "null"
            ib = { "position": position, "prefix": "--" + attr } if typ == "req" else { "prefix": "--" + attr }

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
                "inputBinding": ib
            }

            if value['filetype'] == "output":
                inputs[attr]['default'] = self.getOutputDefault(accepted_formats)
            
            position = position + 1

        return inputs


    def returnInputs(self, tool_schema, tools, basename):
        """ returns inputs list """

        inputs_required = {}
        inputs_optional = {}

        for attr, value in tool_schema['properties'].items():
            if attr != 'properties': 
                if attr in tool_schema['required']:
                    inputs_required[attr] = value
                else:
                    inputs_optional[attr] = value

        inputs_r = self.formatInputs(inputs_required, 'req')
        inputs_o = self.formatInputs(inputs_optional, 'opt')

        inputs = {**inputs_r, **inputs_o}

        conf_label = "Advanced configuration options for ##name##"
        conf_doc = "Advanced configuration options for ##name##. This should be passed as a string containing a dict. The possible options to include here are listed under 'properties' in the ##name## documentation: ##documentation##"
        conf_doc_link = [item for item in tools if item['exec'] == basename][0]['docs']

        inputs['config'] = {
            "label": self.setConfText(conf_label, {"name": tool_schema['name']}),
            "doc": literal_unicode(self.setConfText(conf_doc, {"name": tool_schema['name'],"documentation": conf_doc_link})),
            "type": "string?",
            "inputBinding": {
                "prefix": "--config"
            }
        }

        return inputs

    def formatOutputs(self, outputs_dict, typ):
        """ returns CWL outputs properly formatted """

        outputs = {}

        for attr, value in outputs_dict.items():
            
            tp = "File" if typ == "req" else "File?"

            formats, accepted_formats = self.getFormat(value['file_formats'])

            outputs[attr] = {
                "label": value['description'],
                "doc": literal_unicode(value['description']),
                "type": tp,
                "format": formats,
                "outputBinding": {
                    "glob": "$(inputs." + attr + ")"
                }
            }

        return outputs

    def returnOutputs(self, tool_schema):
        """ returns outputs list """

        outputs_required = {}
        outputs_optional = {}

        for attr, value in tool_schema['properties'].items():
            if attr != 'properties' and value['filetype'] == 'output': 
                if attr in tool_schema['required']:
                    outputs_required[attr] = value
                else:
                    outputs_optional[attr] = value

        outputs_r = self.formatOutputs(outputs_required, 'req')
        outputs_o = self.formatOutputs(outputs_optional, 'opt')

        outputs = {**outputs_r, **outputs_o}

        return outputs


    def literal_unicode_representer(self, dumper, data):
        """ returns a literal unicode """

        return dumper.represent_scalar(u'tag:yaml.org,2002:str', data, style='|')

    def generateCWL(self, tool_schema, pckg_schema, basename):
        """ generates cwl """

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
            "inputs": self.returnInputs(tool_schema, pckg_schema['tools'], basename),
            "outputs": self.returnOutputs(tool_schema),
            "$namespaces": {
                "edam": "http://edamontology.org/"
            },
            "$schemas": [
                "https://raw.githubusercontent.com/edamontology/edamontology/master/EDAM_dev.owl"
            ]
        }

        yaml.add_representer(literal_unicode, self.literal_unicode_representer)

        # get cwl output file path
        path = PurePath(self.output_path).joinpath(basename + '.cwl')

        # save object to cwl file
        with open(path, 'w+') as yml_file:
            yml_file.write('#!/usr/bin/env cwl-runner\n')
            #yaml.dump(object_cwl, yml_file, Dumper=MyDumper, sort_keys=False)
            yaml.dump(object_cwl, yml_file, sort_keys=False)


    def launch(self):
        """ launch function for CWLGenerator """

        # get json schemas
        json_pckg, json_files = self.getJSONSchemas()
        json_pckg_path = PurePath(self.input_path).joinpath(json_pckg)
        pckg_schema = self.parseJSON(json_pckg_path)

        for json_file in json_files:
            json_file_path = PurePath(self.input_path).joinpath(json_file)

            tool_schema = self.parseJSON(json_file_path)
            self.generateCWL(tool_schema, pckg_schema, PurePath(json_file_path).stem)

            print(str(PurePath(self.output_path).joinpath(PurePath(json_file_path).stem + '.cwl')) + " file saved")


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
