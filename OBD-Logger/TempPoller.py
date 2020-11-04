"""
Created by: Dennis Deckert, Pascal Hirsekorn, Silas Mayer, Chris Papke

Version: 1.0
    
Description:
    Contains clas TempPollers for the constant providing of the current 
    temperature (every 2s).
    In the script OBD.py it is used as an own thread.

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
import os 
from gps import *
import gps
from time import *
import time 
import threading 
import glob
import RPi.GPIO as GPIO



class TempPoller(threading.Thread):
    """
    Thread:
    This class is responsible for reading the latetest temperature values from
    DS18BD temperature sensor.
    
    Usage:
    temp = TempPoller()
    temp.start()

    temp.get_current_value()  --> get the latest value
    """
    
    def __init__(self):
        """
        Constructor:
            Create the thread
            Configure the GPIOs of the raspberry pi
            Get the device file containing the output of the sensor
        """
        
        # Create thread
        threading.Thread.__init__(self)
        
        # Use the BCM numeration for the GPIOs
        GPIO.setmode(GPIO.BCM)
        # GPIO 4 as an input with a pull down resistor
        GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Set the basic directory to get to the device file
        base_dir = '/sys/bus/w1/devices/'

        device_folder = None

        # Find the device folder in the basic directory
        try:
            device_folder = glob.glob(base_dir + '28*')[0]
        except IndexError:
            device_folder = None
        print(device_folder)

        # If the folder was found, set the device file and start a measurement
        if (device_folder != None):
            # Set the path to the device file as attribut
            self.device_file = device_folder + '/w1_slave'
            self.TemperaturMessung(self.device_file)
        # If folder was not found, the device file is None, too
        else:
            self.device_file = None
        print(self.device_file)
        
        # No value yet
        self.current_value = None 
        # Measurement of temparature is running
        self.running = True 
        
        
    def get_current_value(self):
        """
        Return the newest value.
        """
        return self.current_value
        
    
    def run(self):
        """
        Run the measurement:
            Gets the next value every two seconds, as long as measurment is 
            running.
        """
        try:
            while self.running:
                # Extract the next value from the device file
                self.current_value = self.TemperaturAuswertung(self.device_file)
                # Wait two seconds
                time.sleep(2)
        # Cannot iterate (iteration number too big)
        except StopIteration:
            pass


    def TemperaturMessung(self, device_file):
        """
        Open the device file and read its content as a list of lines.
        This list is returned.
        """
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines


    def TemperaturAuswertung(self, device_file):
        """
        
        """
        # If the device file is existing
        if (device_file != None):
            # Get the lines from the device file
            lines = self.TemperaturMessung(device_file)
            
            # While the first line ends with "YES", wait 0.1 seconds and read
            # the lines again
            while lines[0].strip()[-3:] != 'YES':
                time.sleep(0.1)
                lines = self.TemperaturMessung(device_file)
                
            # Find the position of "t=" in the second line
            equals_pos = lines[1].find('t=')
            
            # If the position was found, extract the string representing 
            # the temperature and prepare as a float
            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                
            # Return the temperature or None, if the device file was not found
            # or the device file does not contain "t=" in its second line
                return temp_c
            else:
                return None
        else:
            return None
