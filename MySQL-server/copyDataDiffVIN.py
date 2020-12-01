# -*- coding: utf-8 -*-
"""
Date: 01.12.2020

Created by: Tim Hager

Description:
    Appends the data from the database again but with a different (fictive) VIN.
    With that, the already recorded data can be used to verify the application.
"""

### Imports 
import mysql.connector as mysql_connector
import _env
import bcrypt


### Constants
VIN = "12345"


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


### Hash the VIN
hashed = bcrypt.hashpw(VIN.encode(), bcrypt.gensalt(10))
VIN_hashed = hashed.decode("utf-8")


### Get data

# Get the drive cycles in the database and append the data elements to a 
# 2-dimensional list
cursor.execute("SELECT * FROM data")
data_list = []
for data in cursor:
    temp_list = []
    for i, element in enumerate(data):
        if i == 6:
            temp_list.append(VIN_hashed)
        elif i == 0:
            pass
        else:
            temp_list.append(element)
    data_list.append(temp_list)
    
print("Data:")
for data in data_list:
    print(data)
    

### Delete datasets in the table (necessary because filenames must be unique)
cursor.execute("DELETE FROM data")

    
### Append the "new" dataset to the database
for data in data_list:
    # Execute the command
    cursor.execute("INSERT INTO data (filename, date, starttime, totalKM, endtime, VIN, fuelConsumption, energyConsumption, endLat, endLong, endDate, additional_file) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", data)
    db.commit()


### Close the connection
cursor.close()
db.close()