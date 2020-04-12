#!/usr/bin/env python
"""Released under the MIT License
Copyright 2015, 2016 MrTijn/Tijndagamer
"""
from mpu6050 import mpu6050
from time import sleep
import time
import os
from configuration import CubeConfig
from pickle_interface import Pickler

sensor = mpu6050(0x69)


class Accelerometer:
    def __init__(self):
        self.raw_data = dict()
        self.data = {'CurrentAxis': 0,
                     'x': 0,
                     'y': 0,
                     'z': 0}
        self.Accel_Offset = [{'x': 0, 'y': 0, 'z': 0},
                             {'x': 0, 'y': 0, 'z': 0},
                             {'x': 0, 'y': 0, 'z': 0},
                             {'x': 0, 'y': 0, 'z': 0},
                             {'x': 0, 'y': 0, 'z': 0},
                             {'x': 0, 'y': 0, 'z': 0}]
        self.Accel_Offset_Table = [{'x': -1, 'y': 0, 'z': 0},
                                   {'x': 0, 'y': -1, 'z': 0},
                                   {'x': 0, 'y': 0, 'z': 1},
                                   {'x': 0, 'y': 1, 'z': 0},
                                   {'x': 0, 'y': 0, 'z': -1},
                                   {'x': 1, 'y': 0, 'z': 0}]
        self.load_offset()

    def load_offset(self):
        # try to unpickle offsets
        # if not successful calibrate and pickle
        tmp = Pickler.load(CubeConfig.Accel_CalibrationFileName)
        if tmp is not None:
            self.Accel_Offset = tmp
            #self.get_orientation()
        else:
            self.calibration_procedure()
            Pickler.dump(CubeConfig.Accel_CalibrationFileName, self.Accel_Offset)

    def get_orientation(self, TiltThreshold=CubeConfig.Accel_TiltThreshold, wait_for_axis=True):
        self.data['CurrentAxis'] = None
        while self.data['CurrentAxis'] is None:
            self.get_average_accel(50, offset=False)
            if self.data['x'] < -CubeConfig.Accel_Constant + TiltThreshold:
                self.data['CurrentAxis'] = 0
                return 'x'
            elif self.data['y'] < -CubeConfig.Accel_Constant + TiltThreshold:
                self.data['CurrentAxis'] = 1
                return 'y'
            elif self.data['z'] > CubeConfig.Accel_Constant - TiltThreshold:
                self.data['CurrentAxis'] = 2
                return 'z'
            elif self.data['y'] > CubeConfig.Accel_Constant - TiltThreshold:
                self.data['CurrentAxis'] = 3
                return 'y'
            elif self.data['z'] < -CubeConfig.Accel_Constant + TiltThreshold:
                self.data['CurrentAxis'] = 4
                return 'z'
            elif self.data['x'] > CubeConfig.Accel_Constant - TiltThreshold:
                self.data['CurrentAxis'] = 5
                return 'x'
            elif wait_for_axis is False:
                self.data['CurrentAxis'] = None
                return None

    # get raw values from sensor
    def get_values(self):
        self.raw_data = sensor.get_accel_data()

    # get average acceleration of given reads and their sum
    def _get_average(self, sum, count):
        self.data['x'] = (sum['x'] / count)
        self.data['y'] = (sum['y'] / count)
        self.data['z'] = (sum['z'] / count)

    # apply calibration offset
    def _apply_offset(self):
        self.data['x'] += self.Accel_Offset[self.data['CurrentAxis']]['x']
        self.data['y'] += self.Accel_Offset[self.data['CurrentAxis']]['y']
        self.data['z'] += self.Accel_Offset[self.data['CurrentAxis']]['z']

    # round the data to 2 decimal points
    def round_average(self):
        self.data['x'] = round(self.data['x'], 2)
        self.data['y'] = round(self.data['y'], 2)
        self.data['z'] = round(self.data['z'], 2)

    def calibrate(self, count, axis):
        counter = 1
        Sum = {'x': 0,
               'y': 0,
               'z': 0}
        while counter < count:
            raw_data = sensor.get_accel_data()
            Sum['x'] += raw_data['x']
            Sum['y'] += raw_data['y']
            Sum['z'] += raw_data['z']
            # increase counter
            counter += 1
        # set the offset
        self._get_average(Sum, count)
        # set the offset value for each axis accounting for the earth gravity
        self.Accel_Offset[self.data['CurrentAxis']]['x'] = (self.Accel_Offset_Table[self.data['CurrentAxis']]['x'] * CubeConfig.Accel_Constant) - self.data['x']
        self.Accel_Offset[self.data['CurrentAxis']]['y'] = (self.Accel_Offset_Table[self.data['CurrentAxis']]['y'] * CubeConfig.Accel_Constant) - self.data['y']
        self.Accel_Offset[self.data['CurrentAxis']]['z'] = (self.Accel_Offset_Table[self.data['CurrentAxis']]['z'] * CubeConfig.Accel_Constant) - self.data['z']
        print("Done Calibrating Face: " + str(self.data['CurrentAxis']))

    # calibrate the accelerometer for each face of the cube
    def calibration_procedure(self):
        print("Starting calibration procedure..")
        for Face in range(6):
            self.get_orientation()
            print("please put the cube on Face " + str(Face))
            # wait for the cube to be place on the right face
            while self.data['CurrentAxis'] != Face:
                self.get_orientation()
                #print(self.data)
                sleep(0.1)
            # start the calibration of the face
            if self.data['CurrentAxis'] == Face:
                print("Starting calibration of Face " + str(Face) + " DON'T move the cube")
                sleep(1)
                self.calibrate(1000, Face)
        print(self.Accel_Offset)

    # calculate the average of 'count' reads and store them. (applying offset and rounding the result)
    def get_average_accel(self, count, offset=True):
        Sum = {'x': 0,
               'y': 0,
               'z': 0}

        for each_read in range(count):
            self.get_values()
            Sum['x'] += self.raw_data['x']
            Sum['y'] += self.raw_data['y']
            Sum['z'] += self.raw_data['z']
        self._get_average(Sum, count)
        if offset:
            self._apply_offset()
        self.round_average()


class Gyro:
    def __init__(self):
        # Constants
        self.GYRO_OFFSET = {'x': 0,
                            'y': 0,
                            'z': 0}
        self.raw_data = dict()
        self.data = {'x': 0,
                     'y': 0,
                     'z': 0}
        self.axis_threshold = {'x': 1, 'y': 1, 'z': 1}
        self.other_axis = {'x': ['y', 'z'],
                           'y': ['x', 'z'],
                           'z': ['x', 'y']}
        self.current_axis = None

        self.load_offset()

    def load_offset(self):
        # try to unpickle offsets
        # if not successful calibrate and pickle
        tmp = Pickler.load(CubeConfig.Gyro_CalibrationFileName)
        if tmp is not None:
            self.GYRO_OFFSET = tmp
            self.get_gyro_average(1)
        else:
            self.calibrate(1000)
            Pickler.dump(CubeConfig.Gyro_CalibrationFileName, self.GYRO_OFFSET)

    # get the gyro raw values and apply an offset
    def gyro_offset(self):
        self.raw_data = sensor.get_gyro_data()
        # update values with an offset
        self.raw_data['x'] = (self.raw_data['x'] + self.GYRO_OFFSET['x'])
        self.raw_data['y'] = (self.raw_data['y'] + self.GYRO_OFFSET['y'])
        self.raw_data['z'] = (self.raw_data['z'] + self.GYRO_OFFSET['z'])

    # calculate the average of the gyro values
    def get_average(self, Sum, count):
        self.data['x'] = (Sum['x'] / count)
        self.data['y'] = (Sum['y'] / count)
        self.data['z'] = (Sum['z'] / count)

    # update values according to threshold
    def average_threshold(self):
        if self.axis_threshold['x'] >= self.data['x'] >= -self.axis_threshold['x']:
            self.data['x'] = 0
        if self.axis_threshold['y'] >= self.data['y'] >= -self.axis_threshold['y']:
            self.data['y'] = 0
        if self.axis_threshold['z'] >= self.data['z'] >= -self.axis_threshold['z']:
            self.data['z'] = 0

    # round the average value of the gyro
    def convert_to_int(self):
        self.data['x'] = round(self.data['x'], 2)
        self.data['y'] = round(self.data['y'], 2)
        self.data['z'] = round(self.data['z'], 2)

    # set the threshold value of the main axis lower than the rest
    def set_axis(self, axis_key):
        self.current_axis = axis_key
        if axis_key is not None:
            self.axis_threshold[self.other_axis[axis_key][0]] = CubeConfig.Gyro_SecondaryThreshold
            self.axis_threshold[self.other_axis[axis_key][1]] = CubeConfig.Gyro_SecondaryThreshold
            # reduce the threshold for the main axis
            self.axis_threshold[axis_key] = CubeConfig.Gyro_MainThreshold
        else:
            # if cube is not on an axis then all axis have same threshold
            self.axis_threshold['x'] = CubeConfig.Gyro_MainThreshold
            self.axis_threshold['y'] = CubeConfig.Gyro_MainThreshold
            self.axis_threshold['z'] = CubeConfig.Gyro_MainThreshold

    def changed_axis(self):
        if self.current_axis is None:
            # if cube is not on an axis then it should always check with the accelerometer
            return True
        else:
            if (self.data[self.other_axis[self.current_axis][0]] + self.data[self.other_axis[self.current_axis][1]]) != 0:
                return True
            return False

    # calculate the average offset of each axis for #count of reads
    def calibrate(self, count):
        print("Gyro: Calibrating..")
        counter = 1
        Sum = {'x': 0,
               'y': 0,
               'z': 0}
        while counter < count:
            raw_data = sensor.get_gyro_data()
            Sum['x'] += raw_data['x']
            Sum['y'] += raw_data['y']
            Sum['z'] += raw_data['z']
            # increase counter
            counter += 1
        # set the offset
        self.get_average(Sum, count)
        self.GYRO_OFFSET['x'] = -self.data['x']
        self.GYRO_OFFSET['y'] = -self.data['y']
        self.GYRO_OFFSET['z'] = -self.data['z']
        print("Done Calibrating Gyro")
        sleep(1)

    # get the gyro average of #count reads and apply filters
    def get_gyro_average(self, count):
        Sum = {'x': 0,
               'y': 0,
               'z': 0}

        for each_read in range(count):
            self.gyro_offset()
            Sum['x'] += self.raw_data['x']
            Sum['y'] += self.raw_data['y']
            Sum['z'] += self.raw_data['z']

        self.get_average(Sum, count)
        self.average_threshold()
        self.convert_to_int()

    # get the gyro data after deviding by a factor
    def update_mpu_values(self, accel_obj, factor):
        self.get_gyro_average(10)
        if self.changed_axis():
            sleep(1)
            self.set_axis(accel_obj.get_orientation())
            return 0
        else:
            return int(self.data[self.current_axis] / factor)

