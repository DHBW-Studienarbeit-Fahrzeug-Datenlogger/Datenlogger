# pylint: disable=no-member
"""
Created by: Max Vogt

Version: 1.0

Description:
    Script, that gets checks all available OBD2 Signals

"""

# Imports
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
from Signals import signals
from subprocess import call
# Moduls for DS18B20 temperature sensor
import glob
# Moduls for GPS sensor
from GpsPoller import GpsPoller
import RPi.GPIO as GPIO


def main(path):
    """
    connect to OBD2 Dongle
    check for available Signals, print them and write to file
    """
    # Necessary variables initialization
    # No connection yet
    connection = None
    not_connected = True
    has_connection = True

    # No OBD errors yet
    obd_error = 0
    filename = "available_obd_signals.txt"

    # Try to establish a connection with the OBD dongle
    while not_connected:
        try:
            # Connect to OBD dongle
            connection = obd.OBD()
            print(connection.status())

            # If the return of query RPM signal is not null
            # --> Connecting succeeded
            if (connection.status() == obd.utils.OBDStatus.CAR_CONNECTED and (
                    connection.query(obd.commands.RPM).is_null() == False)):
                not_connected = False
                print("Successful connected to OBDII!")  # Connecting to OBD dongle succeeded

                time.sleep(1)
            # Connection not successful: Sleep 1s before trying to connect to OBD dongle again
            else:
                time.sleep(1)
        # Cannot connect to the OBD: wait, add an OBD error and try again
        except Exception as e:
            print("Exception thrown was: ", e)
            print("Error Connecting to OBD-Adapter (" + str(obd_error) + ")")

            time.sleep(1)
            obd_error += 1

        # If could not connect to the OBD for the tenth time, use the only GPS
        # mode to log only the GPS and temperature signal
        if obd_error == 10:
            not_connected = False

    if connection.status() == obd.utils.OBDStatus.CAR_CONNECTED and has_connection:
        # Create an OBD command to get Signal Information
        get_pid01 = OBDCommand("PID01", "Get supported PIDs Service 1 (current data)", b"0100", 4, raw_string)
        get_pid09 = OBDCommand("PID09", "Get supported PIDs Service 9 (vehicle information)", b"0900", 4, raw_string)
        # Send the command to the OBD and accept the response
        pid01 = connection.query(get_pid01, force=True)
        pid09 = connection.query(get_pid09, force=True)

        f = open(path+filename, "w+")
        f.write("Available signals for gathering current data:\n {} \n}\n".format(pid01))
        f.write("Available signals for gathering vehicle information:\n {} \n}\n".format(pid09))
        f.close()
    else:
        print("no connection, signals won't be tested!")


# If script gets executed: execute main function
if __name__ == "__main__":
    path = "/home/pi/"
    main(path)
