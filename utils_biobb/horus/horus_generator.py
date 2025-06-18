from pathlib import Path
import importlib
import argparse
import utils_biobb.common.file_utils as fu
import json
import jinja2
import re
import shutil
from typing import Tuple


class HorusGenerator:

    def __init__(self, package, output_dir):
        self.package_name = package
        self.output_dir = output_dir
        try:
            self.imported_package = importlib.import_module(package)
        except ImportError:
            raise ImportError(f'{package} and biobb_adapters must be available in your environment')

    def _default_value(self, value):
        if value == 'null':
            return None
        if isinstance(value, str):
            return f"\"{value}\""
        return value

    def _escape_string_quotes(self, string: str) -> str:
        return string.replace('"', "\'").replace("'", "\'")

    def __str_type_to_horus_type(self, str_type: str) -> str:
        str_type = str_type.lower()
        if str_type == 'str':
            str_type = 'STRING'
        if str_type == 'int':
            str_type = 'INTEGER'
        if str_type == 'bool':
            str_type = 'BOOLEAN'
        if str_type == 'dict':
            str_type = 'OBJECT'
        if str_type == 'object':
            str_type = 'OBJECT'
        if str_type == 'list':
            str_type = 'LIST'
        if str_type == 'array':
            str_type = 'LIST'
        return f"VariableTypes.{str_type.upper()}"

    def _create_plugin_paths(self, output_path: Path) -> Tuple[Path, Path, Path, Path]:
        plugin_name = self.package_name.lower()
        # Main plugin folder
        plugin_dir_path = Path(output_path).joinpath(plugin_name)
        plugin_dir_path.mkdir(exist_ok=True, parents=True)
        # Config folder
        plugin_dir_path.joinpath("config").mkdir(exist_ok=True, parents=True)
        # Json file
        json_dir_path = plugin_dir_path.joinpath("config").joinpath(f"{plugin_name}.json")
        # Deps folder
        plugin_dir_path.joinpath("deps").mkdir(exist_ok=True, parents=True)
        # Include folder
        include_dir_path = plugin_dir_path.joinpath("Include")
        include_dir_path.mkdir(exist_ok=True, parents=True)
        # Pages folder
        plugin_dir_path.joinpath("Pages").mkdir(exist_ok=True, parents=True)
        # Meta file
        meta_file_path = plugin_dir_path.joinpath("plugin.meta")
        # Plugin python file
        plugin_file_path = plugin_dir_path.joinpath("plugin.py")
        return include_dir_path, json_dir_path, meta_file_path, plugin_file_path

    def launch(self):
        # Create plugin paths
        include_dir_path, json_dir_path, meta_file_path, plugin_file_path = self._create_plugin_paths(Path(self.output_dir))
        # Loading block json file
        block_json_file_path = Path(self.imported_package.__path__[0], f"json_schemas/{self.package_name}.json")
        with open(block_json_file_path) as json_file:
            block_json_dict = json.load(json_file)
        # Preloading jinja2 templates
        templateLoader = jinja2.FileSystemLoader(str(Path(__file__).parent))
        templateEnv = jinja2.Environment(loader=templateLoader)
        # Write plugin json file
        with open(json_dir_path, 'w') as json_file:
            horus_json_template = "templates/horus_json.json"
            template = templateEnv.get_template(horus_json_template)
            print(f'Writting {str(json_dir_path)}')
            json_file.write(template.render())
        # Write plugin meta file
        with open(meta_file_path, 'w') as meta_file:
            horus_meta_template = "templates/horus_meta.meta"
            template = templateEnv.get_template(horus_meta_template)
            print(f'Writting {str(meta_file_path)}')
            meta_file.write(template.render(**block_json_dict))
        # Write plugin python file
        sub_paths_dict = fu.get_sub_paths_dict(biobb_name=self.package_name)
        dot_paths_dict = {module_name: dot_path.replace('/', '.')+'.'+module_name for module_name, dot_path in sub_paths_dict.items()}
        with open(plugin_file_path, 'w') as plugin_file:
            horus_plugin_template = "templates/horus_plugin.jpy"
            template = templateEnv.get_template(horus_plugin_template)
            print(f'Writting {str(plugin_file_path)}')
            plugin_file.write(template.render(block_name=block_json_dict['_id'], dot_paths_dict=dot_paths_dict))

        for module_json in fu.get_file_path_list(dir_path=self.imported_package.__path__[0]):
            print(f'Processing {module_json}')
            module_info = {}
            with open(module_json) as f_json:
                json_dict = json.load(f_json)
                module_name = module_json.name.rsplit('.')[0]
                module_info['module_name'] = module_name
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
                module_info['readthedocs'] = f"{block_json_dict.get('readthedocs', '')}"

                for argument, value in json_dict.get('properties').items():
                    if argument == 'properties':
                        module_info['properties'] = [{**prop_dict, "horus_description": self._escape_string_quotes(prop_dict.get('description')), "name": prop_name, "horus_type": self.__str_type_to_horus_type(prop_dict.get('type')), "horus_default": self._default_value(prop_dict.get('default'))} for prop_name, prop_dict in value.get('properties').items()]
                        for property_dict in module_info['properties']:
                            if property_dict.get('horus_type') == 'VariableTypes.LIST' and isinstance(property_dict.get('horus_default'), str):
                                list_str = property_dict['horus_default'].replace('[', '').replace(']', '').replace("'", '').replace('"', '').replace(' ', '')
                                property_dict['horus_default'] = list_str.split(',')
                        continue

                    argument_dict = {}
                    argument_dict['name'] = argument
                    argument_dict['required'] = argument in module_info['required']
                    # print(f"Processing {argument}")
                    # print(f"description: {value['description']}")
                    # print(f"escape: {self._escape_string_quotes(value['description'])}")
                    argument_dict['description'] = self._escape_string_quotes(value['description'])
                    argument_dict['extensions'] = ["".join(re.split("[^A-Za-z0-9]+", ext)) for ext in value.get('enum')]

                    if value.get('filetype').lower() == 'input':
                        module_info['inputs'].append(argument_dict)
                    else:
                        module_info['outputs'].append(argument_dict)

                adapter_dir_path = Path(include_dir_path).joinpath(Path(sub_paths_dict.get(module_name, '')))
                adapter_dir_path.mkdir(exist_ok=True, parents=True)
                adapter_file_path = adapter_dir_path.joinpath(module_name+'.py')
                with open(adapter_file_path, 'w') as adapter_file:
                    horus_block_template = "templates/horus_block.jpy"
                    template = templateEnv.get_template(horus_block_template)
                    print(f'Writting {str(adapter_file_path)}')
                    adapter_file.write(template.render(**module_info))
        # Create zip file
        print(f'Writting {str(Path(self.output_dir).joinpath(self.package_name+".hp"))}')
        shutil.make_archive(str(Path(self.output_dir).joinpath(self.package_name)), 'zip', str(Path(self.output_dir).joinpath(self.package_name)))
        shutil.move(str(Path(self.output_dir).joinpath(self.package_name+'.zip')), str(Path(self.output_dir).joinpath(self.package_name+'.hp')))
        shutil.rmtree(str(Path(self.output_dir).joinpath(self.package_name)))


def main():
    parser = argparse.ArgumentParser(description="Creates Horus adapters.",
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999),
                                     epilog='''Examples: \nhorus_generator.py -p biobb_package  -o path/to/biobb_adapters/biobb_adapters/horus''')
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--package_name', '-p', required=True, help='BioBB package name from where the json schemas will be taken.')
    required_args.add_argument('--output_dir', '-o', required=True, help='Output path to the Horus adapters folder.')
    args = parser.parse_args()

    HorusGenerator(package=args.package_name, output_dir=args.output_dir).launch()


if __name__ == '__main__':
    main()
