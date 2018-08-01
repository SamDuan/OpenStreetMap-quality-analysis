# -*- coding: utf-8 -*-
"""
Created on Wed Aug 01 09:37:06 2018

@author: Samuel
"""

import sqlite3
import pandas as pd

sqlite_file = 'mydb.db' # name of the sqlite database file
conn = sqlite3.connect(sqlite_file) # Connect to the database
cur = conn.cursor() # Get a cursor object
 

# Check that the data imported correctly
cur.execute('SELECT * FROM nodes limit 10')
all_rows = cur.fetchall()


# Retrieving the data which the amenity is bicycle_parking
query = ("SELECT id \
         FROM nodes_tags \
         WHERE value='bicycle_parking' \
         limit 10")
cur.execute(query)
bike_id=cur.fetchall()

# Retrieving the coord with the the amenity is bicycle_parking
query = ("CREATE TABLE result2 AS \
         SELECT nodes.id, \
         nodes.lat, \
         nodes.lon, \
         nodes_tags.value \
          FROM nodes INNER JOIN nodes_tags \
                  ON nodes.id = nodes_tags.id")
cur.execute(query)
cur.fetchall()

# Check if the tables are created successfully
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cur.fetchall())

query = ("SELECT * FROM result2 \
         WHERE value = 'bicycle_parking'")
cur.execute(query)
bike=pd.DataFrame(cur.fetchall())

# Retrieving the coord with the amenity is college
query = ("SELECT * FROM result2 \
         WHERE value = 'college'")
cur.execute(query)
college=pd.DataFrame(cur.fetchall())

# Close the connection
conn.close()