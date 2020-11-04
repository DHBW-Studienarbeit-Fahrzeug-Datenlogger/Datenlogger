"""
Created by: Dennis Deckert, Pascal Hirsekorn, Silas Mayer, Chris Papke

Version: 1.0
    
Description:
    Contains the class util with diefferent useful methods for the processing
    of signal data.

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
from datetime import datetime, timedelta



class Util:
    """
    This class contains different util methods
    """

    @staticmethod
    def isfloat(value):
        """
        Checks, whether the given value is a float type.

        Parameters
        ----------
        value : not defined
            The value to be checked.

        Returns
        -------
        bool
            True, if the parameter is a float, otherwise False.

        """
        
        # Try to convert to flow. If possible --> True, if not --> False
        try:
            float(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def mean(value):
        """
        Calculates the mean of an array.

        Parameters
        ----------
        value : List
            List with floats for the calculation of the mean.

        Returns
        -------
        float
            The mean of the values in the list.

        """
        return (sum(value) / float(len(value)))

