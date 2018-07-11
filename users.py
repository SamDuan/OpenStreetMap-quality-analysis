#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re

unique_id = set()
a = set()

def get_user(element):
    return element.get('user')

def process_map(filename):
    for _, element in ET.iterparse(filename):
        if element.attrib.get('uid'):
            unique_id.add(element.attrib['uid'])
    return unique_id

def test():
    users = process_map('raleigh_north-carolina.osm')
    pprint.pprint(users)
    print(len(users))
    return users

if __name__ == "__main__":
    a=test()