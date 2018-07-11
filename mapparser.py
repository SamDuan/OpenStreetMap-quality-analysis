import xml.etree.cElementTree as ET
import pprint

def count_tags(filename):
    tags={}
    
    for _, elem in ET.iterparse(filename):
    # references:
    # https://discussions.udacity.com/t/iterative-parsing-assertion/179776/4
    # https://discussions.udacity.com/t/preparing-for-database-help-getting-started/202844/2
    # https://discussions.udacity.com/t/p3-openstreetmap-overview/172045/2
    # https://discussions.udacity.com/t/what-does-the-parameter-events-start-mean/171946
     
        if elem.tag in tags.keys():
            # The keys() returns a list of all the keys in the dictionary "tags"
            tags[elem.tag] += 1
        else:
            tags[elem.tag] = 1
        print(tags)
    return tags
    
def test():

    tags = count_tags('raleigh_north-carolina.osm')
    pprint.pprint(tags)
    if False:
        assert tags == {'bounds': 1,
                        'member': 3,
                        'nd': 4,
                        'node': 20,
                        'osm': 1,
                        'relation': 1,
                        'tag': 7,
                        'way': 1}

if __name__ == "__main__":
    test()