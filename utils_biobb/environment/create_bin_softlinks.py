#!/usr/bin/env python3

from pathlib import Path
import importlib
import argparse
import utils_biobb.common.file_utils as fu


class BinSoftlinkGenerator:

    def __init__(self, package, output_dir):
        self.package_name = package
        self.output_dir = output_dir
        try:
            self.imported_package = importlib.import_module(package)
        except ImportError as ie:
            raise ie(f'{package} and biobb_adapters must be available in your environment')

    def launch(self):
        sub_paths_dict = fu.get_sub_paths_dict(biobb_name=self.package_name)
        for module_name in sub_paths_dict:
            module_path = Path(self.imported_package.__path__[0]).parent / sub_paths_dict.get(module_name) / f"{module_name}.py"
            link_path = Path(self.output_dir).joinpath(module_name)
            print(f"Creating softlink: {link_path} -> {module_path}")
            try:
                link_path.unlink()
            except FileNotFoundError:
                pass
            link_path.symlink_to(module_path)


def main():
    parser = argparse.ArgumentParser(description="Creates pycompss adapters.",
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999),
                                     epilog='''Examples: \ncreate_bin_softlinks.py -p biobb_package  -o path/to/env/bin''')
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--package_name', '-p', required=True, help='BioBB package name from where the json schemas will be taken.')
    required_args.add_argument('--output_bin_dir', '-o', required=True, help='Output path to the environment bin path.')
    args = parser.parse_args()

    package_list = [args.package_name]
    if args.package_name.lower() == 'all':
        package_list = ["biobb_analysis", "biobb_chemistry", "biobb_cmip", "biobb_io", "biobb_gromacs", "biobb_model", "biobb_pmx", "biobb_structure_utils", "biobb_vs", "biobb_ml", "biobb_amber", "biobb_dna"]

    for package in package_list:
        BinSoftlinkGenerator(package=package, output_dir=args.output_bin_dir).launch()


if __name__ == '__main__':
    main()
