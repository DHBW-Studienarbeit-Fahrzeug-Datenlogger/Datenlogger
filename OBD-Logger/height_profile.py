"""
Created by: Maximilian Vogt
Version: 1.0

Description:
    take .csv file
    extract necessary information and reformat (GPS_long, GPS_lat, GPS_alt, GPS_time)
    calculate normalized gradient
    maximum gradient is set to counteract gps inaccuracy leading to high values in stationary state,
    calculate angle(rad), angle(degree)

    save everything in json file
    return dict and json file path

"""

import numpy as np
import csv
import json


def build_height_profile(path="/home/pi/Studienarbeit_OBD_Datenlogger/OBD-Logger/", verbose=0):
    """
    :param path: direct path to .csv file
    :type path: str
    :return: dictionary with all information, filename of json file
    :rtype: dict, str

    take .csv file
    extract necessary information and reformat (GPS_long, GPS_lat, GPS_alt, GPS_time)
    Format:
    0: TIME
    1: SPEED
    2: RPM
    3:ENGINE_LOAD
    4: MAF
    5: AMBIANT_AIR_TEMP
    6: RELATIVE_ACCEL_POS
    7: COMMANDED_EQUIV_RATIO
    8: FUEL_LEVEL
    9: GPS_Long
    10: GPS_Lat
    11: GPS_Alt
    12: GPS_Time
    13: INTERNAL_AIR_TEMP
    14: VIN

    calculate normalized gradient
    maximum gradient is set to counteract gps inaccuracy leading to high values in stationary state,
    calculate angle(rad), angle(degree)

    save everything in json file
    return dict and json file path
    """

    # empty list about to be filled
    gps_alt_list = []
    gps_lat_list = []
    gps_long_list = []
    gps_time_list = []

    # open csv file
    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')

        # skip first row in calculations
        first_row = True

        for row in reader:
            if first_row:
                # check format of .csv file
                # default values
                gps_long_index = 9
                gps_lat_index = 10
                gps_alt_index = 11
                gps_time_index = 12

                # find index for necessary values in csv file
                try:
                    gps_long_index = find_index(row, "GPS_Long")
                    print_debug(("gps_long_index :", gps_long_index), verbose=verbose)
                    gps_lat_index = find_index(row, "GPS_Lat")
                    print_debug(("gps_lat_index :", gps_lat_index), verbose=verbose)
                    gps_alt_index = find_index(row, "GPS_Alt")
                    print_debug(("gps_alt_index: ", gps_alt_index), verbose=verbose)
                    gps_time_index = find_index(row, "GPS_Time")
                    print_debug(("gps time index: ", gps_time_index), verbose=verbose)
                except FileFormatInvalid as e:
                    print(e.message)
                    return None, None

                # debug
                print_debug(row, verbose)

                first_row = False
                continue

            # converting format and inserting in lists
            # unreadable data will be temporarily set to 0.0
            print_debug(row, verbose=verbose)
            try:
                gps_alt_list.append(float(row[gps_alt_index]))
            except ValueError:
                gps_alt_list.append(0.0)
            try:
                gps_lat_list.append(float(row[gps_lat_index]))
            except ValueError:
                gps_lat_list.append(0.0)
            try:
                gps_long_list.append(float(row[gps_long_index]))
            except ValueError:
                gps_long_list.append(0.0)
            try:
                gps_time_list.append(float(row[gps_time_index]))
            except ValueError:
                gps_time_list.append(0.0)

    # debug
    print_debug(gps_alt_list, verbose=verbose)

    # cleaning up data
    # linear interpolation of 0 values
    zero_handling(gps_alt_list)
    zero_handling(gps_lat_list)
    zero_handling(gps_long_list)

    array_size = len(gps_long_list)

    # calculate Position in km from gps coordinates
    for i in range(array_size):
        # delta 1 degree long = cos(angle lat) * d_earth * pi / 360
        long_degree_m = 1000 * np.cos(gps_lat_list[i] * np.pi / 180) * 12742 * np.pi / 360

        # delta 1 degree lat = 111.13 km
        lat_degree_m = 111130

        gps_long_list[i] = gps_long_list[i] * long_degree_m
        gps_lat_list[i] = gps_lat_list[i] * lat_degree_m

    # empty lists about to be filled
    angle_rad_array = np.zeros(array_size)
    angle_deg_array = np.zeros(array_size)
    gradient_array = np.zeros(array_size)
    normalized_gradient_array = np.zeros(array_size)

    # calculating gradient from GPS data
    for i in range(array_size - 1):
        # dx = sqrt(delta_lat^2 + delta_long^2)
        # [dx] = m
        dx = np.sqrt(((gps_long_list[i] - gps_long_list[i + 1]) ** 2) + ((gps_lat_list[i] - gps_lat_list[i + 1]) ** 2))

        # [dy] = m
        dy = gps_alt_list[i + 1] - gps_alt_list[i]

        # [gradient] = 1
        # prevent div 0 errors
        if dx <= 0:
            gradient = 0
        else:
            gradient = dy / dx
            
        gradient_array[i] = gradient
        normalized_gradient_array[i] = normalize(value=gradient, maximum=0.2)
        gps_alt_list[i+1] = gps_alt_list[i] + normalized_gradient_array[i] * dx

        angle_deg_array[i] = angle_from_gradient(normalized_gradient_array[i], in_rad=False)
        angle_rad_array[i] = angle_from_gradient(normalized_gradient_array[i], in_rad=True)

    # debug
    print_debug(("gradient list", gradient_array), verbose=verbose)
    print_debug(("normalized_gradient_list", normalized_gradient_array), verbose=verbose)
    print_debug(("angle list rad", angle_rad_array), verbose=verbose)
    print_debug(("angle list deg", angle_deg_array), verbose=verbose)

    # build array with all information (more than necessary)
    height_profile_dict = {
        "time": gps_time_list,
        "gps_long": gps_long_list,
        "gps_lat": gps_lat_list,
        "gps_alt": gps_alt_list,
        "angle_rad": angle_rad_array.tolist(),
        "angle_deg": angle_deg_array.tolist(),
        "gradient": normalized_gradient_array.tolist()
    }

    # write information to json file
    json_filename = path[:-4]+"_height_profile.json"
    json.dump(height_profile_dict, open(json_filename, "w"), indent=4)

    # debug
    print_debug(height_profile_dict, verbose=verbose)

    return height_profile_dict, json_filename


def zero_handling(iterable, verbose=0):
    # if first element = 0
    if iterable[0] == 0.0:
        count_up = 0
        while True:
            count_up += 1
            if iterable[count_up] != 0.0:
                iterable[0] = iterable[count_up]
                break

    # every other element
    for i in range(len(iterable) - 1):
        if iterable[i + 1] == 0.0:
            count_up = 0
            while True:
                count_up += 1
                try:
                    if iterable[i + 1 + count_up] != 0.0:
                        iterable[i + 1] = (iterable[i+1+count_up] * count_up + iterable[i]) / (count_up + 1)
                        print_debug("zero handled", verbose=verbose)
                        break
                except IndexError:
                    iterable[i+1] = iterable[i]
                    break


def normalize(value, maximum=0.15):
    """
    description:
    returns a normalized value

    :param value:
    :param maximum: cutoff value
    :type maximum: float
    :return: filtered array
    :rtype: list or np.ndarray()
    """

    return maximum * np.tanh(value/maximum)


def angle_from_gradient(gradient, in_rad=True):
    """
    calculates angle from gradient
    :param gradient: gradient
    :type gradient: float
    :param in_rad: rad or degree
    :type in_rad: bool
    :return: angle
    :rtype: float
    """
    # return in rad
    if in_rad:
        return np.arctan(gradient)
    # return in degree
    else:
        return np.arctan(gradient)*180 / np.pi


def find_index(row, string):
    """
    returns the index of the matching element in a list
    """
    i = 0
    for element in row:
        if element == string:
            return i
        else:
            i = i+1
    raise FileFormatInvalid(path, "{} was not found in file {}. check csv file!".format(string, path))


class FileFormatInvalid(Exception):
    """
    Exception to express an invalid FileFormat
    """
    def __init__(self, filename, message):
        Exception.__init__(self)
        self.filename = filename
        self.message = message


def print_debug(to_print, verbose=1):
    """
    enable, disable prints based on verbose value
    """
    if verbose > 0:
        print(to_print)


if __name__ == '__main__':
    # windows debugging path
    path = r"C:\Users\Max\Documents\_5.Semester\Studienarbeit\test.csv"

    # pi path
    # path = "/home/pi/Studienarbeit_OBD_Datenlogger/OBD-Logger/"
    height_profile = build_height_profile(path, verbose=0)
