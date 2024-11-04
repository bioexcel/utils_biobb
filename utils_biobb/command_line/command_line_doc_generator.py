#!/usr/bin/env python3

import argparse
from typing import Optional
import json
from pathlib import Path
import re
import subprocess


def rstlink2mdlink(rst_string):
    pattern = re.compile(r"(?P<text_before>.*)`(?P<text_link>.+)<(?P<text_url>.+)>`_(?P<text_after>.*)")
    match = pattern.match(rst_string)
    if match:
        link = match.groupdict()
        return f"{link['text_before']+'['+link['text_link'].strip()+']('+link['text_url']+')'+link['text_after']}"
    else:
        return rst_string


def get_enum_extensions(enum_list):
    pattern = re.compile(r".*\.(?P<extension>\w+).*")
    return ", ".join(match.groupdict()['extension'].upper() for enum_string in enum_list if (match := pattern.match(enum_string)))


def get_file_content(file_path):
    return Path(file_path).read_text()


def main():
    parser = argparse.ArgumentParser(description="Creates command line documentation file.",
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999),
                                     epilog="Examples: \ncommand_line_doc_generator.py -j path/to/json_schemas_folder -c path/to/config_folder -b biobb_name -o path/to/docs/source/command_line.md")

    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--json_schemas_folder', '-j', required=True,
                               help='json_schemas folder in biobb_example/biobb_example')
    required_args.add_argument('--config_folder', '-c', required=True,
                               help='config folder in biobb_example/biobb_example')
    required_args.add_argument('--biobb_name', '-b', required=True,
                               help='biobb_name')
    required_args.add_argument('--output', '-o', required=True, help='Output md file')

    args = parser.parse_args()

    biobb_name = args.biobb_name
    biobb_title = f"BioBB {biobb_name.split('_')[1].upper()}"
    config_url = f"https://github.com/bioexcel/{biobb_name}/blob/master/{biobb_name}/test/data/config/"
    config_path = args.config_folder

    with open(args.output, 'w') as out:
        # Write document title
        out.write(f"# {biobb_title} Command Line Help\n")
        out.write("Generic usage:\n")
        out.write("```python\n")
        out.write("biobb_command [-h] --config CONFIG --input_file(s) <input_file(s)> --output_file <output_file>\n")
        out.write("```\n")
        out.write("-----------------\n")
        out.write("\n")

        for json_file_path in Path(args.json_schemas_folder).glob('*.json'):
            block_name = json_file_path.stem
            if block_name == biobb_name:
                continue
            with open(json_file_path) as json_file:
                json_dict = json.load(json_file)
            block_description = rstlink2mdlink(json_dict['title'])
            block_help = "    " + "\n    ".join(subprocess.getoutput(f'{block_name} -h').split('\n'))

            out.write("\n")
            out.write(f"## {block_name.capitalize()}\n")
            out.write(f"{block_description}\n")
            out.write("### Get help\n")
            out.write("Command:\n")
            out.write("```python\n")
            out.write(f"{block_name} -h\n")
            out.write("```\n")
            out.write(f"{block_help}\n")

            out.write("### I / O Arguments\n")
            out.write("Syntax: input_argument (datatype) : Definition\n")
            out.write("\n")
            out.write("Config input / output arguments for this building block:\n")
            command_line_list = []
            for argument, argument_dict in json_dict['properties'].items():
                if argument != 'properties':
                    out.write(f"* **{argument}** (*{argument_dict['type']}*): {argument_dict['description']}. File type: {argument_dict['filetype']}. [Sample file]({argument_dict['sample']}). Accepted formats: {get_enum_extensions(argument_dict['enum'])}\n")
                    if argument_dict['sample']:
                        sample_file = argument_dict['sample'].split('/')[-1]
                    else:
                        sample_file = f"{argument_dict['filetype']}.{get_enum_extensions(argument_dict['enum']).split(',')[0].lower()}"
                    command_line_list.append(f"--{argument} {sample_file}")
            out.write("### Config\n")
            out.write("Syntax: input_parameter (datatype) - (default_value) Definition\n")
            out.write("\n")
            out.write("Config parameters for this building block:\n")
            for argument, argument_dict in json_dict['properties']['properties']['properties'].items():
                out.write(f"* **{argument}** (*{argument_dict['type']}*): ({argument_dict['default']}) {rstlink2mdlink(argument_dict['description'])}.\n")

            for extension in ['yml', 'json']:
                if extension == 'yml':
                    out.write("### YAML\n")
                else:
                    out.write(f"### {extension.upper()}\n")
                config_file_name = 'config_'+block_name+'.'+extension
                if not Path(config_path).joinpath(config_file_name).exists():
                    continue
                # if not Path(config_path).joinpath(config_file_name).exists() and block_name=='cmip':
                #    config_file_name = 'config_' + block_name + '_mip.' + extension

                command_line_str = " ".join(['--config', config_file_name] + command_line_list)
                out.write(f"#### [Common config file]({config_url+config_file_name})\n")
                out.write("```python\n")
                out.write(f"{get_file_content(str(Path(config_path).joinpath(config_file_name)))}\n")
                out.write("```\n")
                docker_file_name = 'config_'+block_name+'_docker.'+extension
                if Path(config_path).joinpath(docker_file_name).exists():
                    out.write(f"#### [Docker config file]({config_url+docker_file_name})\n")
                    out.write("```python\n")
                    out.write(f"{get_file_content(str(Path(config_path).joinpath(docker_file_name)))}\n")
                    out.write("```\n")
                singularity_file_name = 'config_' + block_name + '_singularity.'+extension
                if Path(config_path).joinpath(singularity_file_name).exists():
                    out.write(f"#### [Singularity config file]({config_url+singularity_file_name})\n")
                    out.write("```python\n")
                    out.write(f"{get_file_content(str(Path(config_path).joinpath(singularity_file_name)))}\n")
                    out.write("```\n")
                out.write("#### Command line\n")
                out.write("```python\n")
                out.write(f"{block_name} {command_line_str}\n")
                out.write("```\n")


if __name__ == '__main__':
    main()
