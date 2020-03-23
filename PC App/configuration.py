
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

    ButtonBG = "#363636"
    ButtonActiveBG = "#242424"
    ButtonFG = "#EBEBEB"
    ButtonActiveFG = "#EBEBEB"
    ButtonBD = 2
    ButtonRelief = tk.FLAT

    EntryBG = "#363636"
    EntryFG = "#EBEBEB"
    EntryBD = 1
    EntryRelief = tk.FLAT
    EntryWidth = 15

    LabelBG = "#4A4A4A"
    LabelFG = "#EBEBEB"
    LabelBD = 1
    LabelRelief = tk.FLAT
    LabelWidth = 10


class GUI_Queue:

    GUIRequest = {'Connect': 10,
                  'Disconnect': 11,
                  'Start': 12,
                  'Stop': 13,
                  'CubeState': 14}

    CubeState = {'Connected': False,
                 'ReadValues': False,
                 'IP': None,
                 'CurrentFace': None}

    def __init__(self, Queue):
        self.Queue = Queue

    def put_connect(self, ip):
        request = [self.GUIRequest['Connect'], ip]
        self.Queue.put(request)

    def put_disconnect(self):
        self.Queue.put(self.GUIRequest['Disconnect'])

    def put_start(self):
        self.Queue.put(self.GUIRequest['Start'])

    def put_stop(self):
        self.Queue.put(self.GUIRequest['Stop'])





