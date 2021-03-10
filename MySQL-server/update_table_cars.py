#!/usr/bin/python
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


### Functions

def getCSV_rows():
    """
    Function to download the CSV file with the cars and read and return the 
    rows as a list.
    """
    ### Download the CSV file
    csv_file = requests.get(_env.DOWNLOAD_CARS_CSV)
    open(_env.PATH_CARS_CSV, 'wb').write(csv_file.content)
    
    
    ### Read the data from the file
    
    row_list = []
    
    # Read the CSV file
    with open(_env.PATH_CARS_CSV) as file:
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
        # If not enough values given in the list, append None
        if 15 - len(row) > 0:
            for i in range(15 - len(row)):
                row.append(None)
            
    
                
    return row_list


def getTable_names(cursor):
    """
    Function to get the names of the cars that are already in the table and 
    write them into a list. The list is returned.
    """
    
    print("Update starts")
    
    names_list = []
    
    ### Extract the cars that are already in the table

    # Get all cars name from the table
    cursor.execute("SELECT name FROM cars")
    for car in cursor:
        names_list.append(car[0])
        
    return names_list



def main():
    """
    Main part of the script. Gets the cars from the table and from the CSV file.
    Extarcts the cars that are not in the table yet and inserts them.
    """
    
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
    
    
    ### Extract the remaining cars
    new_cars_list = []
    
    row_list = getCSV_rows()
    print(row_list)
    
    # Output for validation: Rows from CSV file
    print("\nThe cars from the CSV file:")
    for row in row_list:
        print(row[4])
    
    names_list = getTable_names(cursor)
    
    # Output for validation: Rows from CSV file
    print("\nThe cars that are already in the table:")
    for name in names_list:
        print(name)
        
    for row in row_list:
        if row[4] not in names_list:
            new_cars_list.append(row)
    
    
    ### Insert the cars into the table
    for row in new_cars_list:
        # Execute the command
        cursor.execute("INSERT INTO cars (type, consumption, capacity, power, name, cw_value, proj_area, rolling_friction_factor, mass, mass_factor, area, lambda_transfer, alpha_inside, alpha_outside, thickness) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", row)
        db.commit()
    
    
    # Output for validation: Rows from CSV file
    names_list = getTable_names(cursor)
    print("\nThe cars that are now in the table:")
    for name in names_list:
        print(name)
    
    ### Close the connection
    cursor.close()
    db.close()
    
    print("\nUpdate finished")




### Calling main function

# If script gets executed: execute main function
if __name__ == "__main__":
    main()
