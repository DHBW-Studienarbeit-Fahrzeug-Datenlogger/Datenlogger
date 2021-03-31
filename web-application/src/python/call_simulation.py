# -*- coding: utf-8 -*-
"""
Date: 13.03.2021

Created by: Tim Hager

Description:
    Python script to execute the simulation script. Afterwards, the newest
    (greatest) ID from the table simulation is extracted and printed.
"""

### Imports
import sys
import mysql.connector as mysql_connector
import _env

# Import simulation script (path from the executing directory: webapplication)
sys.path.append('../MySQL-server')
import driving_simulation


### Get arguments
car_id = sys.argv[1]
route_id = sys.argv[2]


### Call virtual_drive() from simulation script
driving_simulation.virtual_drive(car_id, int(route_id))


### Extract newest ID from table simulation

# Create connection with database
try:
    db = mysql_connector.connect(
            user=_env.DB_USER,
            password=_env.DB_PASSWORD,
            host=_env.DB_HOST,
            database=_env.DB_NAME,
            # Necessary for mysql 8.0 to avoid an error because of encoding
            auth_plugin='mysql_native_password'
        )
except:
    db = mysql_connector.connect(
            user=_env.DB_USER,
            password=_env.DB_PASSWORD,
            host="127.0.0.1",
            database=_env.DB_NAME,
            # Necessary for mysql 8.0 to avoid an error because of encoding
            auth_plugin='mysql_native_password'
        )
    

# Create execution object and execute command
cursor = db.cursor()
cursor.execute("SELECT id FROM simulation")

ID = 0
for id_count in cursor:
    if id_count[0] > ID:
        ID = id_count[0]

# Close the connection
cursor.close()
db.close()


### Print ID
if ID == 0:
    print("No ID found")
else:
    print(ID)
