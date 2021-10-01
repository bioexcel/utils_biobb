#!/usr/bin/env python3

from pathlib import Path
import importlib
import argparse
import utils_biobb.common.file_utils as fu
import json
import jinja2


class PycompssGenerator:

    def __init__(self, package, output_dir):
        self.package_name = package
        self.output_dir = output_dir
        try:
            self.imported_package = importlib.import_module(package)
        except ImportError as ie:
            raise ie(f'{package} and biobb_adapters must be available in your environment')

    def launch(self):
        sub_paths_dict = fu.get_sub_paths_dict(biobb_name=self.package_name)
        for module_json in fu.get_file_path_list(dir_path=self.imported_package.__path__[0]):
            module_info = {}
            with open(module_json) as f_json:
                json_dict = json.load(f_json)
                module_name = module_json.name.rsplit('.')[0]
                module_info['module_name']= module_name
                module_info['iclass']= json_dict.get('name').split()[-1]
                module_info['module_dot_path'] = sub_paths_dict.get(module_name).replace('/', '.')+'.'+module_name
                module_info['mpi'] = json_dict.get('info').get('wrapped_software').get('multinode')
                #print(f'module_info["mpi"]: {module_info["mpi"]}')
                module_info['required'] = json_dict.get('required')
                module_info['arguments'] = []
                not_required = []
                for argument, value in json_dict.get('properties').items():
                    if argument == 'properties':
                        continue
                    if value.get('filetype').lower() == 'input':
                        if argument in module_info['required']:
                            module_info['arguments'].append((argument, 'FILE_IN'))
                        else:
                            not_required.append((argument, 'FILE_IN'))
                    else:
                        if argument in module_info['required']:
                            module_info['arguments'].append((argument, 'FILE_OUT'))
                        else:
                            not_required.append((argument, 'FILE_OUT'))

                module_info['arguments'].extend(not_required)

                adapter_dir_path = Path(self.output_dir).joinpath(Path(sub_paths_dict.get(module_name)))
                adapter_dir_path.mkdir(exist_ok=True, parents=True)
                adapter_file_path = adapter_dir_path.joinpath(module_name+'.py')
                with open(adapter_file_path, 'w') as adapter_file:
                    templateLoader = jinja2.FileSystemLoader(str(Path(__file__).parent))
                    templateEnv = jinja2.Environment(loader=templateLoader)
                    TEMPLATE_FILE = "pycompss_wrapper.tmpl"
                    # Exception for mdrun special template
                    if module_info['iclass'] in ['Mdrun', 'PmemdMDRun', 'SanderMDRun']:
                        TEMPLATE_FILE = "pycompss_wrapper_mdrun.tmpl"
                    template = templateEnv.get_template(TEMPLATE_FILE)
                    print(f'Writting {str(adapter_file_path)}')
                    adapter_file.write(template.render(module_info=module_info))


def main():
    parser = argparse.ArgumentParser(description="Creates pycompss adapters.",
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999),
                                     epilog='''Examples: \npycompss_generator.py -p biobb_package  -o path/to/biobb_adapters/biobb_adapters/pycompss''')
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--package_name', '-p', required=True, help='BioBB package name from where the json schemas will be taken.')
    required_args.add_argument('--output_pycompss_dir', '-o', required=True, help='Output path to the Pycompss adapters folder.')
    args = parser.parse_args()

    PycompssGenerator(package=args.package_name, output_dir=args.output_pycompss_dir).launch()


if __name__ == '__main__':
    main()