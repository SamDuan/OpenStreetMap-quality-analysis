# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 12:26:50 2017

@author: Samuel
"""

import sqlite3
import csv
from pprint import pprint

sqlite_file = 'mydb.db'    # name of the sqlite database file
conn = sqlite3.connect(sqlite_file) # Connect to the database
cur = conn.cursor() # Get a cursor object
 
cur.execute('DROP TABLE IF EXISTS nodes')
cur.execute('DROP TABLE IF EXISTS nodes_tags')
cur.execute('DROP TABLE IF EXISTS ways')
cur.execute('DROP TABLE IF EXISTS ways_tags')
cur.execute('DROP TABLE IF EXISTS ways_nodes')
conn.commit()

# Create the table, specifying the column names and data types:
cur.execute('''CREATE TABLE nodes(id INTEGER PRIMARY KEY NOT NULL, lat REAL, lon REAL, user TEXT, uid INTEGER, version INTEGER, changeset INTEGER, timestamp TEXT)''')
cur.execute('''CREATE TABLE nodes_tags(id INTEGER, key TEXT, value TEXT,type TEXT)''')
cur.execute('''CREATE TABLE ways (id INTEGER PRIMARY KEY NOT NULL, user TEXT, uid INTEGER, version TEXT, changeset INTEGER, timestamp TEXT)''')
cur.execute('''CREATE TABLE ways_tags(id INTEGER NOT NULL, key TEXT NOT NULL, value TEXT NOT NULL, type TEXT)''')
cur.execute('''CREATE TABLE ways_nodes(id INTEGER NOT NULL, node_id INTEGER NOT NULL, position INTEGER NOT NULL)''')

# commit the changes
conn.commit()

# format in csv files --- shall match the column order in the sql table schema
#NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
#NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
#WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
#WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
#WAY_NODES_FIELDS = ['id', 'node_id', 'position']

# Read in the csv file as a dictionary, format the data as a list of tuples:
with open('nodes.csv','rb') as fin:
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['id'], i['lat'], i['lon'], i['user'].decode("utf-8"), i['uid'], i['version'], i['changeset'], i['timestamp'].decode("utf-8")) for i in dr]
# insert the formatted data
cur.executemany("INSERT INTO nodes(id, lat, lon ,user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", to_db)

with open('nodes_tags.csv','rb') as fin:
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['id'], i['key'].decode("utf-8"), i['value'].decode("utf-8"), i['type'].decode("utf-8")) for i in dr]
cur.executemany("INSERT INTO nodes_tags (id, key, value ,type) VALUES (?, ?, ?, ?);", to_db)

with open('ways.csv','rb') as fin:
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['id'], i['user'].decode("utf-8"), i['uid'], i['version'].decode("utf-8"), i['changeset'], i['timestamp'].decode("utf-8")) for i in dr]
cur.executemany("INSERT INTO ways(id, user, uid ,version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?);", to_db)

with open('ways_tags.csv','rb') as fin:
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['id'], i['key'].decode("utf-8"), i['value'].decode("utf-8"), i['type'].decode("utf-8")) for i in dr]
cur.executemany("INSERT INTO ways_tags(id, key, value ,type) VALUES (?, ?, ?, ?);", to_db)

with open('ways_nodes.csv','rb') as fin:
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['id'], i['node_id'], i['position']) for i in dr]
cur.executemany("INSERT INTO ways_nodes(id, node_id ,position) VALUES (?, ?, ?);", to_db)

# commit the changes
conn.commit()

# Check that the data imported correctly
cur.execute('SELECT * FROM nodes')
all_rows = cur.fetchall()
print('1):')
pprint(all_rows)

# Read in the csv file as a dictionary, format the data as a list of tuples:
with open('nodes_tags.csv','rb') as fin:
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['id'], i['key'],i['value'].decode("utf-8"), i['type']) for i in dr]

# insert the formatted data
cur.executemany("INSERT INTO nodes_tags(id, key, value,type) VALUES (?, ?, ?, ?);", to_db)
# commit the changes
conn.commit()

# Check that the data imported correctly
cur.execute('SELECT * FROM nodes_tags')
all_rows = cur.fetchall()
print('1):')
pprint(all_rows)
    
# Close the connection
conn.close()