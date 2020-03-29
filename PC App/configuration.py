
class AppConfig:
    pi_hostname = "MagicCube"

    Count_BufferLength = 25
    # sensitivity for the count threshold
    Face0_sensitivity = 10
    Face1_sensitivity = 10
    Face2_sensitivity = 110
    Face3_sensitivity = 10
    face4_sensitivity = 110
    Face5_sensitivity = 10

    Face_Sensitivity = [30, 30, 30, 30, 30, 30]

    Face_Func = [None, None, None, None, None, None]


import tkinter as tk


class GUIConfig:

    WindowBG = "#4A4A4A"

    Button = {'background': "#363636",
              'activebackground': "#242424",
              'foreground': "#EBEBEB",
              'activeforeground': "#EBEBEB",
              'border': 1,
              'relief': tk.FLAT}

    Entry = {'background': "#363636",
             'foreground': "#EBEBEB",
             'border': 2,
             'relief': tk.FLAT,
             'width': 15}

    Label = {'background': "#4A4A4A",
             'foreground': "#EBEBEB",
             'border': 1,
             'relief': tk.FLAT,
             'width': 10}


class MultiProcess_config:

    GUIRequest = {'EndProcess': -1,
                  'Connect': 10,
                  'Disconnect': 11,
                  'Start': 12,
                  'Stop': 13,
                  'CubeState': 15}




