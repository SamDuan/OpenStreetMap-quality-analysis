# OpenStreetMap Data Case Study

### Map Area: Raleigh, NC, United States
This map is of a city that I used to live, so I’m quite interested to see what database querying reveals. Sources of data:
- [https://mapzen.com/data/metro-extracts/metro/raleigh_north-carolina/](https://mapzen.com/data/metro-extracts/metro/raleigh_north-carolina/)
- [https://www.openstreetmap.org/relation/179052](https://www.openstreetmap.org/relation/179052)



## Problems Encountered in the Map
The full size map was run against audit.py, data.py and db.py sequentially, and few problems with the data are found as shown below:

- Missing spaces upon entering *("LaurelcherryStreet")* 
- Extra information included the street names *("Westgate Park Dr #100", "Barrett Dr Suite 206", "Fayetteville St #1100")*
- Inconsistent postal codes *("277030", "27713-2229", "28616")*
- Typos in the city names *(Morrisville is mis-spelled as Morisville)*

### Inconsistent post codes
To standardize the postal codes, the following codes are inserted into data.py to convert all the postal codes into a basic 5-digit format.

Defining a function to update the postal codes:

``` python
def update_postcode(postcode):
    # ref. https://discussions.udacity.com/t/cleaning-postcode/195512/6
    search = re.match(r'^\D*(\d{5}).*', postcode)
    clean_postcode = search.group(1)
    return clean_postcode
``` 
Incorporating update_costcode() (as well as another function to update the street name, update_name()) into shape_element() function:

``` python
def shape_element():
    ...
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
    ...
``` 
    

# Data Overview and Exploration
This section contains basic statistics and exploration of the dataset, and sql queries used to gather them are listed as well.

### File sizes
```
raleigh_north-carolina.osm .... 482 MB
mydb.db ....................... 266 MB
nodes.csv ..................... 190 MB
nodes_tags.csv ................ 2.1 MB
ways.csv ...................... 13 MB
ways_nodes.cv ................. 63 MB
ways_tags.csv ................. 30 MB
```  

### Number of nodes
```sql
sqlite> SELECT COUNT(*) FROM nodes;
```
```sql
2374920
```

### Number of ways
```sql
sqlite> SELECT COUNT(*) FROM ways;
```
```sql
243842
```

### Number of unique users
```sql
sqlite> SELECT COUNT(DISTINCT(e.uid))          
FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) e;
```
```sql
1019
```

### Number of users appearing only once (having 1 post)
```sql
sqlite> SELECT COUNT(*)
FROM
    (SELECT e.user, COUNT(*) as num
     FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e
     GROUP BY e.user
     HAVING num=1)  u;
```

```sql
199
```

### Sort cities by count, descending
```sql
sqlite> SELECT tags.value, COUNT(*) as count
FROM (SELECT * FROM nodes_tags UNION ALL
      SELECT * FROM ways_tags) tags
WHERE tags.key == 'city'
GROUP BY tags.value
ORDER BY count DESC;
```
And the results are shown below:

```sql
Raleigh      6830
Cary         3119
Morrisville  1732
Durham       1674
Chapel Hill  625
Carrboro     503
Research Triangle Park 6
Hillsborough 5
RTP          4
raleigh      4
chapel Hill  3
Chapel Hill, NC 2
Wake Forest  2
cary         2
durham       2
 Raleigh     1
Apex         1
Morisville   1
Ralegh       1
Ralegih      1
chapel hill  1
```

Firstly, the major cities in the triangle are (Raleigh-Durham-Chapel Hills) are included in this data set. Thus, it contains not only the city of Raleigh but also the nearby cities. Secondly, it is visible that there are several variations of names of the same city (e.g. "Chapel Hill", "chapel Hill", Chapel Hill, NC", "chapel hill").

### Top 10 amenities

```sql
sqlite> SELECT value, COUNT(*) as num
FROM nodes_tags
WHERE key='amenity'
GROUP BY value
ORDER BY num DESC
LIMIT 10;
```

```sql
bicycle_parking  1146
restaurant       924
place_of_worship 742
fast_food        366
bench            264
waste_basket     250
cafe             194
atm              156
school           152
parking          144
```
It is surprising to find out that there are many bicycle parking lots in this area. It is possible these parkings are around the campuses for the students, who ride bikes in their campuses.

### Top 10 shops

```sql
sqlite> SELECT value, COUNT(*) as num
FROM nodes_tags
WHERE key='shop'
GROUP BY value
ORDER BY num DESC
LIMIT 10;
```

```sql
clothes     198
supermarket 186
hairdresser 118
vacant      88
beauty      74
car_repair  60
jewelry     58
department_store 54
gift        48
art         42
```

# Additional Ideas

## Contributor statistics
### Top 10 contributing users
```sql
sqlite> SELECT e.user, COUNT(*) as num
FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) e
GROUP BY e.user
ORDER BY num DESC
LIMIT 10;
```
```sql
jumbanho        1552751
JMDeMai         219489
bdiscoe         129500
woodpeck_fixbot 112193
bigal945        103601
yotann          66555
runbananas      41249
BjornRasmussen  37676
sandhill        33495
MikeInRaleigh   30578
```

Based on the result above, it is easy to note that,
- The top user "jumbanho" makes a significant contribution, which is larger than 65%. 
- The top 5 users corporately contribute to 80% of the data.
- The rest of the users, 99.5% of all users, only contribute to 20% of the data corporately.

It is understandable that certain users are more passionate about the OpenStreetMap project, and therefore contribute more to the data input. However, because data input is dominant by a particular group of people, it is possible the data entry could be skewed.
To alleviate this issue, the OpenStreetMap project could potentially set an upper limit for the contribution from each user. In addition, if the map data of an area is largely provided by an user, a reminder could be posted as a headline, indicating that this set of data may be biased potentially. This could be an incentive to other users to contribute more to normalize the users contribution, and a gereral warning to whoever considering to use the data. A potential drawback could be the delay of building complete data sets because of the limit for the contribution from each user.

# Conclusion
This review provides a general overlook of the geography information in Raleigh area, and certain entry errors have been be identified as well. In addition, the street names and the postal codes are standardized to improve the data quality. The data in this map is largely supplied by few users, which could possibly lead to bias information, and a possible solution is suggested.
