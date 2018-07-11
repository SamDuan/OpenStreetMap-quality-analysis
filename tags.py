#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def key_type(element, keys):
    if element.tag == "tag":
        if lower.search(element.attrib['k']):
            keys["lower"] += 1 
        elif lower_colon.search(element.attrib['k']):
            keys["lower_colon"] += 1
        elif problemchars.search(element.attrib['k']):
            keys["problemchars"] += 1
            print(element.attrib['k'])
        else:
            keys["other"] += 1
            print(element.attrib['k'])
    return keys

def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        # references:
        # https://discussions.udacity.com/t/what-does-the-parameter-events-start-mean/171946
        keys = key_type(element, keys)

    return keys



def test():
    keys = process_map('raleigh_north-carolina.osm')
    pprint.pprint(keys)

if __name__ == "__main__":
    test()