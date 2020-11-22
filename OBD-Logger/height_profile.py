"""
Created by: Maximilian Vogt
Version: 1.0

Description:
    take .csv file
    extract necessary information and reformat (GPS_long, GPS_lat, GPS_alt, GPS_time)
    calculate gradient, angle(rad), angle(degree)
    save everything in np array
"""

import numpy as np
import csv


def build_height_profile(path="/home/pi/Studienarbeit_OBD_Datenlogger/OBD-Logger/"):
    """
    :param path: direct path to .csv file
    :type path: str
    :return: array with all information
    :rtype: np.ndarray()

    take .csv file
    extract necessary information and reformat (GPS_long, GPS_lat, GPS_alt, GPS_time)
    calculate gradient, angle(rad), angle(degree)
    save everything in np array
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
                print(row)
                first_row = False
                continue

            # converting format and inserting in lists
            # 0 handling can be added here
            print(row)
            try:
                gps_alt_list.append(float(row[6]))
            except ValueError:
                gps_alt_list.append(0.0)
            try:
                gps_lat_list.append(float(row[5]))
            except ValueError:
                gps_lat_list.append(0.0)
            try:
                gps_long_list.append(float(row[4]))
            except ValueError:
                gps_long_list.append(0.0)
            try:
                gps_time_list.append(float(row[7]))
            except ValueError:
                gps_time_list.append(0.0)

    # debug
    print(gps_alt_list)

    # empty lists about to be filled
    angle_rad_list = []
    angle_deg_list = []
    gradient_list = []

    # calculating angle and degree from GPS data
    for i in range(len(gps_time_list) - 1):
        # linear interpolation. given values for 45° (78.58km) and 50° (71.44km)
        lat_degree_km = 71.44 + (50.0 - gps_lat_list[i]) * (78.58 - 71.44) / (50.0 - 45.0)
        print("lat degree conversion factor", lat_degree_km)

        # 111.13 km = 1° long
        long_degree_km = 111.13

        # [dx] = m
        dx = 1000 * np.sqrt((((gps_long_list[i] - gps_long_list[i + 1]) * long_degree_km) ** 2) +
                            (((gps_lat_list[i]) - gps_lat_list[i + 1]) * lat_degree_km) ** 2)

        # [dy] = m
        dy = gps_alt_list[i + 1] - gps_alt_list[i]

        # gradient no dimension (m/m)
        gradient = dy / dx
        gradient_list.append(gradient)

        # angle in rad
        angle = np.arctan(gradient)
        angle_rad_list.append(angle)

        # angle in degree
        angle_deg_list.append(angle * 180 / np.pi)

    # add empty element to match list size
    angle_deg_list.append(0.0)
    angle_rad_list.append(0.0)
    gradient_list.append(0.0)

    # debug
    print("angle list rad", angle_rad_list)
    print("angle list deg", angle_deg_list)
    print("gradient list", gradient_list)

    # build array with all information (more than necessary)
    height_profile_array = np.array(
        [gps_time_list, gps_long_list, gps_lat_list, gps_alt_list, angle_rad_list, angle_deg_list, gradient_list])

    # debug
    print(height_profile_array)

    return height_profile_array


if __name__ == '__main__':
    # windows debugging path
    path = r"C:\Users\Max\Documents\_5.Semester\Temp\test.csv"

    # pi path
    # path = "/home/pi/Studienarbeit_OBD_Datenlogger/OBD-Logger/"
    height_profile = build_height_profile()