# pylint: disable=no-member
"""
Created by: Dennis Deckert, Pascal Hirsekorn, Silas Mayer, Chris Papke

Version: 1.0
    
Description:
    Script that gets executed when the datalogging raspberry pi boots.
    Control the process of datalogging.

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
import obd
from obd import OBDCommand, Unit
from obd.protocols import ECU
from obd.decoders import raw_string
import time
import csv
import datetime
import gps
import sys
import os
from LogFile import LogFile, LogStatus         
from Signals import signals
from uptime import uptime
from subprocess import call
#Moduls for DS18B20 temperature sensor
import glob
from TempPoller import TempPoller
#Moduls for GPS sensor
from GpsPoller import GpsPoller
import RPi.GPIO as GPIO



def main():
    """
    Main function to execute the datalogging process. When the script gets
    executed, this function will be executed.
    """
    
    ### GPIO configuration
    
    # BCM numeration for the GPIOs
    GPIO.setmode(GPIO.BCM)
    # Configure the GPIOs as outputs
    GPIO.setup(17,GPIO.OUT)
    GPIO.setup(27,GPIO.OUT)
    GPIO.setup(22,GPIO.OUT)
    # No warnings
    GPIO.setwarnings(False)

    # Define variables for the GPIOs representing the color for the RGB
    RGBblue =  17
    RGBred = 27
    RGBgreen = 22
    
    # Set the RGB to white light (all colors)
    GPIO.output(RGBblue, GPIO.LOW)
    GPIO.output(RGBred,GPIO.LOW)
    GPIO.output(RGBgreen,GPIO.LOW)
    GPIO.output(RGBblue,GPIO.HIGH)
    GPIO.output(RGBred,GPIO.HIGH)
    GPIO.output(RGBgreen,GPIO.HIGH)
    
    ### Create threads (GPS & temperature)
    
    # Create an instance of the GpsPoller and start the thread for its polling
    gpsp = GpsPoller()
    gpsp.start()
    
    # Create an instance of the TempPoller and start the thread for its polling
    temperature = TempPoller()
    temperature.start()
    
    ### Necessary variables initialization
    
    # Line counter. Is necessary to manage the different sample rates of the 
    # different signals
    i = 0
    # No connection yet
    connection = None           
    NotConnected = True
    #Error count to detect the moment when ignition is turned off at the end 
    # of a Driving Cycle
    errorcnt = 0
    
    HasConnection = True

    # Not only GPS logging (yet) --> emergeny mode if no connection to the OBD
    OnlyGPSMode = 0
    # No OBD errors yet
    OBDError = 0
    # Create a CSV file name with the date, time and suffix "test"
    filename = datetime.datetime.now().strftime("%y_%m_%d_%H:%M:%S_") + "test.csv"
    
    
    # Get the time how long the system is on
    start = uptime()
    
    ### Set up OBD connection

    #Try to establish a connection with the OBD dongle
    while NotConnected:
        try:
            # Connect to OBD dongle
            connection = obd.OBD()              
            print(connection.status())
            
            # If the return of query RPM signal is not null
            # --> Connecting succeeded 
            if(connection.status() == obd.utils.OBDStatus.CAR_CONNECTED and (connection.query(obd.commands.RPM).is_null() == False)):
                NotConnected = False
                print("Successful connected to OBDII!") #Connecting to OBD dongle succeeded

                time.sleep(1)
            # Connection not successful: Sleep 1s before trying to connect to OBD dongle again
            else:
                time.sleep(1)
        # Cannot connect to the OBD: wait, add an OBD error and try again
        except:
            print("Error Connecting to OBD-Adapter (" + str(OBDError) + ")")
            
            time.sleep(1)
            OBDError += 1
        
        # If could not connect to the OBD for the tenth time, use the only GPS
        # mode to log only the GPS and temperature signal
        if(OBDError == 10):
                NotConnected = False
                OnlyGPSMode = 1
          
    ### Creation LogFile object and variables
    
    # Create an object of LogFile
    log = LogFile()
    
    # Reset the OBD errors to 0
    OBDError = 0
    # Mode has been stated, need to start only GPS mode or normal mode
    temp = True
    
    # Prefix and suffix for the logfile that will be created, to difference
    # between a file for the normal or the only GPS mode
    stri = ""
    stri_end = ""
    
    ### Handling onlyGpsMode
    
    # Handle only GPS Mode: check if GPS data available (until connection works)
    while(temp and OnlyGPSMode == 1):
        # Get the current value from the GPS
        report = gpsp.get_current_value()
        
        ### Check for GPS connection
        
        # If the JSON objecthas the right class, there is a GPS connection
        if report['class'] == 'TPV':
            # If the longitude, latitude and altitude are existing, the 
            # connection was successful
            if hasattr(report, 'lon') and hasattr(report, 'lat') and hasattr(report, 'alt'):
                print("GPS found-> Only GPS Mode")
                #Set Colour to Cyan
                GPIO.output(RGBblue, GPIO.LOW)
                GPIO.output(RGBred,GPIO.LOW)
                GPIO.output(RGBgreen,GPIO.LOW)
                GPIO.output(RGBblue, GPIO.HIGH)
                
                # Set the prefix and suffix to mark the CSV file for only GPS
                stri = "GPS_"
                stri_end = "x"
                
                # Set that the only GPS mode can be executed
                OnlyGPSMode = 2
                temp = False
        # Not able to connect: Wait a second and try again
        else:
            time.sleep(1)
    
    ### Creation logfile
    
    # Create a logfile
    log.createLogfile(stri + filename + stri_end)
    
    # No VIN yet
    vin = None

    # Get the time how long the system is on
    start = uptime()
    
    
    ### Perform datalogging
    try:
        ### Execute onlyGpsMode
        while(OnlyGPSMode == 2):
            # Line counter for control of sample rates
            i = i+1
            # If the counter is too big (--> StopIteration): reset
            if(i == 2048): 
                i = 0
            # Execute the function for the only GPS mode
            GPS_Only(log, i, start, temperature, gpsp)


        ### Execute normal mode
        
            ### Set up normal mode

        # If OBD is successfully connected: Set the normal mode up
        if(connection.status() == obd.utils.OBDStatus.CAR_CONNECTED and HasConnection):
            # Create an OBD command to get the VIN
            c = OBDCommand("VIN", "Get Vehicle Identification Number",  b"0902", 20, raw_string, ECU.ENGINE, False)
            # Send the command to the OBD and accept the response
            response = connection.query(c, force=True)
            # Parse the VIN from the OBD response
            vin = LogFile.parseVIN(response.value)
            print(vin)
            
            #connection.close()
            
            # Change to asynchronous connection: last value always immediatly
            # retrievable
            connection = obd.Async()
            
            # Keep track of the RPM (constantly get its value)
            connection.watch(obd.commands.RPM)
            # Keep track of every defined OBD signal
            for signal in signals.getOBDSignalList():
                connection.watch(obd.commands[signal.name])
                
            # Start the update loop of the OBD values
            connection.start()
            
            # Wait a moment
            time.sleep(0.5)
            
            # Set RGB colour to pink
            GPIO.output(RGBblue, GPIO.LOW)
            GPIO.output(RGBred,GPIO.LOW)
            GPIO.output(RGBgreen,GPIO.LOW)
            GPIO.output(RGBblue, GPIO.HIGH)
            GPIO.output(RGBred, GPIO.HIGH)
            
            
            ### Perform normal mode
                
        #Normal Mode: OBD-, GPS-, Temperature-Data
        while (connection.status() == obd.utils.OBDStatus.CAR_CONNECTED and HasConnection):
            
                ### Ignition off?
            
            # Error handling to detect IGNITION OFF Signal (RPM is 0 then)
            if(connection.query(obd.commands.RPM).is_null() == True): 
                print("Error")
                errorcnt += 1
                print(errorcnt)
            # If RPM is not 0, reset the errors (just a disruption)
            else:
                errorcnt = 0

            # If the fifth error occured,most likely the ignition is off
            if(errorcnt >= 5):
                print("End: Too many Errors - Ignition seems to be off")
                # No connection anymore
                HasConnection = False
                # Turn off the RGB
                GPIO.output(RGBblue, GPIO.LOW)
                GPIO.output(RGBred,GPIO.LOW)
                GPIO.output(RGBgreen,GPIO.LOW)

                ### Signal recording

            # Increment the line counter for the control of the sample rates
            i = i+1
            # If counter is too big, reset becuase of StopIteration
            if(i == 2048): 
                i = 0

            #Get actual time data
            #timestr = str(datetime.datetime.now())
            # Get the time how long the system is on
            timestr = uptime()
            # Calculate the time since the start of measurement
            timestr = timestr - start
            
            # Create a list to for the signal values
            result = []
            # Append the calculated time
            result.append(timestr)

            #Set the GPS and Temperature variables to initial values (for the
            # case that no value is recorded)
            lon = None
            lat = None
            gpsTime = None
            internalTemp = None
            alt = None
            
            # Get GPS data (if possible)
            if(i % signals.getSignal("GPS_Long").sampleRate == 0):
                report = gpsp.get_current_value()
                (lon, lat, alt, gpsTime) = getGpsData(report)

            # Get internal tempterature data
            if (i % signals.getSignal("INTERNAL_AIR_TEMP").sampleRate == 0):
                internalTemp = temperature.get_current_value()
            
            # Get OBD data for every defined OBD signal
            for signal in signals.getOBDSignalList():
                # Handle the different sample times (with counter i)
                if(i % signal.sampleRate == 0):
                    r = connection.query(obd.commands[signal.name])
                    # If the response is null, append a 0 as value, else the 
                    # returned value
                    if r.is_null():
                        result.append(0)
                    else:
                        result.append(r.value.magnitude)
                # If no smaple for this time, append None
                else:
                    result.append(None)
            
            # Append GPS-Data (if available)
            result.append(lon)
            result.append(lat)
            result.append(alt)
            result.append(gpsTime)
            
            # Append Temperature-Data (if available)
            result.append(internalTemp)
            result.append(vin)
            
                ### Recorded data to buffer

            # Append the list of values to the buffer (dictionary of the 
            # signals with a list of its values as value)
            log.addData(result)
            
            # Write the VIN only once --> does not change and reduce data amount
            if(vin != None):
                vin = None

            # Wait a moment to limit the data amount
            time.sleep(0.5)
            
                ### Buffer to file
            
            # Every 20 rows of measurement: append the buffer data to the CSV file
            if(i % 20 == 0):
                log.appendFile()
                print("Appending File ...")

        ### Ignition is off
        
        # Append the buffer data to the CSV file
        log.appendFile()
        
        print("Ignition Off")
        print("\nKilling Threads..")
        
            ### End threads
        
        # End the GPS polling thread
        gpsp.running = False 
        gpsp.join()
        
        # End the temperature polling thread
        temperature.running = False
        temperature.join()
        
            ### Disconnect OBD
        
        # Stop the connection to the OBD
        connection.stop()
        
            ### Configure GPIOs
        
        # Turn off the RGB
        GPIO.output(RGBblue, GPIO.LOW)
        GPIO.output(RGBred,GPIO.LOW)
        GPIO.output(RGBgreen,GPIO.LOW)
        # Reset the GPIO status
        GPIO.cleanup()


    ### Error occured
    except(KeyboardInterrupt, SystemExit):
        ### Configuration GPIOs
        
        # Turn of the RGB
        GPIO.output(RGBblue, GPIO.LOW)
        GPIO.output(RGBred,GPIO.LOW)
        GPIO.output(RGBgreen,GPIO.LOW)
        # Reset the GPIO status
        GPIO.cleanup()
        
        print("Excpetion:")
        print("\nKilling Threads..")
        
        ### Buffer to file
        
        # Append the buffer data to the CSV file
        log.appendFile()
        
        ### End threads
        
        # End the GPS polling thread
        gpsp.running = False 
        gpsp.join()
        
        # End the temperature polling thread
        temperature.running = False
        temperature.join()
        
        ### Disconnect OBD
        
        # Stop the connection to the OBD
        connection.stop()
        
    
           
def getGpsData(report):
    """
    Get the next GPS JSON object. Extract and return the GPS data.
    """
    
    # Default values for GPS data (e.g. if no sample is recorded this time)
    lon = None
    lat = None
    alt = None
    gpsTime = None
    
    # If response has the right class, extract the GPS data
    if report['class'] == 'TPV':
        if(hasattr(report, 'time')):  
            # Get GPS time                  
            gpsTime = report.time
        if hasattr(report, 'lon') and hasattr(report, 'lat') and hasattr(report, 'alt') and hasattr(report, 'time'):
            # Get GPS coordinates
            lon = report.lon
            lat = report.lat
            alt = report.alt   
            # Get GPS time                 
            gpsTime = report.time
            
            print("Lon:  ", lon)
            print("Lat: ", lat)
    return (lon, lat, alt, gpsTime)



def GPS_Only(log, i, start, temperature, gpsp):
    """
    Mode for only GPS and temperature logging.
    """

    #Get actual time data
    #timestr = str(datetime.datetime.now())
    # Get the time how ling the system is on
    timestr = uptime()
    # Calculate the time since mesaurment beginning
    timestr = timestr - start
    
    ### Record signals
    
    # Create list for the signal values
    result = []
    # Append the calculated time value
    result.append(timestr)
    
    #Set the GPS and Temperature variables to initial values
    lon = None
    lat = None
    alt = None
    gpsTime = None
    internalTemp = None
    
    # No VIN yet
    vin = None
        
    # Get GPS data
    if(i % signals.getSignal("GPS_Long").sampleRate == 0):
        report = gpsp.get_current_value()
        (lon, lat, alt, gpsTime) = getGpsData(report)

    # Get internal Temperature-Data
    if(i % signals.getSignal("INTERNAL_AIR_TEMP").sampleRate == 0):
        internalTemp = temperature.get_current_value()

    # Append None for OBD signals
    for signal in signals.getOBDSignalList():
        result.append(None)
    
    # Append GPS data to values list
    result.append(lon)
    result.append(lat)
    result.append(alt)
    result.append(gpsTime)
    
    # Append internal temperature data to values list
    result.append(internalTemp)
    result.append(vin)
    
    ### Recorded data to buffer
    
    # Append the list of values to the buffer (dictionary of the 
    # signals with a list of its values as value)
    log.addData(result)

    # Wait a moment to reduce amount of data
    time.sleep(0.5)
    
    ### Buffer to file
    
    # Every 10 rows of measurement: Append the data of teh buffer to the CSV file
    if(i % 10 == 0):
        log.appendFile()
        print("Appending File ...")




### Calling main function

# If script gets executed: execute main function
if __name__ == "__main__":
    main()