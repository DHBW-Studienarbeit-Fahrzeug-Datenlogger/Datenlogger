# -*- coding: utf-8 -*-
"""
Date: 01.12.2020

Created by: Tim Hager

Description:
    Creates the additional data with the height_profile script for the already 
    existing data files and appends the file name to the database.
"""

### Imports 
import mysql.connector as mysql_connector
import _env
import glob
import os
import height_profile as hp


### Constants
DIRECTORY = r"/home/pi/datafiles"


### Create connection with database
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
    

# Create execution object
cursor = db.cursor()


### Rename the csvx files to csv
for file in glob.glob(DIRECTORY + "/*.csvx"):
    new_name = file[:-1]
    os.rename(file, new_name)


### For every JSON-file in the directory
for file in glob.glob(DIRECTORY + "/*.csv"):
    print(file)
    
    # Create height profile
    hp.build_height_profile(file, 0)
    
    # File name for additional data
    add_file = file[:-4] + "_height_profile.json"
    # File name for data that is already in the database
    filename = file[:-4] + ".json"
    
    # Execute the command to add the file name for the additional data to the database
    cursor.execute("UPDATE data SET additional_file = %s WHERE filename = %s", (add_file, file))
    db.commit()


### Close the connection
cursor.close()
db.close()