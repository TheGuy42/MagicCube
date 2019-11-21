
class CubeConfig:
    # server config
    # when ip = "" the current ip is used
    ip = ""
    port = 123
    # Accelerometer Config
    Accel_TiltThreshold = 1.0
    Accel_CalibrationFileName = "Accelerometer_Calibration.pickle"
    Accel_Constant = 9.8

    # Gyro Config
    Gyro_MainThreshold = 2
    Gyro_SecondaryThreshold = 15
    Gyro_CalibrationFileName = "GYRO_Calibration.pickle"
    Gyro_Axis_Change_Delay = 1


class Color:
    DefaultBrightness = 0.8
    # Color definitions
    OFF = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    WHITE = (170, 100, 255)
    ORANGE = (255, 50, 0)
    PINK = (190, 0, 255)
    PURPLE = (90, 20, 255)

    # Presets
    PRST_Default = {'Color': [RED, BLUE, ORANGE, GREEN, WHITE, PURPLE],
                    'Brightness': DefaultBrightness}

    PRST_OFF = {'Color': [OFF, OFF, OFF, OFF, OFF, OFF],
                'Brightness': DefaultBrightness}

    PRST_ON_EDGE = {'Color': [RED, BLUE, ORANGE, GREEN, WHITE, PURPLE],
                    'Brightness': DefaultBrightness}

    PRST_FACE0 = {'Color': [OFF, OFF, OFF, GREEN, OFF, OFF],
                  'Brightness': DefaultBrightness}
    PRST_FACE1 = {'Color': [OFF, BLUE, OFF, OFF, OFF, OFF],
                  'Brightness': DefaultBrightness}
    PRST_FACE2 = {'Color': [RED, OFF, OFF, OFF, OFF, OFF],
                  'Brightness': DefaultBrightness}
    PRST_FACE3 = {'Color': [OFF, OFF, OFF, OFF, WHITE, OFF],
                  'Brightness': DefaultBrightness}
    PRST_FACE4 = {'Color': [OFF, OFF, ORANGE, OFF, OFF, OFF],
                  'Brightness': DefaultBrightness}
    PRST_FACE5 = {'Color': [OFF, OFF, OFF, OFF, OFF, PURPLE],
                  'Brightness': DefaultBrightness}

    Led_Face_List = [PRST_FACE0, PRST_FACE1, PRST_FACE2, PRST_FACE3, PRST_FACE4, PRST_FACE5]
