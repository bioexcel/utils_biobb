import argparse
import json
from jsonschema import validate, exceptions#, Draft7Validator

class JSONSchemaValidator():

    def __init__(self, input_package, input_schema, **kwargs):

        # TODO CHECKS!!!

        self.input_package = input_package

        self.input_schema = input_schema
    

    def launch(self):
        """ launch function for JSONSchemaValidator """

        # Opening JSON file 
        with open(self.input_schema) as json_file: 
            schema = json.load(json_file) 

        with open(self.input_package) as json_file: 
            instance = json.load(json_file) 

        try:
            validate(instance, schema)
        except exceptions.ValidationError as e:
            print(e)
            #print(e.message)
            #print(e.schema)
            #print(e.instance)
            exit(0)

        print("ok")

        """v = Draft7Validator(schema)
        errors = sorted(v.iter_errors(instance), key=lambda e: e.path)

        for error in errors:
            print(error.message)"""


def main():
    parser = argparse.ArgumentParser(description="Validates json_schemas for a given BioBB package.", 
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999),
                                     epilog='''Examples: \njson_validator.py -p biobb_package -s path/to/json_schema\njson_validator.py --package biobb_package --schema path/to/json_schema''')
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--package', '-p', required=True, help='[TODO PACKAGE]BioBB package to be validated.')
    required_args.add_argument('--schema', '-s', required=True, help='JSON Schema file.')

    args = parser.parse_args()

    JSONSchemaValidator(input_package=args.package, input_schema=args.schema).launch()


if __name__ == '__main__':
    main()
