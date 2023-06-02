import argparse
import json
import yaml
import shutil
from pathlib import Path, PurePath

###
# python3 cwl_wf_generator.py -y ../../../biobb_workflows/biobb_wf_flexdyn/python/workflow.yml -p ../../../biobb_workflows/biobb_wf_flexdyn/python/workflow.py -a ../../../biobb_adapters/biobb_adapters/cwl -o ../../../biobb_workflows/biobb_wf_flexdyn/cwl_test
###

INPUT_DESCRIPTIONS = 'workflow_input_descriptions.yml'
WORKFLOW = 'workflow.cwl'


class CWLWFGenerator():

    def __init__(self, yml_input_path, python_input_path, adapters_path, output_path, **kwargs):

        # check if yml_input_path exists
        if not Path(yml_input_path).exists():
            raise SystemExit('Unexisting YAML input path')

        self.yml_input_path = yml_input_path

        # check if python_input_path exists
        if not Path(python_input_path).exists():
            raise SystemExit('Unexisting Python input path')

        self.python_input_path = python_input_path

        # check if adapters_path exists
        if not Path(adapters_path).exists():
            raise SystemExit('Unexisting adapters path')
        self.adapters_path = adapters_path

        # check if output_path exists
        if not Path(output_path).exists():
            raise SystemExit('Unexisting output path')

        self.output_path = output_path

    def parseYAML(self):
        with open(self.yml_input_path, "r") as stream:
            try:
                wf_dict = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        wf_dict.pop("working_dir_path")
        wf_dict.pop("can_write_console_log")

        return wf_dict

    def parsePython(self):
        adapters_dict = []
        for line in open(self.python_input_path, 'r').readlines():
            ln = line.strip()
            if (ln.startswith('from biobb_') and not ln.startswith('from biobb_common')):
                parts = ln.strip().split()
                adapters_dict.append({'tool': parts[3], 'package': parts[1].split(sep='.')[0]})
        return adapters_dict

    def generateInputDescriptions(self, wf_dict):
        print(f'\n## Generating {INPUT_DESCRIPTIONS}')
        input_desc_dict = {}
        for k1 in wf_dict:
            paths = wf_dict[k1]['paths']
            for k2 in paths:
                if (k2.startswith('input_') and paths[k2].startswith('/path/to/inputs')):
                    input_desc_dict[f"{k1}_{k2}"] = {'class': 'File', 'path': Path(paths[k2]).name, 'format': 'EDAM FORMAT FOR THIS INPUT'}
                elif (not k2.startswith('input_')):
                    input_desc_dict[f"{k1}_{k2}"] = Path(paths[k2]).name
            if ('properties' in wf_dict[k1]):
                input_desc_dict[f"{k1}_config"] = json.dumps(wf_dict[k1]['properties'])

        # save object to cwl file
        input_desc_path = PurePath(self.output_path).joinpath(INPUT_DESCRIPTIONS)
        with open(input_desc_path, 'w+') as yml_file:
            yaml.dump(input_desc_dict, yml_file, sort_keys=False, width=1000)

        print(f"{input_desc_path} has been properly generated")

    def generateWorkflow(self, wf_dict):
        print(f'\n## Generating {WORKFLOW}')
        out_dict = {
            'cwlVersion': 'v1.0',
            'class': 'Workflow',
            'label': 'WORKFLOW TITLE',
            'doc': 'WORKFLOW DESCRIPTION',
            'inputs': {},
            'outputs': {},
            'steps': {}
        }
        
        # inputs
        inputs_dict = {}
        for k1 in wf_dict:
            paths = wf_dict[k1]['paths']
            for k2 in paths:
                if (k2.startswith('input_') and paths[k2].startswith('/path/to/inputs')):
                    inputs_dict[f"{k1}_{k2}"] = 'File'
                elif (not k2.startswith('input_')):
                    inputs_dict[f"{k1}_{k2}"] = 'string'
            if ('properties' in wf_dict[k1]):
                inputs_dict[f"{k1}_config"] = 'string'

        out_dict['inputs'] = inputs_dict

        # outputs
        outputs_dict = {}
        for k1 in wf_dict:
            paths = wf_dict[k1]['paths']
            c = 1
            for k2 in paths:
                if (k2.startswith('output_')):
                    outputs_dict[f"{k1}_out{c}"] = {
                        'label': k2,
                        'doc': 'Path to the output file',
                        'type': 'File',
                        'outputSource': f"{k1}/{k2}"
                    }
                    c = c + 1

        out_dict['outputs'] = outputs_dict

        # steps
        steps_dict = {}
        for k1 in wf_dict:
            inouts = {}
            if 'properties' in wf_dict[k1]:
                inouts['config'] = f"{k1}_config"

            outs = []
            paths = wf_dict[k1]['paths']
            for k2 in paths:
                if k2.startswith('input_'):
                    if paths[k2].startswith('/path/to/inputs'):
                        inouts[k2] = f"{k1}_{k2}"
                    else:
                        inouts[k2] = f"{paths[k2].replace('dependency/', '')}"
                else:
                    inouts[k2] = f"{k1}_{k2}"
                    outs.append(k2)

            steps_dict[k1] = {
                'label': wf_dict[k1]['tool'],
                'doc': f"Description for {wf_dict[k1]['tool']}",
                'run': f"biobb_adapters/{wf_dict[k1]['tool']}.cwl",
                'in': inouts,
                'out': outs
            }

        out_dict['steps'] = steps_dict

        # print(out_dict['steps'])

        wf_path = PurePath(self.output_path).joinpath(WORKFLOW)
        with open(wf_path, 'w+') as yml_file:
            yml_file.write('#!/usr/bin/env cwl-runner\n')
            yaml.dump(out_dict, yml_file, sort_keys=False, width=1000)

        print(f"{wf_path} has been properly generated")

    def copyBioBBAdapters(self, adapters_dict):
        print('\n## Copying BioBB adapters')
        new_adapters_path = f"{self.output_path}/biobb_adapters"
        # create biobb_adapters folder
        Path(new_adapters_path).mkdir(exist_ok=True)
        # copy adapters into it
        for index in range(len(adapters_dict)):
            src = f"{self.adapters_path}/{adapters_dict[index]['package']}/{adapters_dict[index]['tool']}.cwl"
            shutil.copy2(src, new_adapters_path)
            print(f"{new_adapters_path}/{adapters_dict[index]['tool']}.cwl has been properly copied")

    def launch(self):
        """ launch function for CWLWFGenerator """

        # parse YAML WF file
        wf_dict = self.parseYAML()
        # parse Python WF file
        adapters_dict = self.parsePython()

        # generate workflow_input_descriptions.yml file
        self.generateInputDescriptions(wf_dict)

        # generate workflow.cwl file
        self.generateWorkflow(wf_dict)

        # copy biobb_adapters
        self.copyBioBBAdapters(adapters_dict)

        print('\n## Remember to check all the custom paths and to fill the "label" and "doc" fields of the workflow')


def main():
    parser = argparse.ArgumentParser(description="Translates to CWL a given YAML workflow.",
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999),
                                     epilog='''Examples: \ncwl_wf_generator.py -y path/to/yaml/workflow -p path/to/python/workflow -a path/to/biobb_adapters -o path/to/cwl/workflow\ncwl_wf_generator.py --yml_in path/to/yaml/workflow --python_in path/to/python/workflow --adapters path/to/biobb_adapters --output path/to/cwl/workflow''')
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--yml_in', '-y', required=True, help='Path to the the original YAML file.')
    required_args.add_argument('--python_in', '-p', required=True, help='Path to the the original Python file.')
    required_args.add_argument('--adapters', '-a', required=True, help='Path to the folder from where the biobb_adapters needed for this workflow will be taken.')
    required_args.add_argument('--output', '-o', required=True, help='Output path to the CWL workflow folder.')

    args = parser.parse_args()

    CWLWFGenerator(yml_input_path=args.yml_in, python_input_path=args.python_in, adapters_path=args.adapters, output_path=args.output).launch()


if __name__ == '__main__':
    main()
