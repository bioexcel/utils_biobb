from pathlib import Path
from typing import Dict, List, Any
import importlib
import argparse
import utils_biobb.common.file_utils as fu
import json
import jinja2
import pprint
import re


class HorusGenerator:

    def __init__(self, package, output_dir):
        self.package_name = package
        self.output_dir = output_dir
        try:
            self.imported_package = importlib.import_module(package)
        except ImportError:
            raise ImportError(f'{package} and biobb_adapters must be available in your environment')

    def launch(self):
        sub_paths_dict = fu.get_sub_paths_dict(biobb_name=self.package_name)
        for module_json in fu.get_file_path_list(dir_path=self.imported_package.__path__[0]):
            print(f'Processing {module_json}')
            module_info = {}
            with open(module_json) as f_json:
                json_dict = json.load(f_json)
                module_name = module_json.name.rsplit('.')[0]
                module_info['module_name'] = module_name
                module_info['iclass'] = json_dict.get('name').split()[-1]
                module_info['module_dot_path'] = sub_paths_dict.get(module_name, '').replace('/', '.')+'.'+module_name
                module_info['mpi'] = json_dict.get('info').get('wrapped_software').get('multinode')
                module_info['required'] = json_dict.get('required')
                module_info['inputs'] = []
                module_info['outputs'] = []
                module_info['properties'] = []

                not_required = []
                # pprint.pprint(json_dict)
                # pprint.pprint(module_info)
                for argument, value in json_dict.get('properties').items():
                    if argument == 'properties':
                        module_info['properties'] = list(value.get('properties'))
                        continue
                    argument_dict = {}
                    argument_dict['name'] = argument
                    argument_dict['required'] = argument in module_info['required']
                    argument_dict['description'] = value.get('description')
                    argument_dict['extensions'] = ["".join(re.split("[^A-Za-z0-9]+", ext)) for ext in value.get('enum')]

                    if value.get('filetype').lower() == 'input':
                        module_info['inputs'].append(argument_dict)
                    else:
                        module_info['outputs'].append(argument_dict)

                pprint.pprint(module_info)
                # module_info['arguments'].extend(not_required)

                adapter_dir_path = Path(self.output_dir).joinpath(Path(sub_paths_dict.get(module_name, '')))
                adapter_dir_path.mkdir(exist_ok=True, parents=True)
                adapter_file_path = adapter_dir_path.joinpath(module_name+'.py')
                with open(adapter_file_path, 'w') as adapter_file:
                    templateLoader = jinja2.FileSystemLoader(str(Path(__file__).parent))
                    templateEnv = jinja2.Environment(loader=templateLoader)
                    TEMPLATE_FILE = "templates/horus_block.jpy"
                    # Exception for mdrun special template
                    # if module_info['iclass'] in ['Mdrun', 'PmemdMDRun', 'SanderMDRun']:
                    #     TEMPLATE_FILE = "pycompss_wrapper_mdrun.tmpl"
                    template = templateEnv.get_template(TEMPLATE_FILE)
                    print(f'Writting {str(adapter_file_path)}')
                    adapter_file.write(template.render(**module_info))


def main():
    parser = argparse.ArgumentParser(description="Creates pycompss adapters.",
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999),
                                     epilog='''Examples: \npycompss_generator.py -p biobb_package  -o path/to/biobb_adapters/biobb_adapters/pycompss''')
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--package_name', '-p', required=True, help='BioBB package name from where the json schemas will be taken.')
    required_args.add_argument('--output_dir', '-o', required=True, help='Output path to the Pycompss adapters folder.')
    args = parser.parse_args()

    HorusGenerator(package=args.package_name, output_dir=args.output_dir).launch()


if __name__ == '__main__':
    main()
