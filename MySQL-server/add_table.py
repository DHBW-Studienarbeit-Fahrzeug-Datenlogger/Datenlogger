#!/usr/bin/python
"""
Created by: Tim Hager
Date: 07.03.2021
Version: 1.0
    
Description:
    Adds a table for the virtually created drive cycles.
"""


### Imports
"""Necessary because of the intern structure of the mysql module (connector is 
also a module and has to be imported explicetly)"""
import mysql.connector as mysql_connector
import _env
import csv
import requests


### Functions



### Main
def main():
    """
    Main part of the script.
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
    command = "CREATE TABLE simulation (id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, filename VARCHAR(180) NULL DEFAULT NULL, date VARCHAR(45) NULL DEFAULT NULL, starttime VARCHAR(45) NULL DEFAULT NULL, totalKM FLOAT NULL DEFAULT NULL, endtime VARCHAR(45) NULL DEFAULT NULL, VIN VARCHAR(20) NULL DEFAULT NULL, fuelConsumption FLOAT NULL DEFAULT NULL, energyConsumption FLOAT NULL DEFAULT NULL, endLat FLOAT NULL DEFAULT NULL, endLong FLOAT NULL DEFAULT NULL, endDate VARCHAR(45) NULL DEFAULT NULL, additional_file VARCHAR(180) NULL DEFAULT NULL, id_car INT(11) NULL DEFAULT NULL, id_route INT(11) NULL DEFAULT NULL, filename_energy VARCHAR(180) NULL DEFAULT NULL, UNIQUE INDEX unique_id (id), UNIQUE INDEX filename_energy_unique (filename_energy))"
    cursor.execute(command)
    db.commit()

    
    ### Close the connection
    cursor.close()
    db.close()
    
    print("\nUpdate finished")




### Calling main function

# If script gets executed: execute main function
if __name__ == "__main__":
    main()
