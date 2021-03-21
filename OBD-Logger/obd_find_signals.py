# pylint: disable=no-member
"""
Created by: Max Vogt

Version: 1.0

Description:
    Script, that gets checks all available OBD2 Signals
-------------------------------------------------------------------
Update by: Max Vogt

Date: 30.12.2020

Version 1.1

Description:
    - adding more signals to be checks
    - bugfixes
-------------------------------------------------------------------
Update by: Max Vogt

Date: 21.03.2021

Version 1.2

Description:
    - adding check signals function
    - adding proper function descriptions

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


def obd_find_signals():
    """
    connects to obd dongle
    requests information about all potentially necessary signals
    returns answers individually in hex string format
    :return: 7 obd answers
    :rtype: str
    """
    # Necessary variables initialization
    # No connection yet
    connection = None
    not_connected = True
    has_connection = True

    # No OBD errors yet
    obd_error = 0

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
                print("Successfully connected to OBDII!")  # Connecting to OBD dongle succeeded

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
            return "0", "0", "0", "0", "0", "0", "0"

    if connection.status() == obd.utils.OBDStatus.CAR_CONNECTED and has_connection:
        # Create an OBD command to get Signal Information
        get_pid01_1 = OBDCommand("PID01_1", "Get supported PIDs Service 1 (current data) 1-20", b"0100", 4, raw_string)
        get_pid01_2 = OBDCommand("PID01_2", "Get supported PIDs Service 1 (current data) 21-40", b"0120", 4, raw_string)
        get_pid01_3 = OBDCommand("PID01_3", "Get supported PIDs Service 1 (current data) 41-60", b"0140", 4, raw_string)
        get_pid01_4 = OBDCommand("PID01_4", "Get supported PIDs Service 1 (current data) 61-80", b"0160", 4, raw_string)
        get_pid01_5 = OBDCommand("PID01_5", "Get supported PIDs Service 1 (current data) 81-A0", b"0180", 4, raw_string)
        get_pid01_6 = OBDCommand("PID01_6", "Get supported PIDs Service 1 (current data) A1-C0", b"01A0", 4, raw_string)
        get_pid09 = OBDCommand("PID09", "Get supported PIDs Service 9 (vehicle information)", b"0900", 4, raw_string)

        # Send the command to the OBD and accept the response
        pid01_1 = str(connection.query(get_pid01_1, force=True))
        pid01_2 = str(connection.query(get_pid01_2, force=True))
        pid01_3 = str(connection.query(get_pid01_3, force=True))
        pid01_4 = str(connection.query(get_pid01_4, force=True))
        pid01_5 = str(connection.query(get_pid01_5, force=True))
        pid01_6 = str(connection.query(get_pid01_6, force=True))
        pid09 = str(connection.query(get_pid09, force=True))
        return pid01_1, pid01_2, pid01_3, pid01_4, pid01_5, pid01_6, pid09


def check_signal(signal_number, signals):
    """
    takes a signals hex string
    converts into binary string
    checks whether or not a certain string position is 1

    :param signal_number: string position to be checked
    :type signal_number: int
    :param signals: concatenated hex string elements
    :type signals: str
    """
    signals_str = str(format(int(signals), '0>476b'))
    try:
        if signals_str[signal_number] == '1':
            return True
        else:
            return False
    except IndexError:
        return False


def main(path):
    """
    connect to OBD2 Dongle
    check for available Signals, print them and write to file
    :param path: file storage directory
    :type path: str
    """

    filename = "available_obd_signals.txt"
    pid01_1, pid01_2, pid01_3, pid01_4, pid01_5, pid01_6, pid09 = obd_find_signals()
    f = open(path + filename, "w+")
    f.write("Available signals for gathering current data:\n1: {}\n2: {}\n3: {}\n4: {}\n5: {}\n6:{}\n\n".format(pid01_1,
                                                                                                                pid01_2,
                                                                                                                pid01_3,
                                                                                                                pid01_4,
                                                                                                                pid01_5,
                                                                                                                pid01_6))
    f.write("Available signals for gathering vehicle information:\n {}\n\n".format(pid09))
    f.close()


# If script gets executed: execute main function
if __name__ == "__main__":
    path = "/home/pi/Studienarbeit_OBD_Datenlogger/OBD-Logger/Files/"
    main(path)
