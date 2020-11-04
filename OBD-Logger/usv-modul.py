# pylint: disable=no-member
"""
Created by: Dennis Deckert, Pascal Hirsekorn, Silas Mayer, Chris Papke

Version: 1.0
    
Description:
    Configures and controls the interuption free supply.

-------------------------------------------------------------------------------

Update by: Tim Hager

Date: 04.11.2020

Version 1.0

Description:
    - Commentation of code
    - Creation of header
    - Basic structuring   
    
"""



### Imports
from LogFile import LogFile
import subprocess
import signal
import time
import os
import socket
import env
import shutil
import RPi.GPIO as GPIO



### Configuration GPIOs

# No Warnings
GPIO.setwarnings(False)
# BOARD numeration for the GPIOs
GPIO.setmode(GPIO.BOARD)
# GPIOs 19, 23, 21 as output ports
GPIO.setup(19,GPIO.OUT)
GPIO.setup(23,GPIO.OUT)
GPIO.setup(21,GPIO.OUT)
# Set GPIO 21 to HIGH
GPIO.output(21, GPIO.HIGH)



def timeout_handler(num, stack):
    """
    Raises an error for the case t5hat no wireless network is connected.
    """
    print("Received SIGALRM")
    raise Exception("No wireless networks connected")


### Timeout handler creation

# Create timeout handler
signal.signal(signal.SIGALRM, timeout_handler)
# Wait for 20s til the system will be shut down
signal.alarm(20)


### Try

try:
    ### Creation LogFile object
    
    print(env.PATH)
    # Create an object of the class LogFile --> logging
    log = LogFile()
    # Get the file names of the LogFile
    files = LogFile.getFilenames()
    print(files)
    
    ### Transfer every CSV file to server
    
    # For every file of the LogFile
    for file in files:
        # Load the file from the LogFile: Loads the data from the csv file     
        log.loadFromFile(file)
        
        ### Delete Files without content
        if(log.isBrokenFile()):
            # If the file path exists, delete it and write the action to the log
            if os.path.exists(env.PATH + file):
                os.remove(env.PATH  + file)
                print("[DELETE] broken file: " + str(file))
                with open( env.PATH + "LOG.log", "a") as f:
                    f.write("[DELETE]: " + str(file) +  " - File was broken (No GPS or RPM signals) "+ "\n")
            continue
        
        ### Transfer of JSON to server
        
        # If file has content, transfer the data to a JSON object
        filename = log.transferToJson()
        print(filename)
        
        # Transfer the file to the server
        success, err = log.copyFileToServer(filename)
        print(success)
        print(err)
        
        # If transfer was successful, set the RGB to the corresponding color
        # and append the successful transfer to the log
        if(success):
            print("Success!!")
            GPIO.output(19, GPIO.HIGH)
            with open( env.PATH + "LOG.log", "a") as f:
                f.write("Success: " + str(file) + "(" + str(filename) + ") has been copied to Server\n")
                
            # If file exists in the path (defined in env), copy the file to
            # the folder OLD and delete it from the current directory
            if os.path.exists(env.PATH + file):
                shutil.copy2(env.PATH + file, env.PATH + "OLD/")
                print("copy file to old folder")
                os.remove(env.PATH  + file)
                print("[DELETE] " + str(file))
                
            # If the corresponding JSON file exists, delete it
            if os.path.exists(env.PATH + "JSON/" +  filename):
                os.remove(env.PATH  + "JSON/" + filename)
                print("[DELETE] " + str(filename))
            
        # If transfer was not successful, set the correspondig color to the RGB
        # and write the unsuccessful transfer to the log
        else:
            GPIO.output(23, GPIO.HIGH)
            with open( env.PATH + "LOG.log", "a") as f:
                f.write("Error: " + str(file) + "(" + str(filename) + ") could not be copied to Server: "+ str(err) + "\n")
           
### Except     
           
# If the above was not successful, set the RGB to the corresponding color and
# let it blink three times
except Exception as ex:
    print(ex)
    for i in range(3):
        GPIO.output(23, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(23, GPIO.LOW)
        time.sleep(0.1)
        
        
### Finally
        
# No matter if the above was successful or not, wait a second, turn the RGB of 
# and set the timeout handler to 0. The system will shut down.
finally:
    time.sleep(1)
    GPIO.output(23, GPIO.LOW)
    GPIO.output(19, GPIO.LOW)
    GPIO.output(21, GPIO.LOW)
    signal.alarm(0)
    


