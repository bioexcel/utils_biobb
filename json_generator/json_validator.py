import argparse
import json
from os import walk
from pathlib import Path, PurePath
from jsonschema import validate, exceptions

class JSONSchemaValidator():

    def __init__(self, package, input_path, input_schema, **kwargs):

        self.package = package

        if not Path(input_path).exists():
            raise SystemExit('Unexisting input path')

        self.input_path = input_path

        if not Path(input_schema).exists():
            raise SystemExit('Unexisting input schema')

        self.input_schema = input_schema
    

    def getJSONSchemas(self):
        """ returns all the JSON Schemas files of the package and the package json file """

        # get all files in json_schemas folder
        json_files = []
        for (dirpath, dirnames, filenames) in walk(self.input_path):
            json_files.extend(filenames)
            break

        if(self.package + '.json' in json_files): 
            json_files.remove(json_pckg)

        return json_files

    def launch(self):
        """ launch function for JSONSchemaValidator """

        # Opening JSON schema 
        with open(self.input_schema) as json_file: 
            schema = json.load(json_file) 

        json_files = self.getJSONSchemas()
        for json_file in json_files:
            json_file_path = PurePath(self.input_path).joinpath(json_file)

            with open(json_file_path) as js_f_p: 
                instance = json.load(js_f_p) 

            try:
                validate(instance, schema)
            except exceptions.ValidationError as e:
                print("Error in " + str(json_file_path))
                print(e)
                exit(0)

            print(str(json_file_path) + " is valid")


def main():
    parser = argparse.ArgumentParser(description="Validates json_schemas for a given BioBB package.", 
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999),
                                     epilog='''Examples: \njson_validator.py -p biobb_package -i path/to/json_files -s path/to/json_schema\njson_validator.py --package biobb_package --input path/to/json_files --schema path/to/json_schema''')
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--package', '-p', required=True, help='BioBB package from where the json schemas will be taken.')
    required_args.add_argument('--input', '-i', required=True, help='Path to the folder from where the json files will be taken.')
    required_args.add_argument('--schema', '-s', required=True, help='JSON Schema file.')

    args = parser.parse_args()

    JSONSchemaValidator(package=args.package, input_path=args.input, input_schema=args.schema).launch()


if __name__ == '__main__':
    main()
