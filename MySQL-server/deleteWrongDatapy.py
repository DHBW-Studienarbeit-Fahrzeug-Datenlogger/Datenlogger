"""
Created by: Tim Hager
Date: 07.03.2021
Version: 1.0
    
Description:
    Deletes wrong data from the tables.
"""


### Imports
"""Necessary because of the intern structure of the mysql module (connector is 
also a module and has to be imported explicetly)"""
import mysql.connector as mysql_connector
import _env
import csv
import requests

# The data to be deleted: ["table", "identifier", "value"]
const = [[]]


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
    
    for data in const:
        command = "DELETE FROM "+data[0]+" WHERE "+data[1]+" = %s"
        print(command)
        cursor.execute(command, (data[2],))
        db.commit()

    
    ### Close the connection
    cursor.close()
    db.close()
    
    print("\nDelete finished")




### Calling main function

# If script gets executed: execute main function
if __name__ == "__main__":
    main()