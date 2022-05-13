""" Utility to generate Galaxy automated tool definitions (XML) from biobb json_schemas """

import argparse
from itertools import count
import json
import os
import re
import sys
from os.path import join as opj
from tkinter import W

from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.exceptions import TemplateSyntaxError

TEMPL = "biobb_galaxy_tool_template.xml"
XML_DIR = "./xml_files"
SERVER_BASE_DIR = "dev_biobb"
SECTIONS = {
    'biobb_io': 'Get Data',
    'biobb_structure_utils': 'Structure Utils',
    'biobb_model': 'Modelling',
    'biobb_cmip' : 'CMIP',
    'biobb_md': 'Setup and Simulation (GROMACS)',
    'biobb_amber': 'Setup and Simulation (AMBER)',
    'biobb_analysis': 'Trajectory analysis',
    'biobb_dna': 'Nucleic Acids Trajectory analysis',
    'biobb_chemistry': 'Small molecules',
    'biobb_pmx': 'PMX Free Energy calculation',
    'biobb_vs': 'Virtual Screening / Docking',
    'biobb_ml': 'Machile Learning'
}

def tool_name(orig):
    data = re.split('_', orig)
    return ''.join([a.capitalize() for a in data])

def main():
    """ Usage: json2galaxy.py [-h] [--template TEMPLATE] [--xml_dir XML_DIR]
                      [--id ID] [--display_name DISPLAY_NAME] [--create_dir]
                      base_biobb_dir
        positional arguments:                                                                    
            * base_biobb_dir (**str**)      Path to biobb's folder
        optional arguments:
            * --template (**str**)  Path to Template for XML galaxy adapter (xml) (default: biobb_galaxy_template.xml)
            * --xml_dir (**str**) Path to directory to place XML output files. 
            * --create_dir (**bool**)  Create biobb group adapter directory (default False)
            * --file_types (**bool**)  Add discovered file types to logs
            * --tools_xml (**str**) Generate tools panel XML
    """
    parser = argparse.ArgumentParser(description='Build galaxy adapters.')
    parser.add_argument("--template", default=TEMPL, help="Template for XML galaxy adapter")
    parser.add_argument("--xml_dir", default=XML_DIR, help="Path to place output XML recipes")
    parser.add_argument("--create_dir", action="store_true", help="Create biobb package directory if not exists")
    parser.add_argument(dest="base_biobb_dir", help="Json schema from building blocks group")
    parser.add_argument("--file_types", action="store_true", help="List required File Types on log")
    parser.add_argument("--tools_xml", action="store", help="Generate tools panel XML")
        
    args = parser.parse_args()
    
    # Extracting data directory 
    if args.template == TEMPL:
        template_dir = os.path.dirname(__file__)
    else:
        template_dir = os.path.dirname(args.template)
    
    if not template_dir:
        template_dir='.'
    
    if args.tools_xml:
        try:
            tools_xml = open(args.tools_xml, "w")
        except IOError as e:
            print(e)
            print("Skipping tools_conf file")
            args.tools_xml = None
             
    for group in os.listdir(args.base_biobb_dir):
        write_conf = args.tools_xml and group in SECTIONS
        if not re.search('^biobb', group):
            continue
        print('Building group', group)
        
        if write_conf:
            tools_xml.write(f"<section id=\"{group}\" name=\"{SECTIONS[group]}\" >\n")
        
        # Parsing json schemas
        group_schema = opj(args.base_biobb_dir, group, group, 'json_schemas', group + '.json')
        try:
            with open(group_schema, "r") as schema_file:
                schema_group_data = json.load(schema_file)
        except IOError as err:
            print(err)
            continue
        base_path = os.path.dirname(group_schema)

        group_data = {
            'id' : schema_group_data['_id'],
            'conda': schema_group_data['conda'],
            'docker': schema_group_data['docker'],
            'version': schema_group_data['version'],
            'blocks': schema_group_data['tools']
        }
        
        for block in group_data['blocks']:
            if 'exec' not in block:
                print(" ERROR: Block name (exec) not found in", block)
                continue
            print(f"  - Building {block['exec']} XML definition")
            schema_file = opj(base_path, block['exec'] + '.json')    
            try:
                with open(schema_file, 'r') as schema_json:
                    schema_data = json.load(schema_json)        
            except IOError as err:
                print(err, file=sys.stderr)
                continue
        
            #Getting data components from schema
            
            data = {'files':{'input':{}, 'output':{}}, 'props':{}}
            
            # Extracting tool name and group from schema $id to generate defaults
            data['name'] = block['exec']
            data['display_name'] = tool_name(data['name'])

            data['biobb_group'] = group_data['id']
            data['version'] = group_data['version']

            data['tool_id'] = f"{data['biobb_group']}_{data['name']}"
            
            data['description'] = schema_data['title']
            
            multiple_formats_required = []
    
            if args.file_types:
                file_types = {'input':set(), 'output': set()}
                
            for f in schema_data['properties']:
                if f != 'properties':
                    # Parsing input and output files
                    tool_data = {
                        'name': f, 
                        'file_types':[],
                        'description': schema_data['properties'][f]['description'],
                        'optional': f not in schema_data['required']
                        }
                    
                    if 'enum' in schema_data['properties'][f]:
                        for v in schema_data['properties'][f]['enum']:
                            m = re.search(r"\w+", v)
                            tool_data['file_types'].append(m.group(0))
                    if args.file_types: 
                        for ty in tool_data['file_types']:
                            file_types[schema_data['properties'][f]['filetype']].add(ty)
                     
                    tool_data['format'] = ','.join(tool_data['file_types'])
                    
                    if len(tool_data['file_types']) > 1:
                        tool_data['help_format'] = '[format]'
                        tool_data['multiple_format'] = "output_format"
                        if schema_data['properties'][f]['filetype'] == 'output':
                            multiple_formats_required.append(tool_data)  
                    else:
                        tool_data['help_format'] = tool_data['format']
                    
                    tool_data['label'] = schema_data['properties'][f]['filetype'] + ' ' +  tool_data['format'].upper()
                    
                    data['files'][schema_data['properties'][f]['filetype']][f] = tool_data
                
                else:
                    # Parsing properties
                    # TODO include more structured information in json schema to avoid re

                    props_str=[]
                    for k,v in schema_data['properties'][f]['properties'].items():
                        if re.match('container', k) or\
                            ('description' in v and re.search('WF property', v['description'])) or\
                            ('wf_prop' in v and v['wf_prop']):
                            continue
                        if 'enum' in v:
                            v['values'] = v['enum']
                            if v['type'] == 'array':
                                v['multiple'] = "true"
                            v['type'] = 'select'
                        elif 'description' in v:
                            m = re.search('(.*) Valid values: (.*)', v['description'])
                            if m:
                                v['values'] = re.split(', *', m.group(2).replace('.',''))
                                v['type'] = 'select'
                                v['description'] = m.group(1)                
                        if 'default' in v and isinstance(v['default'], str):
                            v['default'] = v['default'].replace('"','')
                            if v['default'] == 'None':
                                v['default'] = ''
                                v['optional'] = "true"
                        #Hack to avoid Galaxy compilation error
                        if not v['default']:
                            v['optional'] = "true"
                        if 'optional' not in v:
                            v['optional'] = "false"
                        if v['type'] == 'number':
                            v['type'] = 'float'
                        if 'property_formats' in v:
                            dum = {}
                            for fmt in v['property_formats']:
                                dum[fmt['name']] = fmt['description']
                            v['property_formats'] = dum
                        else:
                            v['property_formats'] = []
                        if 'multiple' not in v or not v['multiple']:
                            v['multiple'] = 'false'
                        data['props'][k] = v
                        #
                        # Generating "galaxyfied" Json string for config parameter
                        if v['type'] in ('string', 'select'):
                            if 'multiple' in v and v['multiple'] != 'false':
                                # ["${'","'.join($properties.k)}"]
                                txt = "__ob____dq__${'__dq__,__dq__'.join($properties." + k + ")}__dq____cb__" 
                            else:
                                # "${k}"
                                txt = "__dq__${properties." + k + "}__dq__"
                            props_str.append("__dq__" +  k + "__dq__:" + txt)
                            
                        else:
                            props_str.append("__dq__" +  k + "__dq__:${properties." + k + "}")
                    
                    data['config_str'] = "__oc__" + ",".join(props_str) + "__cc__"
                    #print(data)
                    # Adding output_format when multiple output formats
                    n_formats_required = len(multiple_formats_required);
                    if multiple_formats_required:
                        for tool in multiple_formats_required:
                            param_name = 'output_format'
                            if n_formats_required > 1 :
                                param_name = tool['name'] + '_format'
                            if param_name not in data['props']:
                                data['props'][param_name] = {
                                    'type': 'select',
                                    'default': None,
                                    'wf_prop': False,
                                    'description': 'Format of the output file',
                                    'enum': tool['file_types'],
                                    'property_formats': {},
                                    'values': tool['file_types'],
                                    'optional': 'true',
                                    'multiple': 'false'
                                }
                                data['files']['output'][tool['name']]['multiple_format'] = param_name
                                print(f"WARNING: added {param_name} property due to {tool['name']}")
            env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=select_autoescape(['xml'])
            )
            templ = env.get_template(args.template)
            
            if args.create_dir:
                output_path_dir = opj(args.xml_dir, data['biobb_group'])
                if not os.path.isdir(output_path_dir):
                    os.mkdir(output_path_dir)
                output_path = opj(output_path_dir, f"biobb_{data['name']}.xml")
            with open(output_path, "w") as xml_file:
                xml_file.write(templ.render(data))
            if write_conf:
                tools_xml.write(f"  <tool file=\"{SERVER_BASE_DIR}/{group}/biobb_{data['name']}.xml\" />\n")
            if args.file_types:
                for io in file_types:
                    for ty in file_types[io]:
                        print(f"#TYP {ty}\t{io}\t{data['tool_id']}")

        if write_conf:
            tools_xml.write("</section>\n")    
    
    if args.tools_xml:
        tools_xml.close()
            
if __name__ == '__main__':
    main()
