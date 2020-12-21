# pylint: disable=no-member
"""
Created by: Dennis Deckert, Pascal Hirsekorn, Silas Mayer, Chris Papke

Version: 1.0
    
Description:
    Contains classes to process and log the data from the different sources, 
    such as OBD II, GPS module, temperature sensor.

-------------------------------------------------------------------------------

Update by: Tim Hager

Date: 04.11.2020

Version 1.0

Description:
    - Commentation of code
    - Creation of header
    - Basic structuring   
    
-------------------------------------------------------------------------------

Update by: Maximilian Vogt

Date: 21.12.2020

Version 1.1

Description:
    - Syntax error corrections
    - new import height_profile module (contains everything needed to build a height profile)
    - new objects in LogFile class
        1) self.height_profile_dict = None
        2) self._filename_height_profile = ""
    - adding height profile calculation to loadFromFile
        1) build json with calculated data
        2) filepath is saved in self._filename_height_profile
    - adding filename_height_profile to StringBuilder
    - changing transmitToSQL call
    - adding filename_height_profile to transmitToSQL
"""



### Imports
import csv
import os
import datetime    
import mysql.connector
import env
import os
import subprocess
import socket
import json
import bcrypt
from subprocess import Popen, PIPE
from datetime import datetime, timedelta
from Util import Util
from statistics import mean
from Signals import signals
import height_profile


# Fuer Raspberry bzw. Linux --> + "/Files/" Bei Windows: "\\OBD-Logger\\Files\\"
# "/Files/" #"\\OBD-Logger\\Files\\"

### Constants

# Constant for the basic directory from the env
path = env.PATH

#path = "/home/pi/Studienarbeit_OBD_Datenlogger/OBD-Logger/Files/"


class LogStatus:
    """
    Defines the Log status flags 
    """
    
    NO_LOGFILE = "No LogFile"
    LOG_CREATED = "LogFile created"
    LOG_FILE_LOADED = "LogFile loaded from File"
    

class Stringbuilder:
    """
    Class for building a string for the upload of a file to the MySql server
    """
    
    @staticmethod
    def SqlAddEntry(filename_raw_data, date, starttime, totalKM, endtime, VIN, fuelConsumption, energyConsumption, endLat, endLong, endDate, filename_height_profile):
        """
        Create query string to load new file to db
        SqlAddEntry(filename, date, starttime, totalKM, endtime, VIN, fuelConsumption, energyConsumption, endLat, endLong, endDate, filename_height_profile)
        date: MM-DD-YYYY
        time: HH:MM:SS
        """
        
        sql = "INSERT INTO  data ( filename_raw_data, date, starttime, totalKM, endtime, VIN, fuelConsumption, " \
            + "energyConsumption, endLat, endLong, endDate, filename_height_profile) VALUES ('" + str(filename_raw_data) \
            + "', '" + str(date) + "', '" + str(starttime) \
            + "', '" + str(totalKM) + "', '" + str(endtime) + "', '" + str(VIN) + "', '" + str(fuelConsumption) \
            +"', '" + str(energyConsumption) + "', '" + str(endLat) + "', '" + str(endLong) \
            + "', '" + str(endDate) + "', '" + str(filename_height_profile) + "')"

        return sql


class LogFile:
    """
    Class to log data from the OBDII adapter, GPS module and temperature sensor.
    """

    @staticmethod
    def getFilenames():
        """
        Returns a sorted List of the file names which are located in the basic
        path (defined at the beginning of the file).
        """
        return sorted([f for f in os.listdir(path) if f.endswith('.csv')])

    @staticmethod
    def parseVIN(res):
        """
        Parse the VIN from the OBD response to a VIN string.
        """
        
        # Split the response from the OBD into its lines
        str1 = res.split('\n')
        # VIN empty yet
        VIN = ""
        # Extract VIN part from first line
        str10 = str1[0].split("490201")[-1]
        # Add VIN part to VIN
        VIN = VIN + str(str10)
        # Extract more parts from the second and third lines and append to VIN
        VIN = VIN + str(str1[1][5:]) + str(str1[2][5:])
        # Convert the VIN from hex to an utf-8 coded string
        VIN = bytes.fromhex(VIN).decode("utf-8")
        
        return VIN

    def __init__(self):
        """
        Constructor:
                Initialize attributs.
                Create a dictionary of the signals with the signal names as keys
                and a yet empty list as value.
                Set status to NO_LOGFILE.
        """
        self._filename_raw_data = ""
        self._VIN = ""
        
        # Create dictionary of signals
        self._data = {

        }
        for s in signals.getSignalList():
            self._data[s.name] = []

        # Set status
        self._status = LogStatus.NO_LOGFILE
        
        # File is not broken yet
        self._isBrokenFile = False

        # height profile
        self.height_profile_dict = None
        self._filename_height_profile = ""

    def status(self):
        """
        Returns status of the object.
        """
        return self._status

    def isBrokenFile(self):
        """
        Returns if the file is broken (attribut _isBrokenFile).
        """
        return self._isBrokenFile

    def getDataDict(self):
        """
        Returns dictionary of the signals.
        """
        return self._data

    def transferToJson(self):
        """
        Transfers the dictionary of the signals to a JSON object and file.
        Returns the file name of the JSON file.
        
        First call "loadFromFile", otherwise the CSV content is not stored 
        in the dictionary, but only the last buffered data.
        """
        
        # Get the dictionary of the signals
        data = self._data
        
        # Remove the VIN from the dictionary (no signal to be tracked)
        if("VIN" in data):
            data.pop("VIN")

        # Create path to the JSON directory
        jsonPath = path + "JSON/"
        # Get the file name of the CSV file
        filename = self._filename_raw_data
        # Create a JSON file with the same file name and write the dictionary
        # as a JSON object to the file
        with open( jsonPath + filename.split(".csv")[0] + ".json", 'w') as fp:
            json.dump(data, fp)
        
        return filename.split(".csv")[0] + ".json"

    def copyFileToServer(self, filename):
        """
        Establishes a connection to the MySql server and transmits the 
        JSON file.
        """
        
        # No connection error yet
        errcnt = 0
        
        # List for the available IPs
        ip = []
        
        # Read the last connected IP address from the file ipAddress.ip
        f = open(env.PATH_REPO + "ipAddress.ip", "r")
        ipAddress = f.read()

        # Try saved IP address
        
        # If there is an IP in the file, scan port 22 for IPs
        if(not ipAddress == ""):
            # Scan for the IP and save the output
            stri = str(subprocess.check_output(('nmap -p22 ' + str(ipAddress)), shell=True))
            
            # If "open" is in the output, append the last connected IP from
            # the file to the list of IPs
            if(stri.find("open") != -1):
                ip.append(str(ipAddress))
                
        # Scan for possible IP addresses
                
        # If no IP in file, create a new socket
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Connect the socket to the server with address 8.8.8.8
            s.connect(('8.8.8.8', 1))
            # Get the IP address of the socket
            own_ip = str(s.getsockname()[0])
            
            # Create an IP mask from the socket IP to look for similar IPs
            ip_mask = ".".join(own_ip.split('.')[0:-1]) + ".*"
            # Check port 22 for IPs matching with the created IP mask
            stri = str(subprocess.check_output(('nmap -p22 ' + str(ip_mask)), shell=True))
            # Split the output ino its lines
            output = stri.split("\\n")

            # Inspect every line from the output
            for i, line in enumerate(output):
                # If there is "open" in the line and the IP extracted from the 
                # line is not the IP of the socket, append it to the list of IPs
                if(line.find("open") != -1 and output[i-3].split(' ')[-1] != own_ip):
                    ip.append(output[i-3].split(' ')[-1].replace("(", "").replace(")",""))
                    print(ip)
        
        # Try connecting to server
        
        # If there is at least one IP stored in the list, execute the following
        if(len(ip) >= 1):        
            # Execute the following for every IP in the list
            for i, tmp in enumerate(ip):
                # Create a command to send the JSON file to the database server
                cmd = "sshpass -p '" + str(env.DB_PASSWORD) + "' scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/home/pi/known_host -r " + str(path) + "JSON/" + str(filename) + " pi@" + str(ip[i]) +":datafiles/"
                # Create a new process with pipes for the channels (std) and 
                # execute the created command
                proc =  Popen([cmd], stdin=PIPE, stdout=PIPE,  stderr=PIPE, shell=True)
                # Interact with process and read the output and error channel
                stdout, stderr = proc.communicate()
                print(stderr)
                
                # If there occured no error from the command, execute the following
                if stderr == b'' or stderr.endswith(b'to the list of known hosts.\r\n'):
                    # Try to transmit the data to the database. If successful
                    # write the used IP to the file ipAddress.ip
                    try:
                        self.transmitToSQL(filename_raw_data=filename,
                                           ip=str(ip[i]),
                                           filename_height_profile=self._filename_height_profile)
                        f = open(env.PATH_REPO + "ipAddress.ip", "w")
                        f.write(str(ip[i]))
                    # If connection error to the MySql, return the error
                    except mysql.connector.errors.IntegrityError as err:
                        return False, err
                    # If successful, return positive statement
                    return True, ""
                # If error occured from the command, continue to next IP.
                # If it was last IP, return negative statement
                else:
                    if(len(ip)-1  == i):
                        return False, ""
                    
        # Connection not possible
        
        # If no IP in the list, return negative statement (no server connection)
        else:
            return False, "No Server connection found!"

    def createLogfile(self, filename):
        """
        Create a logfile (CSV) to track the signal data.
        """
        try:
            # Create the file with the file name in the basic path
            with open(path+filename, 'w', newline='') as file:
                # Create an CSV writer without automatic data convertion
                wr = csv.writer(file, quoting=csv.QUOTE_MINIMAL)
                # Auto generate Header from signals in Signals.py (which column
                # for which signal)
                header = [s.name for s in signals.getSignalList()]
                # Write the header to the file
                wr.writerow(header)
                
        # If file could not be created, print error
        except:
            print("Error! Creating File failed")

        # Set the file name as attribut and change the status to LOG_CREATED
        self._filename_raw_data = filename
        self._status = LogStatus.LOG_CREATED

    def addData(self, signalList):
        """
        Add the recorded signal data to the buffer.
        The buffer is the dictionary of the signals in the attributs (_data).
        """
        
        # If the given signal list has the correct size, iterate over the signals
        if(len(signals.getSignalList()) == len(signalList)):
            for i, s in enumerate(signals.getSignalList()):
                # If it one of the specified signals, append the value from the
                # list to the buffer
                if(s.name == "GPS_Time" or s.name == "VIN" or signalList[i] == None):
                    self._data[s.name].append(signalList[i])
                # If it is another signal, append its float value, rounded in
                # consideration of the signals defined round digit
                else:
                    self._data[s.name].append(round(float(signalList[i]), s.roundDigit))
        # If the signals list has the wrong size, raise an error
        else:
            raise ValueError("Error: signalList has to have the same shape as signals.getSignalList()")

    def getLabelData(self, labelName):
        """
        Returns measurement data by a signal name.
        
        First it is necessary to call loadFrimFile.
        """
        
        # If the status is not LOG_FILE_LOADED, raise an error
        if (not self._status == LogStatus.LOG_FILE_LOADED):
            raise ValueError("Not allowed! You have to loadFromFile first")
        # Return the signals data by its name
        return self._data[labelName]

    def getTime(self):
        """ 
        Returns the value list of the signal TIME (not the GPS time).
        """
        return self.getLabelData(signals.getTimeSignal().name)

    def getRelTime(self):
        """
        Returns a list of the relative time in second based on the start time
        for the measurement points.
        """
        
        # Create an empty list and get the value list of TIME
        tList = []
        timebuffer = self.getTime()
        
        # Append the relative time (current time - time of measurement start)
        # to the created list for every value in the value list of TIME
        for i in timebuffer:
            tList.append(round((datetime.strptime(i, "%Y-%m-%d %H:%M:%S.%f") -
                                datetime.strptime(self._data[signals.TIME.name][0], "%Y-%m-%d %H:%M:%S.%f")).total_seconds(), 2))
        # Return the filled list
        return tList

    def getfilename(self):
        """
        Returns the current file name used for the CSV and JSON file.
        """
        return self._filename_raw_data

    def appendFile(self):
        """
        Save the data from the buffer (dictionary) to the CSV file.
        
        First it is necessary to call createLogfile.
        """
        
        # If status is not LOG_CREATED, raise an error
        if(not self._status == LogStatus.LOG_CREATED):
            raise ValueError("You have to create LogFile first!")

        try:
            # Open the CSV file for appending new lines
            with open(path+self._filename_raw_data, 'a', newline='') as file:
                # Create a CSV writer without automatic data convertion
                wr = csv.writer(
                    file, quoting=csv.QUOTE_MINIMAL, quotechar='"')

                # Write the data from the buffer (dictionary) to the CSV file
                for i in range(0, len(self._data["TIME"])):
                    buffer = []
                    # Append one row of measurement to the temporary list
                    for s in signals.getSignalList():
                        buffer.append(self._data[s.name][i])

                    # Write the data row to the CSV file
                    wr.writerow(buffer)
        
        # If any error occured, raise a customized error
        except:
            raise FileNotFoundError("Error!: Appending file failed")

        # Clear the buffer (dictionary)
        self._data.clear()
        # Fill the dictionary with the keys as signals and yet empty lists as values
        for s in signals.getSignalList():
            self._data[s.name] = []

    def loadFromFile(self, filename):
        """
        Load the data from the CSV file to the dictioary of signals. The
        dictionary will contain the signals data of the whole measurement.
        
        Called at the end of a measurement.

        Analysis of height profile
        """
        # Load file to buffer
        try:
            # Create a list for the columns of data. One column matches one signal
            columns = []
            
            # Read CSV
            
            # Open the CSV file for reading
            with open(env.PATH + filename, 'r') as f:
                # Create a CSV reader and read the content of the CSV file
                reader = csv.reader( (line.replace('\0','') for line in f) )
                
                # Execute the following code for every row/line of the CSV file
                for row in reader:
                    # If the list for columns is not empty
                    if columns:
                        # Append the values of the signals to the columns list
                        # for every value in the row
                        for i, value in enumerate(row):
                            # If no value was recorded, append None
                            if(value == ""):
                                columns[i].append(None)
                            # Value recorded: append the value (float or string)
                            else:
                                if(Util.isfloat(value)):
                                    columns[i].append(float(value))
                                else:
                                    columns[i].append(value)
                    # If the columns list is empty, add a list containing the
                    # signals name for every name in the first row. In these
                    # lists, the data for the signals will be appended
                    else:
                        # First row with signal names
                        columns = [[value] for value in row]
                        
            ### Create dictionary
                        
            # Create a dictionary from the columns list with the signal names
            # as keys and the data lists as values
            as_dict = {c[0]: c[1:] for c in columns}
            
            # Get the VIN from the dictionary and set it as attribut
            if("VIN" in as_dict):
                # VIN is only recorded once, other values are None
                vinList = [x for x in as_dict["VIN"] if x is not None]
                # If VIN exists, set as attribut
                if(len(vinList) > 0):
                    self._VIN = vinList[0]
                    
            ### Check if file broken
                    
            # Get all GPS longitude values (that are not None). If there are
            # only None values, the file is broken --> set attribut _isBrokenFile True
            if("GPS_Long" in as_dict):
                gpsL = [x for x in as_dict["GPS_Long"] if x is not None]
                if(len(gpsL) < 1):
                    self._isBrokenFile = True
                    
            # Get all RPM values (that are not None). If there are only None 
            # values, the file is broken --> set attribut _isBrokenFile True
            if("RPM" in as_dict):
                rpm = [x for x in as_dict["RPM"] if int(x) is not 0]
                if(len(rpm) < 1):
                    self._isBrokenFile = True

            ### Data to buffer

            # Set the created dictionary as the buffer (attribut dictionary _data)
            self._data = as_dict
            
        ### Loading failed
        
        # If any error occured, raise a costumized error
        except Exception as e:
            raise FileNotFoundError("Error: Loading File failed!" + str(e))
            
        # Set the file name as attribut and the status to LOG_FILE_LOADED
        self._filename_raw_data = filename

        self._status = LogStatus.LOG_FILE_LOADED

        # adding data analysis
        self.height_profile_dict, self._filename_height_profile = height_profile.build_height_profile(env.PATH + filename, verbose=1)

    def transmitToSQL(self, filename_raw_data, ip, filename_height_profile):
        """
        Connects to SQL server and transmits all data stored in the LogFile 
        object.
            
        """
        ### Connect to server
        
        # Set up a connection to the SQL server (database)
        db = mysql.connector.connect(
            user=env.DB_USER,
            password=env.DB_PASSWORD,
            host=ip,
            database=env.DB_NAME
        )
        
        ### Get & calculate data
        
        # Get the start and end time of the measurement and split them by ";"
        dateTimeStart = self.getStartTime().split(";")
        dateTimeEnd = self.getEndTime().split(";")

        # Extract the date and the time from the start time
        date = dateTimeStart[0]
        starttime = dateTimeStart[1]
        
        # Extract the date and the time from the end time
        endDate = dateTimeEnd[0]
        endtime = dateTimeEnd[1]
        
        # Get the driven distance
        totalKM = self.getDistance()
        # Get the hashed VIN
        VIN = self.getHashedVIN()
        # Get the fuel consuption
        fuelConsumption = self.getFuelConsumption()
        # Get the energy consumption
        energyConsumption = self.getEnergyCons()
        
        # Get the coordinates (latitude and longitude) of the last position
        endLat = [x for x in self._data["GPS_Lat"] if x is not None][-1]
        endLong = [x for x in self._data["GPS_Long"] if x is not None][-1]
        
        ### Commit data to server

        # Create a cursor to interact with the database
        cursor = db.cursor()   
        # Store the data in the database (therefore create the data transfer string)                
        cursor.execute(Stringbuilder.SqlAddEntry(filename_raw_data, filename_height_profile, date, starttime, totalKM, endtime, VIN, fuelConsumption, energyConsumption, endLat, endLong, endDate))
        
        # Commit the execution (necessary so that the data is actually stored)
        db.commit()
        
        ### Disconnect
        
        # Disconnect from the SQL server
        db.close()

    def getAverageData(self, signalStr):
        """
        Returns the average of the values from a given signal by the given
        signal name.
        
        First it is necessary to call loadFromFile.
        """
        
        # If the status is not LOG_FILE_LOADED, raise an error
        if (not self._status == LogStatus.LOG_FILE_LOADED):
            raise ValueError("Not allowed! You have to loadFromFile first")
            
        # If the given signal name is not of a defined signal, raise an error
        if not signals.containsSignalByString(signalStr):
            raise ValueError("Signal is not available!")
        
        # Get the data list of the signal with the given name
        L = self._data[signalStr]
        # Delete the NOne values
        L = [x for x in L if x is not None]
        # Return the mean of the values in the list
        return mean(L)

    def getFuelConsumption(self):
        """
        Calculates and returns the fuel consumption during the drive cycle.
        """
        
        # Get the data from the necessary signals
        speed = self._data["SPEED"]
        maf = self._data["MAF"]
        cer = self._data["COMMANDED_EQUIV_RATIO"]
        
        # Create a list for the values of the fuel consumption over the speed
        # at the measurement point
        fuelCon_normal = []
        #  Append the calculated fuel consumption value to the list
        for i in range(len(speed)):
            # Do not calculate when CER is 0 (dividing through 0)
            if((cer[i]) == 0):
                pass
            else:
                #density fuel : 748
                #Air Fuel ratio : 14.7
                fuelCon_normal.append(((maf[i]* 3600)/(748*14.7*cer[i])))

        # Calculate the average of the lists for the fuel consumption and speed
        avfuelCon = Util.mean(fuelCon_normal)
        avSpeed = Util.mean(speed)

        # Calculate the actual fuel consumption
        avfuelCon = 100*(avfuelCon/avSpeed)

        print("Normal: " + str(avfuelCon))

        return avfuelCon

    def getHashedVIN(self):
        """
        Encrypts (hashes) the vehicle identification number (VIN) to store it
        in db on server --> data security.
        """
        
        # Create a yet empty string for the hashed VIN
        hashed = ""
        
        # If the VIN exists, hash it
        if(not self._VIN == ""):
            hashed = bcrypt.hashpw(self._VIN.encode(), bcrypt.gensalt(10))
            
        # Return the hashed VIN as a utf-8 decoded string
        return hashed.decode("utf-8")
    

    def getEnergyCons(self):
        """
        Calculates and returns the energy consumption during the drive cycle.
        
        Time has to be relative Signal.
        """
        
        # Get the values of the signal TIME (not GPS time)
        time = self.getTime()
        
        # Create a list for the time differences between the measurement points
        diff = []
        
        # Get the necessary signal data (MAF = mass air flow)
        maf = self._data[signals.MAF.name]
        cer = self._data[signals.COMMANDED_EQUIV_RATIO.name] 

        # Efficiency of the engine
        eff = 0.35
        # Calorific value gasoline
        cal = 0.01125
        # Air fuel ratio
        airFuel = 14.7

        # Append the calculated time difference to the list for every time value
        for i in range(1, len(time)):
            diff.append(time[i]- time[i-1])
        # Calculate the mean of the time differences
        dT = Util.mean(diff)
        
        # Create list for the energy values at the measurement points
        energy = []
        # Claculate the energy consumption for each measurement point
        # and append it to the list
        for i in range(len(maf)):
            # Do not divide through 0
            if(cer[i] == 0):
                pass
            else:
                energy.append(eff *cal *dT * maf[i] / (airFuel * cer[i]))
        
        # Return the actual energy consumption (sum it up and divide through
        # the efficiency of the electric engine)
        return (sum(energy)/0.85)

    def getStartTime(self):
        """
        Returns a datetime of the real start of data logging.
        """
        
        # Set the default time
        str = "2000-01-01T00:00:00.000Z000.00"
        
        # Get the last value of the GPS time that is not None
        strlist = [x for x in self._data["GPS_Time"] if x is not None]
        if(len(strlist) >= 1):
            str = strlist[-1]
        #2000-01-01T00:00:00.000Z000.00

        # Split the time value into its date parts
        dateArray  = str.split("T")[0].split("-")
        year = dateArray[0]
        month = dateArray[1]
        day = dateArray[2]

        # Split the time value into its time parts
        time = str.split("T")[1].split("Z")[0].split(":")
        hours = time[0]
        min = time[1]
        sec = time[2]
        
        # If the time value exists in the list of values of the GPS time, get
        # its position and get the time value of the signal TIME at this position
        if(str in self._data["GPS_Time"]):
            ind = self._data["GPS_Time"].index(str)
            timeInd = self._data["TIME"][ind]
        
        # If the time value is not included in the values of the GPS time,
        # Use the default time
        else:
            ind = 0
            timeInd = 0
        
        # Calculate a datetime of the real start of data logging
        d = datetime(year=int(year), month=int(month), day=int(day), hour=int(hours), minute=int(min), second=int(float(sec))) - timedelta(seconds=int(float(timeInd)))
        
        # Return the datetime as a formatted string
        return d.strftime("%m-%d-%Y;%H:%M:%S")

    def getEndTime(self):
        """
        Returns a datetime of the real end of data logging.
        """
        
        #2019-02-23T10:58:31.000Z417.75
        # Set the default time
        str = "2000-01-01T00:00:00.000Z000.00"
        
        # Get the last value of the GPS time that is not None
        strlist = [x for x in self._data["GPS_Time"] if x is not None]
        if(len(strlist) >= 1):
            str = strlist[-1]

        # Split the time value to its date parts
        dateArray  = str.split("T")[0].split("-")
        print(dateArray)
        year = dateArray[0]
        month = dateArray[1]
        day = dateArray[2]

        # Split the time value to its time parts
        time = str.split("T")[1].split("Z")[0].split(":")
        hours = time[0]
        min = time[1]
        sec = time[2]

        # If the time value exists in the GPS time data, get its position and
        # get the value of the signal TIME at this position
        if(str in self._data["GPS_Time"]):
            ind = self._data["GPS_Time"].index(str)
            timeInd = self._data["TIME"][ind]
            timeend = self._data["TIME"][-1]
            
        # If the time value does not exist in the GPS time data
        else:
            timeInd = 0
            timeend = 0
            
        # Calculate the delay betwenn the time values
        timedel = timeend - timeInd

        # Calculate a datetime of the real end of data logging
        d = datetime(year=int(year), month=int(month), day=int(day), hour=int(hours), minute=int(min), second=int(float(sec))) + timedelta(seconds=int(float(timedel)))
        
        # Return the calculated datetime as formatted string
        return d.strftime("%m-%d-%Y;%H:%M:%S")

    def getDistance(self):
        """
        Calculates adn returns the distance travelled in the drive cycle.
        """
        
        #time = self._data[signals.TIME.name][-1]
        
        # Get the values of the signal TIME
        time = self.getTime()
        # Calculate the average speed from the values of the speed signal
        avSpeed = Util.mean(self._data[signals.SPEED.name])
        
        # Calculate the travelled distance
        km = avSpeed*(time[-1]/3600)
        return round(km,2)




                

