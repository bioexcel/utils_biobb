#import glob
import argparse
import re
import json
#import yaml
from importlib import import_module
from difflib import SequenceMatcher
#from ast import literal_eval
from pathlib import Path, PurePath
from os import walk

#regex_default = '\((\"*([a-zA-Z0-9_ \-\^\:\.\/\']*|\-*\d*\.*\d*)\"*)\)'
#regex_default_array = '\((\[.*?\])\)'
#regex_float = '\-*\d*\.\d*'
#regex_prop_name = '\*\*(.*?)\*\*'
#regex_type = '\(\*(.*?)\*\)'
regex_sphinx_link = '\`(.+)\<(.+)\>\`\_'
regex_parameters = '(\w*)\ *(?:\()(\w*)(?:\)):?\ *(\(\w*\):)?\ *(.*?)(?:\.)\ ?(?:File type:\ *)(\w+)\.\ *(\`(?:.+)\<(.*)\>\`\_\.)?\ *(?:Accepted formats:\ *)(.+)(?:\.)?'
#regex_param_value = '(\w*)\ (?:\()(.*)(?:\))'
regex_param_value = '(\w*)\ *(?:(?:\()(.*)(?:\)))?'
regex_property_values = '(?:\*\ *\*\*)(.*)(?:\*\*)\ *(?:\(\*)(\w*)(?:\*\))\ *\-\ ?(?:\()(.*?)(?:\))\ *(?:(?:\[)(\d+(?:\.\d+)?)\-(\d+(?:\.\d+)?)(?:\|)?(\d+(?:\.\d+)?)?(?:\]))?\ *(?:(?:\[)(.*)(?:\]))?\ *(.*)?(?:Values:\ *)(.+)(?:\.)?'
regex_property_non_values = '(?:\*\ *\*\*)(.*)(?:\*\*)\ *(?:\(\*)(\w*)(?:\*\))\ *\-\ ?(?:\()(.*?)(?:\))\ *(?:(?:\[)(\d+(?:\.\d+)?)\-(\d+(?:\.\d+)?)(?:\|)?(\d+(?:\.\d+)?)?(?:\]))?\ *(?:(?:\[)(.*)(?:\]))?\ *(.*)?'
regex_prop_value = '([a-zA-Z0-9_\-]+)\ *(?:(?:\()(.*)?(?:\)))?'
regex_info = '\*\ *(.*)'
regex_info_item = '(.*?)\:(?:\ *)(.*)'

class JSONSchemaGenerator():

    def __init__(self, input_package, output_path, **kwargs):
        self.input_package = input_package

        # check if output_path exists
        if not Path(output_path).exists():
            raise SystemExit('Unexisting output path')

        # check if output_path has correct structure
        if not input_package in output_path:
            raise SystemExit('Incorrect output path. The structure must be: path/biobb_package/biobb_package')

        self.output_path = PurePath(output_path).joinpath('json_schemas')
        #self.output_path_test = PurePath(output_path).joinpath('test')
        #self.output_path_config = PurePath(output_path).joinpath('test/data/config')

        if not Path(self.output_path).exists():
            raise SystemExit('Incorrect output path. The structure must be: path/biobb_package/biobb_package')
       

    def similar_string(self, a, b):
        """ check similarity between two strings """
        return SequenceMatcher(None, a, b).ratio()

    def getType(self, type):
        """ return JSON friendly type """
        if type == 'str': return 'string'
        if type == 'int': return 'number'
        if type == 'float': return 'float'
        if type == 'bool': return 'boolean'
        if type == 'dic': return 'object'

        return type 

    """def getDefault(self, default, i):
        # return defaults
        
        if(i == 0): return literal_eval(default)
        else: val = default[i]

        if val == 'True': return True
        if val == 'False': return False
        if val == 'None': return None
        if val.lstrip('-+').isdigit(): 
            return int(val)
        if re.match(regex_float, val) is not None:
            return float(val)

        if isinstance(val, str): return val.strip('\"')
        
        return val"""


    def replaceLink(self, matchobj):
        return matchobj.group(1)

    def getParamFormats(self, vals, description):

        list_vals = re.split(', |,',vals)

        formats = []
        file_formats = []
        for val in list_vals:
            f = re.findall(regex_param_value, val)[0]
            formats.append('.*\.{0}$'.format(f[0]))

            ff = {
                    "extension": '.*\.{0}$'.format(f[0]),
                    "description": description.strip('.')
                }

            if f[1]:
                ffs = re.split('\|',f[1])
               
                for item in ffs:
                    parts = re.split('\:',item)
                    ff[parts[0]] = parts[1]

            file_formats.append(ff)


        return formats, file_formats

    def getPropFormats(self, vals):

        formats = []
        prop_formats = []

        list_vals = re.split(', |,',vals)

        for val in list_vals:

            val = re.sub(regex_sphinx_link, self.replaceLink, val)

            f = re.findall(regex_prop_value, val)[0]
            formats.append(f[0])

            desc = f[1] if f[1] else None

            ff = {
                    "name": f[0],
                    "description": desc
                }

            prop_formats.append(ff)

        return formats, prop_formats

    def getParameters(self, row, required):
        # get list with all info in parameters:
        # * property id
        # * property type
        # * property description
        # * mandatory / optional
        # * file type
        # * sample file
        # * formats
        param = row.strip()

        param = re.findall(regex_parameters, param)[0]

        param_id = param[0]
        param_type = param[1]
        if not param[2]: required.append(param_id)
        description = param[3]
        filetype = param[4]
        sample = param[6] if param[6] else None
        formats, file_formats = self.getParamFormats(param[7], description)

        p = {
            "type": self.getType(param_type),
            "description": description,
            "filetype": filetype,
            "sample": sample,
            "enum": formats,
            "file_formats": file_formats
            }

        return param_id, p, required


    def getProperties(self, row):
        # get list with all info in properties:
        # * property id
        # * property type
        # * property default
        # * property min-max|step
        # * WF property
        # * property description
        # * property possible values
        prop = row.strip()

        regex = regex_property_values if 'Values:' in row else regex_property_non_values

        prop = re.findall(regex, prop)[0]

        prop_id = prop[0]
        prop_type = prop[1]
        default = prop[2]
        prop_min = prop[3] if prop[3] else None
        prop_max = prop[4] if prop[4] else None
        prop_step = prop[5] if prop[5] else None
        wf_prop = True if prop[6] else False
        description = prop[7]
        if len(prop) == 9: formats, property_formats = self.getPropFormats(prop[8])

        p = {
            "type": self.getType(prop_type),
            "default": default,
            "wf_prop": wf_prop,
            "description": description
            }

        if prop_min: p["min"] = prop_min
        if prop_max: p["max"] = prop_max
        if prop_step: p["step"] = prop_step

        if len(prop) == 9:
            p["enum"] = formats
            p["property_formats"] = property_formats

        return prop_id, p

    def getInfoProp(self, info_prop):
        info_prop = re.findall(regex_info_item, info_prop)[0]
        return info_prop[0], info_prop[1]

    def getGenericInfo(self, row):
        output = row.strip()
        if output.startswith('|'):
            output = output.replace('|', '')
            output = output.strip()
            output = re.sub(regex_sphinx_link, self.replaceLink, output)
        else:
            output = None
        return output

    def parseDocs(self, doclines, module):
        """ parse python docs to object / JSON format """

        # clean empty spaces from doclines
        doclines = list(filter(lambda name: name.strip(), doclines))

        # get name, title and description
        name = self.getGenericInfo(doclines[0])
        title = self.getGenericInfo(doclines[1])
        description = self.getGenericInfo(doclines[2])        

        # parse documentation
        args = False
        info = False
        required = []
        obj_info = {}
        object_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$id": "http://bioexcel.eu/" + self.input_package + "/json_schemas/1.0/" + module,
            "name": name,
            "title": title,
            "description": description,
            "type": "object",
            "info": [],
            "required": [],
            "properties": {}
        }
        properties = {}
        
        for row in doclines:
            leading = len(row) - len(row.lstrip())

            # check if arguments
            if 'Args:' in row:
                args = True
                info = False

            if args:
                # first level: I/O & parameters dictionary
                if leading == 8: 

                    if 'properties' not in row:

                        param_id, p, required = self.getParameters(row, required)

                        properties[param_id] = p
                
                # second level: properties
                if leading == 12 and not row.isspace():

                    if not "properties" in properties: 
                        properties["properties"] = { "type": "object", "properties": {} }

                    prop_level1, p = self.getProperties(row)

                    properties["properties"]["properties"][prop_level1] = p

                # third level: parameters
                if(leading == 16):

                    if not "parameters" in properties["properties"]["properties"][prop_level1]: 
                        properties["properties"]["properties"][prop_level1]["type"] = "object"
                        properties["properties"]["properties"][prop_level1]["parameters"] = {}

                    prop_level2, p = self.getProperties(row)

                    properties["properties"]["properties"][prop_level1]["parameters"][prop_level2] = p

            # check if info
            if 'Info:' in row:
                info = True
                args = False

            if info:
                if leading == 8: 
                    info_id = row.strip()
                    info_id = re.findall(regex_info, info_id)[0].strip(':')
                    obj_info[info_id] = {}
                if leading == 12: 
                    info_prop = row.strip()
                    info_prop = re.findall(regex_info, info_prop)[0].strip(':')
                    k, v = self.getInfoProp(info_prop)
                    obj_info[info_id][k] = v
                object_schema["info"] = obj_info

        object_schema["required"] = required
        object_schema["properties"] = properties

        object_schema["additionalProperties"] = False

        return object_schema

    def cleanOutputPath(self):
        """ removes all JSON files from the output path (except the biobb_package.json file) and all the config files """

        # get all files in json_schemas folder
        files = []
        for (dirpath, dirnames, filenames) in walk(self.output_path):
            files.extend(filenames)
            break

        # remove biobb_package.json file from array of files
        if(self.input_package + '.json' in files): files.remove(self.input_package + '.json')

        # remove files from array of files
        for f in files:
            path = PurePath(self.output_path).joinpath(f)
            Path(path).unlink()

        # get all files in config folder
        #files = []
        #for (dirpath, dirnames, filenames) in walk(self.output_path_config):
        #    files.extend(filenames)
        #    break

        # remove files from array of files
        #for f in files:
        #    path = PurePath(self.output_path_config).joinpath(f)
        #    Path(path).unlink()

    def saveJSONFile(self, module, object_schema):
        """ save JSON file for each module """

        path = PurePath(self.output_path).joinpath(module + '.json')

        with open(path, 'w') as file:
            json.dump(object_schema, file, indent=4)

        print(str(path) + " file saved")

    """def saveConfigJSONFile(self, properties, module, ):
        # save config JSON file for each module 

        # pmx hardcoding
        if module.endswith('_docker'):
            module = module.replace('_docker', '')

        conf_json = {
            'properties': properties
        }
        path = PurePath(self.output_path_config).joinpath('config_'+ module + '.json')
        with open(path, 'w') as file:
            json.dump(conf_json, file, indent=4)

        print(str(path) + " file saved")"""

    def launch(self):
        """ launch function for JSONSchemaGenerator """

        # import package
        packages = import_module(self.input_package)

        # remove old JSON files
        self.cleanOutputPath()

        # get config properties
        """with open(PurePath(self.output_path_test).joinpath('conf.yml')) as f:
            try:
                conf = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                print(exc)"""

        # get documentation of python files
        for package in packages.__all__:
            # for every package import all modules
            modules = import_module(self.input_package + '.' + package)
            for module in modules.__all__:

                # config files
                # biobb_analysis hardcoding for bfactor, rms and rmsf
                #mdl = module
                #if(self.input_package == 'biobb_analysis' and not module in conf):
                #    mdl = module + '_first'

                # biobb_analysis hardcoding forcing to take docker cofiguration
                ##########################################
                ## TO FIX WHEN NEW BIOBB_PMX IS DONE
                ##########################################
                #if(self.input_package == 'biobb_pmx'):
                #    mdl = module + '_docker'

                #if('properties' in conf[mdl] and conf[mdl]['properties'] is not None): 
                #    self.saveConfigJSONFile(conf[mdl]['properties'], mdl)

                # json schemas
                # import single module
                mod = import_module(self.input_package + '.' + package + '.' + module)

                # get class name through similarity with module name
                sel_class = ''
                similarity = 0;
                for item in dir(mod):
                    if ( item[0].isupper() and 
                    not item.startswith('Path') and 
                    not item.startswith('Pure') and
                    not item.startswith('check_') ):
                        s = self.similar_string(item, module)
                        if s > similarity:
                            sel_class = item
                            similarity = s

                # exceptions:
                if sel_class == "KMeans" and module == "k_means": 
                    sel_class = "KMeansClustering"
                if sel_class == "KMeans" and module == "dbscan": 
                    sel_class = "DBSCANClustering"
                if sel_class == "AgglomerativeClustering": 
                    sel_class = "AgglClustering"
                if sel_class == "SpectralClustering": 
                    sel_class = "SpecClustering"

                # get class documentation
                klass = getattr(mod, sel_class)
                doclines = klass.__doc__.splitlines()

                object_schema = self.parseDocs(doclines, module)

                self.saveJSONFile(module, object_schema)


def main():
    parser = argparse.ArgumentParser(description="Creates json_schemas for given BioBB package.", 
                                     formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999),
                                     epilog='''Examples: \njson_generator.py -p biobb_package -o path/to/biobb_package/biobb_package\njson_generator.py --package biobb_package --output path/to/biobb_package/biobb_package''')
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--package', '-p', required=True, help='BioBB package to be parsed.')
    required_args.add_argument('--output', '-o', required=True, help='Output path to the biobb_package/biobb_package folder.')

    args = parser.parse_args()

    JSONSchemaGenerator(input_package=args.package, output_path=args.output).launch()


if __name__ == '__main__':
    main()
