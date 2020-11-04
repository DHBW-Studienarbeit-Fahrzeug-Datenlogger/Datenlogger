"""
Created by: Dennis Deckert, Pascal Hirsekorn, Silas Mayer, Chris Papke

Version: 1.0
    
Description:
    Contains the class OBDSignal for the definition and configuration of every
    signal, not only the OBD ones.

-------------------------------------------------------------------------------

Update by: Tim Hager

Date: 04.11.2020

Version 1.0

Description:
    - Commentation of code
    - Creation of header
    - Basic structuring   
    
"""



class OBDSignal:
    """
    Class for the representation of a signal
    """

    def __init__(self, name, db_name, isOBDSignal, sampleRate, roundDigit):
        """
        Constructor:
            signal name, database name, OBD signal bool, sample rate, round 
            digit
        """
        # Name of the signal
        self.name = name
        # Name of the signal in the database
        self.db_name = db_name
        # Whether the signal is an OBD one
        self.isOBDSignal = isOBDSignal
        # Sample rate of the signal (different signals have different sample rates)
        self.sampleRate = sampleRate
        # How many digits after the comma
        self.roundDigit = roundDigit


    def __str__(self):
        """
        Returns the representing string for the signal.
        """
        return "%s" % (self.name)


    def __eq__(self, other):
        """
        Is the given object the same as this one. --> Equals-method
        """
        # Check if object is from the same class
        if isinstance(other, OBDSignal):
            # Check if the name is the same
            return self.name == other.name and self.sampleRate == other.sampleRate




















