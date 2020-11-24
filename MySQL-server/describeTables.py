# -*- coding: utf-8 -*-
"""
Date: 24.11.2020

Created by: Tim Hager

Description:
    Prints the name of the tables as well as their description in the terminal.
    Used to get the information about the established database.
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
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()


### Get all tables and print the name of the tables as well as their description
for (table, ) in tables:
    print(table + ":\n")
    cursor.execute("DESCRIBE " + table)
    for column in cursor:
        print(column)
    print("\n\n")
    


### Close the connection
cursor.close()
db.close()