import CubeFunctions as func

class CubeDefaultSettings:
    def __init__(self):
        self.pi_hostname = "MagicCube"
        self.port = 4444
        self.Profile = "Profiles\AppSettings.pickle"
        self.CountBufferLength = 25
        self.GyroValueFactor = 10
        # Dictionary for function settings
        self.AppFunctionDict = {'Change volume': {'call': func.change_volume, 'threshold': 500, 'AfterDelay': 0},
                                'Change song': {'call': func.change_song, 'threshold': 2500, 'AfterDelay': 0.3},
                                'Switch windows': {'call': func.change_window, 'threshold': 500, 'AfterDelay': 1.0},
                                'Switch desktops': {'call': func.change_desktop, 'threshold': 2500, 'AfterDelay': 1.0}}
        # function key list for corresponding face
        self.Func_Key = ['Switch desktops', 'Switch windows', None, 'Change song', 'Change volume', None]
        self.Color = self.ColorSettings()

    class ColorSettings:
        # position of led for each face
        Led_pos = [3, 1, 0, 4, 2, 5]
        # Color definitions
        DefaultBrightness = 0.9
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



import tkinter as tk
from tkinter.font import Font

class GUIConfig:
    class Main_Window:
        font = ("", 12)

        WindowBG = "#4A4A4A"

        Frame = {'background': "#4A4A4A",
                 'border': 1,
                 'relief': tk.FLAT}

        Button = {'background': "#363636",
                  'activebackground': "#242424",
                  'foreground': "#EBEBEB",
                  'activeforeground': "#EBEBEB",
                  'border': 1,
                  'relief': tk.RIDGE,
                  'font': font}

        Entry = {'background': "#363636",
                 'foreground': "#EBEBEB",
                 'border': 2,
                 'relief': tk.FLAT,
                 'width': 15,
                 'font': font}

        Label = {'background': "#4A4A4A",
                 'foreground': "#EBEBEB",
                 'border': 1,
                 'relief': tk.FLAT,
                 'width': 10,
                 'font': font}
        Listbox = {'background': "#4A4A4A",
                   'foreground': "#EBEBEB",
                   'selectbackground': "#363636",
                   'border': 1,
                   'relief': tk.SUNKEN,
                   'font': font}

        DropDown = {'background': "#4A4A4A",
                    'foreground': "#EBEBEB",
                    'activebackground': "#363636",
                    'activeforeground': "#EBEBEB",
                    'border': 1,
                    'relief': tk.RIDGE,
                    'font': font}

    class Config_window:
        font = ("", 12)

        WindowBG = "#4A4A4A"

        Frame = {'background': "#4A4A4A",
                 'border': 1,
                 'relief': tk.SUNKEN}

        Button = {'background': "#363636",
                  'activebackground': "#242424",
                  'foreground': "#EBEBEB",
                  'activeforeground': "#EBEBEB",
                  'border': 1,
                  'relief': tk.RIDGE,
                  'font': font}

        Entry = {'background': "#363636",
                 'foreground': "#EBEBEB",
                 'border': 2,
                 'relief': tk.FLAT,
                 'width': 15,
                 'font': font}

        Label = {'background': "#4A4A4A",
                 'foreground': "#EBEBEB",
                 'border': 1,
                 'relief': tk.FLAT,
                 'width': 10,
                 'font': font}

        Listbox = {'background': "#4A4A4A",
                   'foreground': "#EBEBEB",
                   'selectbackground': "#363636",
                   'border': 1,
                   'relief': tk.SUNKEN,
                   'font': font}

        DropDown = {'background': "#4A4A4A",
                    'foreground': "#EBEBEB",
                    'activebackground': "#363636",
                    'activeforeground': "#EBEBEB",
                    'border': 1,
                    'relief': tk.RIDGE,
                    'font': font}


class MultiProcess_config:

    GUIRequest = {'EndProcess': -1,
                  'Connect': 10,
                  'Disconnect': 11,
                  'Start': 12,
                  'Stop': 13,
                  'CubeState': 15,
                  'UpdateSettings': 40}

    # Response has all values of GUIRequest on top of it's own
    Response = {'Failed': False}
    Response.update(GUIRequest)


