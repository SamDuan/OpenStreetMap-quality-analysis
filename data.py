import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus

import schema

OSM_PATH = "raleigh_north-carolina.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

mapping = { "St": "Street",
            "ST": "Street",
            "St.": "Street",
            "Rd": "Road",
            "Rd.": "Road",
            "Ave": "Avenue",
            "Ln": "Lane", # newly added for Raleigh map
            "Ct": "Court", # newly added for Raleigh map
            "Cir": "Circle",
            "PI": "Place",
            "Blvd.": "Boulevard",
            "Blvd": "Boulevard",
            "Dr": "Drive", # newly added for Raleigh map
            "Pky": "Parkway",
            "Pkwy": "Parkway", # newly added for Raleigh map
            "Ext": "Exit"
            }

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    if element.tag == 'node':
        # note_attribs
        for item in NODE_FIELDS:
            node_attribs[item] = element.get(item)
        # tags
        for child in element:
            colon = child.get('k').find(':')
            if (child.tag == 'tag'):
                tag_dict ={}
                tag_dict['id'] = element.get('id')
                
                # start cleaning:
                # Street name
                if child.attrib["k"] == 'addr:street':
                    tag_dict["value"] = update_name(child.attrib["v"], mapping)
                # Postcodes
                elif child.attrib["k"] == 'addr:postcode':
                    tag_dict["value"] = update_postcode(child.attrib["v"])
                else:
                    tag_dict["value"] = child.attrib["v"]
                # end cleaning
                
                if (colon != -1): # colon is found
                    type_value = child.get('k')[:colon]
                    key_value = child.get('k')[colon+1:]                  
                    tag_dict['type'] = type_value
                    tag_dict['key'] = key_value
                else: # colon is not found
                    tag_dict['key'] = child.get('k')
                    tag_dict['type'] = 'regular'
                tags.append(tag_dict)
        return {'node': node_attribs, 'node_tags': tags}

    elif element.tag == 'way':
        # way_attribs
        for item in WAY_FIELDS:
            way_attribs[item] = element.get(item)
        # way_nodes & tags
        n = 0
        for child in element:  
            if child.tag == 'nd':
                nd_dict ={}
                nd_dict['id'] = element.get('id')
                nd_dict['node_id'] = child.get('ref')
                nd_dict['position'] = n
                n += 1
                print(n)
                print(nd_dict)
                way_nodes.append(nd_dict)
            if (child.tag == 'tag'):
                colon = child.get('k').find(':')
                tag_dict ={}
                tag_dict['id'] = element.get('id')
                
                # start cleaning:
                # Street name
                if child.attrib["k"] == 'addr:street':
                    tag_dict["value"] = update_name(child.attrib["v"], mapping)
                # Postcodes
                elif child.attrib["k"] == 'addr:postcode':
                    tag_dict["value"] = update_postcode(child.attrib["v"])
                else:
                    tag_dict["value"] = child.attrib["v"]
                # end cleaning
                
                if (colon != -1): # colon is found
                    type_value = child.get('k')[:colon]
                    key_value = child.get('k')[colon+1:]
                    tag_dict['type'] = type_value
                    tag_dict['key'] = key_value
                else: # colon is not found
                    tag_dict['key'] = child.get('k')
                    tag_dict['type'] = 'regular'
                tags.append(tag_dict)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
    
def update_name(name, mapping):
    m = street_type_re.search(name)
    if m.group() in mapping:
        print("m.group")
        print(m.group())
        name = re.sub(m.group(), mapping[m.group()], name)
    return name

def update_postcode(postcode):
    # https://discussions.udacity.com/t/cleaning-postcode/195512/6
    search = re.match(r'^\D*(\d{5}).*', postcode)
    clean_postcode = search.group(1)
    return clean_postcode

# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    # for python 2
    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        #https://discussions.udacity.com/t/problem-with-column-names-and-values-in-the-generated-csv-files/316584/2
        # For Python 2
        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)
    
        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)
                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])

if __name__ == '__main__':
    process_map(OSM_PATH, validate=False)
    
