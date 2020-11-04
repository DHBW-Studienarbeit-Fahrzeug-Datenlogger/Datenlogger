"""
Created by: Dennis Deckert, Pascal Hirsekorn, Silas Mayer, Chris Papke

Version: 1.0
    
Description:
    Contains the class GpsPoller for the constant providing of the current GPS
    data.
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



class GpsPoller(threading.Thread):
    """
    Thread:
    This class is responsible for reading the latetest temperature values from
    GPS module connected to the raspberry pi.
    
    Usage:
    gps = GpsPoller()
    gps.start()

    gps.get_current_value() --> get the latest value
    value is a JSON object containing the GPS data
    """
    
    
    def __init__(self):
        """
        Constructor:
            Create the thread
            Start the GPS module connected to the raspberry pi
            Start a GPS session
        """
        
        # Create thread
        threading.Thread.__init__(self)
        # Start GPS module
        os.system("sudo gpsd /dev/serial0 -F /var/run/gpsd.sock")

        # Create a session with the localhost and the port
        self.session = gps.gps("localhost", "2947")
        # Set the session in the watching mode so the GPS data is received constantly
        self.session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
        # No value yet. A value is a JSON object containing the data from the GPS
        self.current_value = None 
        # GPS measurement is running
        self.running = True 
        
        
    def get_current_value(self):
        """
        Returns the newest value.
        """
        return self.current_value
        
    
    def run(self):
        """
        Run the measurement:
            Gets the new current value, if session is running.
        """
        try:
            while self.running:
                # Get the next value
                self.current_value = self.session.next()
        # Cannot iterate (iteration number too big)
        except StopIteration:
            pass
            