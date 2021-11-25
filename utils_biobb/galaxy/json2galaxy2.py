""" Utility to generate Galaxy automated tool definitions (XML) from biobb json_schemas """

import argparse
import json
import os
import re
import sys
from os.path import join as opj

from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2.exceptions import TemplateSyntaxError

TEMPL = "biobb_galaxy_template.xml"
XML_DIR = "./xml_files"

def tool_name(orig):
    data = re.split('_', orig)
    return ''.join([a.capitalize() for a in data])

def main():
    """ Usage: json2galaxy.py [-h] [--template TEMPLATE] [--xml_dir XML_DIR]
                      [--id ID] [--display_name DISPLAY_NAME] [--create_dir]
                      base_biobb_dir
        positional arguments:                                                                    
            * group_schema (**str**)      Path to Json schema from biobb group
        optional arguments:
            * --template (**str**)  Path to Template for XML galaxy adapter (xml) (default: biobb_galaxy_template.xml)
            * --xml_dir (**str**) Path to directory to place XML output files. 
            * --create_dir (**bool**)  Create biobb group adapter directory (default False)
    """
    parser = argparse.ArgumentParser(description='Build galaxy adapters.')
    parser.add_argument("--template", default=TEMPL, help="Template for XML galaxy adapter")
    parser.add_argument("--xml_dir", default=XML_DIR, help="Path to place output XML recipes")
    parser.add_argument("--create_dir", action="store_true", help="Create biobb directory")
    parser.add_argument(dest="base_biobb_dir", help="Json schema from building blocks group")

    args = parser.parse_args()
    
    # Extracting data directory 
    if args.template == TEMPL:
        template_dir = os.path.dirname(__file__)
    else:
        template_dir = os.ath.dirname(args.template)
    
    if not template_dir:
        template_dir='.'

    for group in os.listdir(args.base_biobb_dir):
        if not re.search('^biobb', group):
            continue
        print('Building group', group)
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
            print("  - Building {} XML definition".format(block['exec']))
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

            data['tool_id'] = data['biobb_group'] + "_" + data['name']
            
            if 'version' in schema_group_data:
                data['version'] = schema_group_data['version']
            else:
                data['version'] = '0.1.0'
                
            data['description'] = schema_data['title']
            
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
                    
                    tool_data['format'] = ','.join(tool_data['file_types'])
                    
                    if len(tool_data['file_types']) > 1:
                        tool_data['help_format'] = '[format]'
                        tool_data['multiple_format'] = "output_format"
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
                                v['multiple'] = True
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
                        data['props'][k] = v
                        #
                        
                        # Generating "galaxyfied" Json string for config parameter
                        if v['type'] in ('string', 'select'):
                            if 'multiple' in v and v['multiple']:
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
            env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=select_autoescape(['xml'])
            )
            templ = env.get_template(args.template)
            
            if args.create_dir:
                output_path_dir = opj(args.xml_dir, data['biobb_group'])
                if not os.path.isdir(output_path_dir):
                    os.mkdir(output_path_dir)
                output_path = opj(output_path_dir, "biobb_" + data['name'] + ".xml")
            with open(output_path, "w") as xml_file:
                xml_file.write(templ.render(data))
        
if __name__ == '__main__':
    main()
