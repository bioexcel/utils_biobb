#!/usr/bin/env python3

from pathlib import Path
from typing import Dict
import importlib
import argparse
import utils_biobb.common.file_utils as fu
from pprint import pprint


class BinSoftlinkGenerator:

    def __init__(self, package, output_dir, debug, dry):
        self.dry = dry
        self.debug = debug
        self.package_name = package
        self.output_dir = output_dir
        try:
            self.imported_package = importlib.import_module(package)
        except ImportError:
            raise ImportError(f'{package} and biobb_adapters must be available in your environment')

    def launch(self):
        sub_paths_dict: Dict[str, str] = fu.get_sub_paths_dict(biobb_name=self.package_name)
        for module_name in sub_paths_dict:
            module_path = Path(self.imported_package.__path__[0]).parent / sub_paths_dict.get(module_name, '') / f"{module_name}.py"
            link_path = Path(self.output_dir).joinpath(module_name)
            print(f"Creating softlink: {link_path} -> {module_path}")
            if not module_path.exists():
                raise FileNotFoundError(f"Module {module_path} does not exist")
            if self.debug:
                pprint(f"{module_path} -- {module_path.stat()}")
            if not Path(self.output_dir).exists():
                raise FileNotFoundError(f"Output directory {self.output_dir} does not exist")
            if self.debug:
                pprint(f"{Path(self.output_dir)} -- {Path(self.output_dir).stat()}")
            if self.dry:
                continue
            try:
                link_path.unlink()
            except FileNotFoundError:
                pass
            link_path.symlink_to(module_path)


def main():
    parser = argparse.ArgumentParser(description="Creates softlinks in your anaconda environment.",
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999),
                                     epilog='''Examples: \ncreate_bin_softlinks.py -p biobb_package  -o path/to/env/bin''')
    parser.add_argument('--debug', '-d', action='store_true', required=False, help='Debug printing file')
    parser.add_argument('--dry', action='store_true', required=False, help='Dry run printing file')
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--package_name', '-p', required=True, help='BioBB package name from where the json schemas will be taken.')
    required_args.add_argument('--output_bin_dir', '-o', required=True, help='Output path to the environment bin path.')
    args = parser.parse_args()

    package_list = [args.package_name]
    if args.package_name.lower() == 'all':
        # biobb_common
        # biobb_template
        # biobb_structure_checking
        # biobb_ml
        # utils_biobb
        package_list = ["biobb_amber", "biobb_analysis", "biobb_chemistry", "biobb_cmip", "biobb_cp2k", "biobb_dna", "biobb_flexdyn", "biobb_flexserv", "biobb_godmd", "biobb_gromacs", "biobb_haddock", "biobb_io", "biobb_model", "biobb_pdb_tools", "biobb_pmx", "biobb_pytorch", "biobb_structure_utils", "biobb_vs"]

    for package in package_list:
        BinSoftlinkGenerator(package=package, output_dir=args.output_bin_dir, debug=args.debug, dry=args.dry).launch()


if __name__ == '__main__':
    main()
