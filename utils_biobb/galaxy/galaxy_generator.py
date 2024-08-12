from pathlib import Path
import importlib
import argparse
import utils_biobb.common.file_utils as fu
import json
import jinja2
import re
from typing import Tuple
import yaml
import shutil
from pprint import pprint


class GalaxyGenerator:
    def __init__(self, package, output_dir, debug=False):
        self.package_name = package
        self.output_dir = output_dir
        self.debug = debug
        try:
            self.imported_package = importlib.import_module(package)
        except ImportError:
            raise ImportError(f'{package} and biobb_adapters must be available in your environment')

    def _create_paths(self, output_path: Path) -> Tuple[Path, Path, Path]:
        # Main plugin folder
        dir_path = Path(output_path).joinpath(self.package_name.lower())
        dir_path.mkdir(exist_ok=True, parents=True)
        # Testdata folder
        testdata_dir_path = dir_path.joinpath("test-data")
        testdata_dir_path.mkdir(exist_ok=True, parents=True)
        # Json file
        shed_file_path = dir_path.joinpath(".shed.yml")

        return dir_path, testdata_dir_path, shed_file_path

    def _get_test_file_path(self, module_name: str, parameter_orig_path: str, sub_paths_dict: dict) -> Path:
        # Get test file path
        sub_folder = "reference"
        if "test_data_dir" in parameter_orig_path:
            sub_folder = "data"

        subpackage = sub_paths_dict.get(module_name, '').split('/')[-1]
        if self.package_name == "biobb_dna" and "correlation" in subpackage:
            subpackage = "correlation"
        elif self.package_name == "biobb_pmx" and "pmxbiobb" in subpackage:
            subpackage = subpackage.replace("pmxbiobb", "pmx")

        package_path = self.imported_package.__path__[0]

        test_file_name = parameter_orig_path.split('/')[-1]

        return Path(package_path, f"test/{sub_folder}/{subpackage}/{test_file_name}")

    def _escape_string_quotes(self, string: str) -> str:
        return string.replace('"', "\'").replace("'", "\'")

    def launch(self):
        # Create paths
        dir_path, testdata_dir_path, shed_file_path = self._create_paths(self.output_dir)
        # Load block json file
        block_json_file_path = Path(self.imported_package.__path__[0], f"json_schemas/{self.package_name}.json")
        with open(block_json_file_path) as json_file:
            block_json_dict = json.load(json_file)
        # Preloading jinja2 templates
        templateLoader = jinja2.FileSystemLoader(str(Path(__file__).parent))
        templateEnv = jinja2.Environment(loader=templateLoader)
        # Write shed file
        with open(shed_file_path, 'w') as shed_file:
            shed_template = "templates/shed_template.yml"
            template = templateEnv.get_template(shed_template)
            print(f'Writting {str(shed_file_path)}')
            shed_file.write(template.render(**block_json_dict))
        # Load test config yaml file
        test_config_file_path = Path(self.imported_package.__path__[0], "test/conf.yml")
        with open(test_config_file_path) as test_config_file:
            test_config_dict = yaml.safe_load(test_config_file)

        # Get paths
        sub_paths_dict = fu.get_sub_paths_dict(biobb_name=self.package_name)
        if self.debug:
            pprint(sub_paths_dict)
        # Create each xml file
        for module_json in fu.get_file_path_list(dir_path=self.imported_package.__path__[0]):

            print(f'Processing {module_json}')
            with open(module_json) as f_json:
                json_dict = json.load(f_json)
                module_name = module_json.name.rsplit('.')[0]
                module_info = {}
                module_info['block_info'] = block_json_dict
                module_info['module_name'] = module_name
                module_info['module_name_capitalized'] = ''.join([word[0].upper()+word[1:] for word in module_name.split('_')])
                module_info['long_description'] = self._escape_string_quotes(json_dict.get('description'))
                module_info['short_description'] = self._escape_string_quotes(json_dict.get('title'))
                module_info['iclass'] = json_dict.get('name').split()[-1]
                module_info['module_dot_path'] = sub_paths_dict.get(module_name, '').replace('/', '.')+'.'+module_name
                module_info['mpi'] = json_dict.get('info').get('wrapped_software').get('multinode')
                module_info['required'] = json_dict.get('required')
                module_info['docker_image'] = block_json_dict.get('docker', '').replace('https://', '')
                module_info['inputs'] = []
                module_info['outputs'] = []
                module_info['properties'] = []

                for argument, value in json_dict.get('properties').items():
                    if argument == 'properties':
                        continue
                    argument_dict = {}
                    argument_dict['name'] = argument
                    argument_dict['required'] = argument in module_info['required']
                    argument_dict['description'] = self._escape_string_quotes(value['description'])
                    argument_dict['extensions'] = ["".join(re.split("[^A-Za-z0-9]+", ext)) for ext in value.get('enum')]
                    if value.get('filetype').lower() == 'input':
                        module_info['inputs'].append(argument_dict)
                    else:
                        module_info['outputs'].append(argument_dict)
            # Tests
            test_info = test_config_dict.get(module_name, {})
            module_info['test_info'] = test_info
            module_info['test_info']['refs'] = {}
            # Write test config json file
            properties_dict = test_info.get('properties', {})
            test_config_file_path = testdata_dir_path.joinpath(f"config_{module_name}.json")
            with open(test_config_file_path, 'w') as test_config_file:
                print(f'Writting {str(test_config_file_path)}')
                json.dump(properties_dict, test_config_file, indent=4)

            for param_name, param_path in test_info.get("paths", {}).items():
                if param_name.startswith('ref_'):
                    module_info['test_info']['refs'][param_name.replace('ref_', '')] = {'file': param_path.split('/')[-1]}
                    ref_file_path = self._get_test_file_path(module_name, param_path, sub_paths_dict)
                    module_info['test_info']['refs'][param_name.replace('ref_', '')]['size'] = int(ref_file_path.stat().st_size)
                    module_info['test_info']['refs'][param_name.replace('ref_', '')]['delta'] = int(module_info['test_info']['refs'][param_name.replace('ref_', '')]['size']/4)
                    continue
                if param_name.startswith('input_'):
                    input_file_path = self._get_test_file_path(module_name, param_path, sub_paths_dict)
                    print(f"Copying {input_file_path} to {testdata_dir_path.joinpath(param_path.split('/')[-1])}")
                    shutil.copy(input_file_path, testdata_dir_path.joinpath(param_path.split('/')[-1]))
                module_info['test_info'][param_name] = param_path.split('/')[-1]

            # Write adapter file
            adapter_file_path = dir_path.joinpath(f"biobb_{module_name}.xml")
            with open(adapter_file_path, 'w') as adapter_file:
                galaxy_block_template = "templates/galaxy_block.xml"
                template = templateEnv.get_template(galaxy_block_template)
                print(f'Writting {str(adapter_file_path)}')
                adapter_file.write(template.render(**module_info))


def main():
    parser = argparse.ArgumentParser(description="Creates Galaxy adapters.",
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999),
                                     epilog='''Examples: \ngalaxy_generator.py -p biobb_package  -o path/to/biobb_adapters/biobb_adapters/galaxy''')
    parser.add_argument('--debug', '-d', action='store_true', required=False, help='Debug printing file')
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--package_name', '-p', required=True, help='BioBB package name from where the json schemas will be taken.')
    required_args.add_argument('--output_dir', '-o', required=True, help='Output path to the Galaxy adapters folder.')
    args = parser.parse_args()

    GalaxyGenerator(package=args.package_name, output_dir=args.output_dir, debug=args.debug).launch()


if __name__ == '__main__':
    main()
