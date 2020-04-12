
class CubeConfig:
    # server config
    # when ip = "" the current ip is used
    ip = ""
    port = 4444
    # Accelerometer Config
    Accel_TiltThreshold = 1.0
    Accel_CalibrationFileName = "Accelerometer_Calibration.pickle"
    Accel_Constant = 9.8

    # Gyro Config
    Gyro_MainThreshold = 2
    Gyro_SecondaryThreshold = 15
    Gyro_CalibrationFileName = "GYRO_Calibration.pickle"
    Gyro_Axis_Change_Delay = 1

class CubeDefaultSettings:
    class ColorSettings:
        # position of led for each face
        Led_pos = [3, 1, 0, 4, 2, 5]
        # Color definitions
        DefaultBrightness = 0.8
        OFF = (0, 0, 0)
        RED = (255, 0, 0)
        GREEN = (0, 255, 0)
        BLUE = (0, 0, 255)
        WHITE = (170, 100, 255)
        ORANGE = (255, 50, 0)
        PINK = (190, 0, 255)
        PURPLE = (90, 20, 255)

        def __init__(self):
            # Presets
            self.PRST_OFF = {'Color': [self.OFF, self.OFF, self.OFF, self.OFF, self.OFF, self.OFF],
                             'Brightness': self.DefaultBrightness}

            self.PRST_FACE0 = {'Color': [self.OFF, self.OFF, self.OFF, self.GREEN, self.OFF, self.OFF],
                               'Brightness': self.DefaultBrightness}
            self.PRST_FACE1 = {'Color': [self.OFF, self.BLUE, self.OFF, self.OFF, self.OFF, self.OFF],
                               'Brightness': self.DefaultBrightness}
            self.PRST_FACE2 = {'Color': [self.RED, self.OFF, self.OFF, self.OFF, self.OFF, self.OFF],
                               'Brightness': self.DefaultBrightness}
            self.PRST_FACE3 = {'Color': [self.OFF, self.OFF, self.OFF, self.OFF, self.WHITE, self.OFF],
                               'Brightness': self.DefaultBrightness}
            self.PRST_FACE4 = {'Color': [self.OFF, self.OFF, self.ORANGE, self.OFF, self.OFF, self.OFF],
                               'Brightness': self.DefaultBrightness}
            self.PRST_FACE5 = {'Color': [self.OFF, self.OFF, self.OFF, self.OFF, self.OFF, self.PURPLE],
                               'Brightness': self.DefaultBrightness}

            self.Face_List = [self.PRST_FACE0, self.PRST_FACE1, self.PRST_FACE2,
                              self.PRST_FACE3, self.PRST_FACE4, self.PRST_FACE5]

            self.PRST_ON_EDGE = {'Color': [self.Face_List[0]['Color'][self.Led_pos[0]],
                                           self.Face_List[1]['Color'][self.Led_pos[1]],
                                           self.Face_List[2]['Color'][self.Led_pos[2]],
                                           self.Face_List[3]['Color'][self.Led_pos[3]],
                                           self.Face_List[4]['Color'][self.Led_pos[4]],
                                           self.Face_List[5]['Color'][self.Led_pos[5]]],
                                 'Brightness': self.DefaultBrightness}
