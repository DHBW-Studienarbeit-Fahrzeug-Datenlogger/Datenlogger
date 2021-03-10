# -*- coding: utf-8 -*-
"""
Date: 27.11.2020

Created by: Tim Hager

Description:
    Appends a new column to the table data for the json file with the 
    additional calculated signals.
"""

### Imports 
import mysql.connector as mysql_connector
import _env


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

### Append column additional_file to table data
try:
    cursor.execute("ALTER TABLE data ADD additional_file VARCHAR(180) NULL DEFAULT NULL")
except Exception as e:
    print("Column in data probably already existing:\n")
    print(e)
    
### Append columns to table cars
try:
    cursor.execute("ALTER TABLE cars ADD (cw_value FLOAT NULL DEFAULT NULL, proj_area FLOAT NULL DEFAULT NULL, rolling_friction_factor FLOAT NULL DEFAULT NULL, mass FLOAT NULL DEFAULT NULL, mass_factor FLOAT NULL DEFAULT NULL, area FLOAT NULL DEFAULT NULL, lambda_transfer FLOAT NULL DEFAULT NULL, alpha_inside FLOAT NULL DEFAULT NULL, alpha_outside FLOAT NULL DEFAULT NULL, thickness FLOAT NULL DEFAULT NULL)")
except Exception as e:
    print("Columns in cars probably already existing:\n")
    print(e)


### Close the connection
cursor.close()
db.close()