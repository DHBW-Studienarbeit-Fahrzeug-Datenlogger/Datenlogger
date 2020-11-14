# -*- coding: utf-8 -*-
"""
Created by: Tim Hager

Date: 13.11.2020

Version: 1.0
    
Description:
    Updates the table of electric cars in the database. Downloads an CSV file
    with the data from GitHub, parses it and inserts the cars that are not
    already in the table.

"""


### Imports
"""Necessary because of the intern structure of the mysql module (connector is 
also a module and has to be imported explicetly)"""
import mysql.connector as mysql_connector
import _env
import csv
import requests


### Important variables
row_list = []
names_list = []


### Download the CSV file
csv_file = requests.get(_env.DOWNLOAD_CARS_CSV)

open(_env.PATH_CARS_CSV, 'wb').write(csv_file.content)


### Read the data from the file
# Read the CSV file
with open(_env.PATH_CARS_CSV, newline='') as file:
    reader = csv.reader(file, delimiter=';', quotechar='|')
    for row in reader:
        row_list.append(row)

# Change the float values to float type
for row in row_list:
    for i, element in enumerate(row):
        element = element.replace(",", ".")
        try:
            row[i] = float(element)
        except:
            pass

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


### Extract the cars that are not in the table

# Get all cars name from the table
cursor.execute("SELECT name FROM cars")
for car in cursor:
    names_list.append(car[0])



### Extract the remaining cars
for row in row_list:
    if row[4] in names_list:
        row_list.remove(row)


### Insert the cars into the table
for row in row_list:
    # Execute the command
    cursor.execute("INSERT INTO cars (type, consumption, capacity, power, name) VALUES (%s, %s, %s, %s, %s)", row)
    db.commit()



### Close the connection
cursor.close()
db.close()

