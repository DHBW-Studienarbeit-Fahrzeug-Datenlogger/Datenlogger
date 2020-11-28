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
    # print(gps_alt_list)

    # cleaning up data
    zero_handling(gps_alt_list)
    zero_handling(gps_lat_list)
    zero_handling(gps_long_list)

    array_size = len(gps_long_list)

    # calculate Position in km from gps coordinates
    for i in range(array_size):
        # delta 1° long = cos(angle lat) * d_earth * pi / 360
        long_degree_m = 1000 * np.cos(gps_lat_list[i] * np.pi / 180) * 12742 * np.pi / 360

        # delta 1° lat = 111.13 km
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
        # dx = sqrt(delta_lat² + delta_long²)
        # [dx] = m
        dx = np.sqrt(((gps_long_list[i] - gps_long_list[i + 1]) ** 2) + ((gps_lat_list[i] - gps_lat_list[i + 1]) ** 2))

        # [dy] = m
        dy = gps_alt_list[i + 1] - gps_alt_list[i]

        # [gradient] = 1
        gradient = dy / dx
        gradient_array[i] = gradient
        normalized_gradient_array[i] = normalize(value=gradient, maximum=0.2)
        gps_alt_list[i+1] = gps_alt_list[1] + normalized_gradient_array[i] * dx

        angle_deg_array[i] = angle_from_gradient(normalized_gradient_array[i], in_rad=False)
        angle_rad_array[i] = angle_from_gradient(normalized_gradient_array[i], in_rad=True)

    # debug
    print("gradient list", gradient_array)
    print("normalized_gradient_list", normalized_gradient_array)
    print("angle list rad", angle_rad_array)
    print("angle list deg", angle_deg_array)

    # build array with all information (more than necessary)
    height_profile_array = np.array(
        [gps_time_list,
         gps_long_list,
         gps_lat_list,
         gps_alt_list,
         angle_rad_array,
         angle_deg_array,
         normalized_gradient_array]
    )

    # debug
    # print(height_profile_array)

    return height_profile_array


def zero_handling(iterable):
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
                        print("zero handled")
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


def normalize_iterable(iterable, maximum=0.15, keep_original=False, differential_mode=False):
    """
    description:
    takes a iterable object, list or array
    returns a normalized array of equal size
    differences or absolute values are dampened:
    1) near 0: f(x) = y
    2) infinity: f(x) = maximum

    usage:
    1) overwrite your array
        normalize_iterable(iterable=array, maximum=maximum)
    2) keep original array
        normalized_array = normalize_iterable(iterable=array, maximum=maximum, keep_orinal=True)

    :param iterable: list or array
    :type iterable: list or np.ndarray()
    :param maximum: cutoff value
    :type maximum: float
    :param keep_original: overwrite or new array
    :type keep_original: bool
    :param differential_mode: either differences are filtered or absolute values
    :type differential_mode: bool
    :return: filtered array
    :rtype: list or np.ndarray()
    """
    from copy import deepcopy as deepcopy
    # only works with iterables with at least 2 elements
    try:
        iterable[1] = iterable[1]
    except IndexError:
        return iterable
    if keep_original:
        # new array
        temp_iterable = deepcopy(iterable)
    else:
        temp_iterable = iterable

    if differential_mode:
        # second till last are changed, difference is low pass filtered
        for i in range(len(temp_iterable)-1):
            temp_iterable[i+1] = temp_iterable[i] + maximum * np.tanh((temp_iterable[i+1]-temp_iterable[i])/maximum)
    else:
        # every value is filtered
        for i in range(len(temp_iterable)):
            temp_iterable[i] = maximum * np.tanh((temp_iterable[i])/maximum)

    return temp_iterable


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


if __name__ == '__main__':
    # windows debugging path
    path = r"C:\Users\Max\Documents\_5.Semester\Temp\test.csv"

    # pi path
    # path = "/home/pi/Studienarbeit_OBD_Datenlogger/OBD-Logger/"
    height_profile = build_height_profile(path)