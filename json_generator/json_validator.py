"""import argparse
import re
import json
from importlib import import_module
from difflib import SequenceMatcher
from pathlib import Path, PurePath
from os import walk"""
import argparse
import json
from jsonschema import validate, exceptions

regex_sphinx_link = '\`(.+)\<(.+)\>\`\_'
regex_parameters = '(\w*)\ *(?:\()(\w*)(?:\)):?\ *(\(\w*\):)?\ *(.*?)(?:\.)\ *(?:File type:\ *)(\w+)\.\ *(\`(?:.+)\<(.*)\>\`\_\.)?\ *(?:Accepted formats:\ *)(.+)(?:\.)?'
regex_param_value = '(\w*)\ *(?:(?:\()(.*)(?:\)))?'
#regex_property_values = '(?:\*\ *\*\*)(.*)(?:\*\*)\ *(?:\(\*)(\w*)(?:\*\))\ *\-\ *(?:\()(.*?)(?:\))\ *(?:(?:\[)(\d+(?:\.\d+)?)\-(\d+(?:\.\d+)?)(?:\|)?(\d+(?:\.\d+)?)?(?:\]))?\ *(?:(?:\[)(.*)(?:\]))?\ *(.*)?(?:Values:\ *)(.+)(?:\.)?'
regex_property_values = '(?:\*\ *\*\*)(.*)(?:\*\*)\ *(?:\(\*)(\w*)(?:\*\))\ *\-\ ?(?:\()(.*)(?:\))\ *(?:(?:\[)(\w*)\-(\w*)(?:\|)?(\w*)?(?:\]))?\ *(?:(?:\[)(.*)(?:\]))?\ *(.*)\ ?(?:Values:\ *)(.+)(?:\.)?'
regex_property_non_values = '(?:\*\ *\*\*)(.*)(?:\*\*)\ *(?:\(\*)(\w*)(?:\*\))\ *\-\ *(?:\()(.*?)(?:\))\ *(?:(?:\[)(\d+(?:\.\d+)?)\-(\d+(?:\.\d+)?)(?:\|)?(\d+(?:\.\d+)?)?(?:\]))?\ *(?:(?:\[)(.*)(?:\]))?\ *(.*)?'
#################
#regex_property_values = '(?:\*\s*\*\*)(.*)(?:\*\*)\s*(?:\(\*)(\w*)(?:\*\))\s*\-\s*(?:\()(.*)(?:\))\s*(?:(?:\[)(\w*)\-(\w*)(?:\|)?(\w*)?(?:\]))?\s*(?:(?:\[)(.*)(?:\]))?\s([a-zA-Z0-9_\- ().&?,!;]+)(?:\s|\.)+(?:(?:Values:)(.+))?'
###################
regex_prop_value = '([a-zA-Z0-9_\-]+)\ *(?:(?:\()(.*)?(?:\)))?'
regex_info = '\*\ *(.*)'
regex_info_item = '(.*?)\:(?:\ *)(.*)'

class JSONSchemaValidator():

    def __init__(self, input_package, input_schema, **kwargs):

        # TODO CHECKS!!!

        self.input_package = input_package

        self.input_schema = input_schema

        """self.input_package = input_package

        TODOS



        # check if output_path exists
        if not Path(output_path).exists():
            raise SystemExit('Unexisting output path')

        # check if output_path has correct structure
        if not input_package in output_path:
            raise SystemExit('Incorrect output path. The structure must be: path/biobb_package/biobb_package')

        self.output_path = PurePath(output_path).joinpath('json_schemas')

        if not Path(self.output_path).exists():
            raise SystemExit('Incorrect output path. The structure must be: path/biobb_package/biobb_package')"""

    

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
            #print(e.instance)
            #print(e.schema)
            exit(0)

        print("ok")

        """try:
            validate(instance={"name" : "Eggs", "price" : "34.99"}, schema=schema)
        except:
            print(exceptions.ValidationError.message)"""

        """instance = {"name" : "Eggs", "price" : 34.99}
        v = Draft7Validator(schema)
        errors = sorted(v.iter_errors(instance), key=lambda e: e.path)

        for error in errors:
            print(error.message)"""

        # import package
        """packages = import_module(self.input_package)

        # remove old JSON files
        self.cleanOutputPath()

        # get documentation of python files
        for package in packages.__all__:
            # for every package import all modules
            modules = import_module(self.input_package + '.' + package)
            for module in modules.__all__:

                # json schemas
                # import single module
                mod = import_module(self.input_package + '.' + package + '.' + module)

                # get class name through similarity with module name
                sel_class = ''
                similarity = 0;
                for item in dir(mod):
                    if ( item[0].isupper() and 
                    not item.startswith('Path') and 
                    not item.startswith('Pure') and
                    not item.startswith('check_') ):
                        s = self.similar_string(item, module)
                        if s > similarity:
                            sel_class = item
                            similarity = s

                # exceptions:
                if sel_class == "KMeans" and module == "k_means": 
                    sel_class = "KMeansClustering"
                if sel_class == "KMeans" and module == "dbscan": 
                    sel_class = "DBSCANClustering"
                if sel_class == "AgglomerativeClustering": 
                    sel_class = "AgglClustering"
                if sel_class == "SpectralClustering": 
                    sel_class = "SpecClustering"

                # get class documentation
                klass = getattr(mod, sel_class)
                doclines = klass.__doc__.splitlines()

                object_schema = self.parseDocs(doclines, module)

                self.saveJSONFile(module, object_schema)"""


def main():
    parser = argparse.ArgumentParser(description="Validates json_schemas for given BioBB package.", 
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999),
                                     epilog='''Examples: \njson_generator.py -p biobb_package -o path/to/biobb_package/biobb_package\njson_generator.py --package biobb_package --output path/to/biobb_package/biobb_package''')
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--package', '-p', required=False, help='[TODO PACKAGE]BioBB package to be validated.')
    required_args.add_argument('--schema', '-s', required=False, help='JSON Schema file.')

    args = parser.parse_args()

    JSONSchemaValidator(input_package=args.package, input_schema=args.schema).launch()


if __name__ == '__main__':
    main()
