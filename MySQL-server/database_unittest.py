# -*- coding: utf-8 -*-
"""
Created by: Tim Hager
Date: 14.11.2020
Version: 1.0
    
Description:
    Tests the script update_table_cars.
    Before first execution with the interpreter, comment out the execution of 
    the main function in the script update_table_cars.
"""
import _env
import mysql.connector as mysql_connector
import unittest
import update_table_cars as toTest


class DatabaseTest(unittest.TestCase):
    """
    Class for the database test. Includes the unit test methods.
    """

    def test1(self):
        """
        This test checks whether the table cars of the database contains
        all cars from the csv file and the cars that existed already in the 
        table after the automatic table update was executed.
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
        
        # Get the relevant data
        csv_rows = toTest.getCSV_rows()
        table_rows = []
        cursor.execute("SELECT * FROM cars")
        for car in cursor:
            table_rows.append(car)
            
            
        ### Create the list with the expected table elements
        specification_list = []
        for row in table_rows:
            specification_list.append(list(row[1:]))
        for row in csv_rows:
            existing = False
            for table_row in specification_list:
                if row[4] == table_row[4]:
                    existing = True
            
            if not existing:
                specification_list.append(row)
            
        
        
        ### Close the connection
        cursor.close()
        db.close()
        
        
        ### Execute the function that is to be tested
        toTest.main()
        
        
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
        
        ### Create the list with the actual table elements
        actual_list = []
        cursor.execute("SELECT * FROM cars")
        for row in cursor:
            actual_list.append(list(row[1:]))
            
            
        ### Close the connection
        cursor.close()
        db.close()
            
        # Get the result
        self.assertCountEqual(specification_list, actual_list)



### Run tests
unittest.main()
