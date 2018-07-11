import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "raleigh_north-carolina.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

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

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")
            
def audit_postcode(postcodes, postcode):
    postcodes[postcode].add(postcode)
    return postcodes            

def is_postcode(elem):
    return (elem.attrib['k'] == "addr:postcode")

def audit(osmfile):
    print("in audit()")
    street_types = defaultdict(set)
    postcodes = defaultdict(set)
    
    for event, elem in ET.iterparse(osmfile):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                
# This part below with comments is for street type auditing
#                if is_street_name(tag):
#                    audit_street_type(street_types, tag.attrib['v'])
#    return street_types                
                if is_postcode(tag):
                    audit_postcode(postcodes, tag.attrib['v'])
    return postcodes

def update_name(name, mapping):
    m = street_type_re.search(name)
    if m.group() in mapping:
        print("m.group")
        print(m.group())
        name = re.sub(m.group(), mapping[m.group()], name)
    return name

def update_postcode(postcode):
    # references:
    # https://discussions.udacity.com/t/cleaning-postcode/195512/6
    search = re.match(r'^\D*(\d{5}).*', postcode)
    clean_postcode = search.group(1)
    return clean_postcode

def test():
# This part below with comments is for street type auditing
#    st_types = audit(OSMFILE)
#    pprint.pprint(dict(st_types))
    
#    for st_type, ways in st_types.items():
#        for name in ways:
#            better_name = update_name(name, mapping)
#            print(name, "=>", better_name)
    
    p_codes = audit(OSMFILE)
    pprint.pprint(dict(p_codes))
    
    for code_type, ways in p_codes.items():
        for code in ways:
            better_code = update_postcode(code)
            print(code, "=>", better_code)

if __name__ == '__main__':
    test()
    