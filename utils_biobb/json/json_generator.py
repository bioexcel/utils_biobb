import argparse
import re
import json
from importlib import import_module
from difflib import SequenceMatcher
from pathlib import Path, PurePath
from os import walk

# regex_sphinx_link = '\`(.+)\<(.+)\>\`\_'
regex_sphinx_link = r'\`([^\`]+)\ (\<[^\`]+\>\`\_)'
regex_parameters = r'(\w*)\ *(?:\()(\w*)(?:\)):?\ *(\(\w*\):)?\ *(.*?)(?:\.)\ *(?:File type:\ *)(\w+)\.\ *(\`(?:.+)\<(.*)\>\`\_\.)?\ *(?:Accepted formats:\ *)(.+)(?:\.)?'
regex_param_value = r'(\w*)\ *(?:(?:\()(.*)(?:\)))?'
# regex_property_values = '(?:\*\ *\*\*)(.*)(?:\*\*)\ *(?:\(\*)(\w*)(?:\*\))\ *\-\ *(?:\()(.*?)(?:\))\ *(?:(?:\[)(\d+(?:\.\d+)?)\-(\d+(?:\.\d+)?)(?:\|)?(\d+(?:\.\d+)?)?(?:\]))?\ *(?:(?:\[)(.*)(?:\]))?\ *(.*)?(?:Values:\ *)(.+)(?:\.)?'
regex_property_values = r'(?:\*\ *\*\*)(.*)(?:\*\*)\ *(?:\(\*)(\w*)(?:\*\))\ *\-\ ?(?:\()(.*)(?:\))\ *(?:(?:\[)([\-]?\d+(?:\.\d+)?)\~([\-]?\d+(?:\.\d+)?)(?:\|)?(\d+(?:\.\d+)?)?(?:\]))?\ *(?:(?:\[)(.*)(?:\]))?\ *(.*)\ ?(?:Values:\ *)(.+)(?:\.)?'
regex_property_non_values = r'(?:\*\ *\*\*)(.*)(?:\*\*)\ *(?:\(\*)(\w*)(?:\*\))\ *\-\ *(?:\()(.*?)(?:\))\ *(?:(?:\[)([\-]?\d+(?:\.\d+)?)\~([\-]?\d+(?:\.\d+)?)(?:\|)?(\d+(?:\.\d+)?)?(?:\]))?\ *(?:(?:\[)(.*)(?:\]))?\ *(.*)?'
#################
# regex_property_values = '(?:\*\s*\*\*)(.*)(?:\*\*)\s*(?:\(\*)(\w*)(?:\*\))\s*\-\s*(?:\()(.*)(?:\))\s*(?:(?:\[)(\w*)\-(\w*)(?:\|)?(\w*)?(?:\]))?\s*(?:(?:\[)(.*)(?:\]))?\s([a-zA-Z0-9_\- ().&?,!;]+)(?:\s|\.)+(?:(?:Values:)(.+))?'
###################
regex_prop_value = r'([a-zA-Z0-9_\-\+:\/\/\.\ \,\*\#]+)\ *(?:(?:\()(.*)?(?:\)))?'
regex_info = r'\*\ *(.*)'
regex_info_item = r'(.*?)\:(?:\ *)(.*)'


class JSONSchemaGenerator():

    def __init__(self, input_package, output_path, **kwargs):
        self.input_package = input_package

        # check if output_path exists
        if not Path(output_path).exists():
            raise SystemExit('Unexisting output path')

        # check if output_path has correct structure
        if not (input_package in output_path):
            raise SystemExit('Incorrect output path. The structure must be: path/biobb_package/biobb_package')

        self.output_path = PurePath(output_path).joinpath('json_schemas')

        if not Path(self.output_path).exists():
            raise SystemExit('Incorrect output path. The structure must be: path/biobb_package/biobb_package')

    def similar_string(self, a, b):
        """ check similarity between two strings """
        return SequenceMatcher(None, a.replace("_", "").lower(), b.replace("_", "").lower()).ratio()

    def getType(self, type):
        """ return JSON friendly type """
        if type == 'str':
            return 'string'
        if type == 'int':
            return 'integer'
        if type == 'float':
            return 'number'
        if type == 'bool':
            return 'boolean'
        if type == 'dict':
            return 'object'
        if type == 'list':
            return 'array'

        return type

    def getDefaultProperty(self, type, default):
        """ return default according to type """
        if default == 'None' and type != 'dict':
            return None
        elif default == 'None' and type == 'dict':
            default = {}
        elif type != 'dict':
            default = re.sub('\"|\'', '', default)
        elif type == 'dict':
            default = json.loads(default)

        if type == 'str' or type == 'string':
            return default
        if type == 'int':
            return int(default)
        if type == 'float':
            return float(default)
        if type == 'bool':
            return default.lower() in ("yes", "true", "t", "1")
        if type == 'dict':
            return default

        return default

    def getMinMaxStep(self, prop_type, prop_min):
        if prop_type == "float":
            return float(prop_min)
        elif prop_type == "int":
            return int(prop_min)

    def replaceLink(self, matchobj):
        return matchobj.group(1).strip()

    def getParamFormats(self, vals, description):

        list_vals = re.split(', |,', vals)

        formats = []
        file_formats = []
        for val in list_vals:
            f = re.findall(regex_param_value, val)[0]
            formats.append(r'.*\.{0}$'.format(f[0]))

            ff = {
                "extension": r'.*\.{0}$'.format(f[0]),
                "description": description.strip('.')
            }

            if f[1]:
                ffs = re.split(r'\|', f[1])

                for item in ffs:
                    parts = re.split(r'\:', item)
                    ff[parts[0]] = parts[1]

            file_formats.append(ff)

        return formats, file_formats

    def getPropFormats(self, vals, type_):

        if not vals:
            return None, None

        formats = []
        prop_formats = []

        list_vals = re.split(', |,', vals)

        for val in list_vals:

            # trick for cases when there are parenthesis in the format name
            val = re.sub(r'\\\(', '****', val)
            val = re.sub(r'\\\)', '++++', val)

            val = re.sub(regex_sphinx_link, self.replaceLink, val)

            f = re.findall(regex_prop_value, val)[0]

            frmt = f[0].strip(' ')
            if type_ == 'integer':
                frmt = int(f[0])
            if type_ == 'float':
                frmt = float(f[0])

            desc = f[1] if f[1] else None

            # trick for cases when there are parenthesis in the format name
            if type_ != 'integer' and type_ != 'float':
                if '****' in frmt:
                    frmt = re.sub(r'\*\*\*\*', '(', frmt)
                    frmt = re.sub(r'\+\+\+\+', ')', frmt)

            formats.append(frmt)

            ff = {
                "name": frmt,
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
        if not param[2]:
            required.append(param_id)
        description = re.sub(regex_sphinx_link, self.replaceLink, param[3])
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
        # regex = regex_property_values

        prop = re.findall(regex, prop)[0]

        prop_id = prop[0]
        prop_type = prop[1]
        default = prop[2]
        prop_min = prop[3] if prop[3] else None
        prop_max = prop[4] if prop[4] else None
        prop_step = prop[5] if prop[5] else None
        wf_prop = True if prop[6] else False
        description = re.sub(regex_sphinx_link, self.replaceLink, prop[7])
        if len(prop) == 9:
            formats, property_formats = self.getPropFormats(prop[8].rstrip(r'\.'), self.getType(prop_type))
        # formats, property_formats = self.getPropFormats(prop[8])

        p = {
            "type": self.getType(prop_type),
            "default": self.getDefaultProperty(prop_type, default),
            "wf_prop": wf_prop,
            "description": description
        }

        if prop_min:
            p["min"] = self.getMinMaxStep(prop_type, prop_min)
        if prop_max:
            p["max"] = self.getMinMaxStep(prop_type, prop_max)
        if prop_step:
            p["step"] = self.getMinMaxStep(prop_type, prop_step)

        if len(prop) == 9:
            p["enum"] = formats
            p["property_formats"] = property_formats
        # if formats and property_formats:
        #    p["enum"] = formats
        #    p["property_formats"] = property_formats

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

                    if not ("properties" in properties):
                        properties["properties"] = {"type": "object", "properties": {}}

                    prop_level1, p = self.getProperties(row)

                    properties["properties"]["properties"][prop_level1] = p

                # third level: parameters
                if (leading == 16):

                    if not ("parameters" in properties["properties"]["properties"][prop_level1]):
                        properties["properties"]["properties"][prop_level1]["type"] = "object"
                        properties["properties"]["properties"][prop_level1]["parameters"] = {}

                    prop_level2, p = self.getProperties(row)

                    properties["properties"]["properties"][prop_level1]["parameters"][prop_level2] = p

            # check if examples
            r = row.strip()
            if r.startswith('Examples'):
                info = False
                args = False

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
        if (self.input_package + '.json' in files):
            files.remove(self.input_package + '.json')

        # remove files from array of files
        for f in files:
            path = PurePath(self.output_path).joinpath(f)
            Path(path).unlink()

    def saveJSONFile(self, module, object_schema):
        """ save JSON file for each module """

        path = PurePath(self.output_path).joinpath(module + '.json')

        with open(path, 'w') as file:
            json.dump(object_schema, file, indent=4)

        print(str(path) + " file saved")

    def launch(self):
        """ launch function for JSONSchemaGenerator """

        # import package
        packages = import_module(self.input_package)

        # remove old JSON files
        self.cleanOutputPath()

        # get documentation of python files
        for package in packages.__all__:
            # for every package import all modules
            modules = import_module(self.input_package + '.' + package)
            for module in modules.__all__:

                print("Parsing " + str(PurePath(self.output_path).joinpath(module + '.json')))

                # json schemas
                # import single module
                mod = import_module(self.input_package + '.' + package + '.' + module)

                # get class name through similarity with module name
                sel_class = ''
                similarity = 0
                for item in dir(mod):
                    if (item[0].isupper() and
                        not item.startswith('Path') and
                        not item.startswith('Pure') and
                            not item.startswith('check_')):
                        s = self.similar_string(item, module)
                        # print(f"Similarity between {item} and {module}: {s}")
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
