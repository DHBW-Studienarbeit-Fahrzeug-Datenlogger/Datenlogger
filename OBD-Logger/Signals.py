"""
Created by: Dennis Deckert, Pascal Hirsekorn, Silas Mayer, Chris Papke

Version: 1.0
    
Description:
    Contains the class Signals that is used for the definition of the 
    available signal for measurement.

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
from OBDSignal import OBDSignal



### List defined signals

# A list with all defined signals
# To add a new signal to the datalogging, append it to this list
__signals__ = [
    #         SignalName                  description                     isOBDSignal  sampleRate     round
    # SIgnal of the time since the start of measurement
    OBDSignal("TIME"                    , "time"                           ,False      , 1         , 2),

    #OBD SIGNALS:
    OBDSignal("SPEED"                   , "speed"                          ,True       , 1         , 2),
    OBDSignal("RPM"                     , "rpm"                            ,True       , 1         , 2),
    OBDSignal("ENGINE_LOAD"             , "engine_load"                    ,True       , 1         , 2),
    OBDSignal("MAF"                     , "maf"                            ,True       , 1         , 2),
    OBDSignal("AMBIANT_AIR_TEMP"        , "ambiant_temperature"            ,True       , 1         , 2),
    OBDSignal("RELATIVE_ACCEL_POS"      , "pedal"                          ,True       , 1         , 2),
    OBDSignal("COMMANDED_EQUIV_RATIO"   , "afr"                            ,True       , 1         , 2),
    OBDSignal("FUEL_LEVEL"              , "fuel_level"                     ,True       , 2         , 2),

    #GPS SIGNALS:
    OBDSignal("GPS_Long"                , "Longitude"                      ,False      , 2         , 9),
    OBDSignal("GPS_Lat"                 , "Latitude"                       ,False      , 2         , 9),
    OBDSignal("GPS_Alt"                 , "Altitude"                       ,False      , 2         , 9),
    OBDSignal("GPS_Time"                , "time"                           ,False      , 2         , 0),
    #TEMPERATURE SIGNAL
    OBDSignal("INTERNAL_AIR_TEMP"       , "internal_temperature"           ,False      , 4         , 2),
    #VIN OF THE CAR (Not OBD, only read once)
    OBDSignal("VIN"                     , "Vehicle Identification Number"  ,False      , 0         , 0), #VIN is not an OBD Signal because its only necessary to read once
    
]


class Signals:
    """
    Class that contains the list of defined signals from above.
    Contains methods to process this list and to transfer the defined
    information to the datalogger.
    """
    
    
    def __init__(self):
        """
        Constructor:
            Include the list of defined signals and create a dictionary
            with the signal names as keys and the signal objects as values.
        """
        
        # Include list of defined signals
        self.signals = __signals__

        # Create a dictionary
        for s in self.signals:
            if s is not None:
                self.__dict__[s.name] = s


    def __getitem__(self, key):
        """
        Signals can be accessed by different ways
        signals.RPM
        signals.["RPM"]
        signals.[1]
        """
        # Return the signal at the position of a given number
        if isinstance(key, int):
            return self.signals[key]
        # Return the signal with the given name
        elif isinstance(key, str):
            return self.__dict__[key]
    
    
    def getTimeSignal(self):
        """
        Returns the signal TIME.
        This is not the time from the GPS.
        """
        return [x for x in self.signals if x.name == "TIME"][0]


    def getSignal(self, name):
        """
        Returns a signal by its name.
        """
        return [x for x in self.signals if x.name == name][0]


    def getOBDSignalList(self):
        """
        Returns a list of the signals that are OBD ones.
        """
        return [x for x in self.signals if x.isOBDSignal == True]


    def getSignalList(self):
        """
        Returns a list of all defined signals.
        """
        return self.signals


    def containsSignalByString(self, str):
        """
        Returns (boolean) whether the given string is the name of a defined
        signal.
        """
        for s in self.signals:
            if(s.name == str):
                return True
        return False


    def containsSignal(self, signal):
        """
        Returns (boolean) whether the given object is one of the defined
        signals.
        """
        
        # Check if given object is an OBDSignal-object. If not, raise an error
        if not isinstance(signal, OBDSignal):
            raise ValueError("Value has to be instance of OBDSignal")
            
        # Check if the given OBDSignal-object equals one in the list
        for s in self.signals:
            if(s == signal):
                return True
        return False



### Signals object creation

# Create an object of the Signals-class
signals = Signals()



