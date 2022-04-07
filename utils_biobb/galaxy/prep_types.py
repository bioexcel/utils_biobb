#!/usr/env python

import sys


TEMPLATE = '<datatype extension="{}" type="{}" subclass="true" display_in_upload="true" />'

PARENTS = {
    'binary': 'galaxy.datatypes.binary:Binary',
    'text': 'galaxy.datatypes.text:Text'
}

file = sys.argv[1]

with open(file) as types_file:
    for line in types_file:
        data = line.rstrip().split(',')
        if data[3]:
            continue
        print(TEMPLATE.format(data[0],PARENTS[data[2]]))