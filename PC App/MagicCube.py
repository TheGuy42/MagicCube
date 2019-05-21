import Client
from time import sleep
from keyboard import Keyboard
import logging
from configuration import AppConfig
import tk_interface
import tkinter as tk
from tkinter import messagebox
from Pickle_Interface import Pickler


logging.basicConfig(level=logging.INFO)
logging.info("=======================")


def change_volume(value):
    if value < 0:
        Keyboard.key(Keyboard.VK_VOLUME_DOWN)
    elif value > 0:
        Keyboard.key(Keyboard.VK_VOLUME_UP)


def change_song(value, AfterDelay=0.3):
    if value < 0:
        Keyboard.key(Keyboard.VK_MEDIA_PREV_TRACK)
    elif value > 0:
        Keyboard.key(Keyboard.VK_MEDIA_NEXT_TRACK)
    sleep(AfterDelay)


def arrow_key(value, AfterDelay=1.0):
    if value < 0:
        Keyboard.key(Keyboard.VK_RIGHT)
    elif value > 0:
        Keyboard.key(Keyboard.VK_LEFT)
    sleep(AfterDelay)


def change_desktop(value, AfterDelay=1.0):
    Keyboard.keyDown(Keyboard.VK_CONTROL)
    Keyboard.keyDown(Keyboard.VK_LWIN)
    arrow_key(-value, AfterDelay=0.0)
    Keyboard.keyUp(Keyboard.VK_LWIN)
    Keyboard.keyUp(Keyboard.VK_CONTROL)

    sleep(AfterDelay)


class Configure:

    class AppDefaultSettings:
        def __init__(self, MagicCubeObj):
            self.CountBufferLength = 25
            self.GyroValueFactor = 10
            # Dictionary for function settings
            self.AppFunctionDict = {'change volume': {'call': MagicCubeObj.Change_Volume, 'threshold': 10},
                                    'change song': {'call': MagicCubeObj.Change_Song, 'threshold': 110},
                                    'switch windows': {'call': MagicCubeObj.Switch_Windows, 'threshold': 10},
                                    'switch desktops': {'call': MagicCubeObj.Switch_Desktop, 'threshold': 110}}
            # function key list for corresponding face
            self.Func_Key = ['change song', 'change volume', 'change song', 'switch windows', 'switch desktops', None]

    AppSettingsPath = "AppSettings.pickle"

    def __init__(self, MagicCubeObj):
        self.Cube = MagicCubeObj
        self.AppSettings = self.AppDefaultSettings(self.Cube)
        self.load_app_settings()

    # load the pickled settings
    def load_app_settings(self):
        tmp = Pickler.load(self.AppSettingsPath)
        if tmp is not None:
            self.AppSettings = tmp
        else:
            print('load config error')
            #messagebox.showwarning('Configuration', 'No configuration file found!\nload_app_settings()')

    # save settings to a pickle file
    def save(self, path):
        Pickler.dump(path, self.AppSettings)

    # set a function to specific face, given the dictionary key for the function
    def set_face_func(self, face, FuncDictKey):
        self.AppSettings.Func_Key[face] = FuncDictKey

    def set_func_threshold(self, funcKey, threshold):
        self.AppSettings.AppFunctionDict[funcKey]['threshold'] = threshold

    # return a list of all function keys
    def get_AppFunctionDict_keys(self):
        return self.AppSettings.AppFunctionDict.keys()

    # revert changes to AppSettings by getting the last updated version from Cube object
    def cancel_app_changes(self):
        self.AppSettings = self.Cube.Settings

    # apply the app settings changes to the cube object
    def apply_app_settings(self):
        self.Cube.Settings = self.AppSettings


class MagicCube:
    CUBE_FACE_0 = 0
    CUBE_FACE_1 = 1
    CUBE_FACE_2 = 2
    CUBE_FACE_3 = 3
    CUBE_FACE_4 = 4
    CUBE_FACE_5 = 5

    Request_Run = '10'
    Request_Stop = '11'

    def __init__(self, port):
        # initialize settings Object and apply settings to cube object
        self.Config = Configure(self)
        self.Settings = self.Config.AppSettings
        # initialize a socket
        self.Socket = Client.Client(port)

        self.LastAxis = 0
        self.Data = {'CurrentAxis': 0,
                     'GyroValue': 0}
        self.connected = False
        self.ReadValues = False

    # update the last axis variable and read new data
    # TODO: check if no factor is viable
    def recieve_tcp(self, factor=10):
        self.LastAxis = self.Data['CurrentAxis']
        self.Data = self.Socket.recieve_tcp(1024)

        if self.Data is False:
            self.Data = {'CurrentAxis': self.LastAxis,
                         'GyroValue': 0}
        else:
            self.Data['GyroValue'] = int(self.Data['GyroValue'] / factor)
        logging.info(str(self.Data))

    def send(self, value):
        self.Socket.send_tcp(value)

    def connect(self, ip):
        self.Socket.connect(ip)
        self.connected = True

    def disconnect(self):
        self.Socket.disconnect()
        self.ReadValues = False
        self.connected = False

    # check if changed axis since last read
    def changed_axis(self):
        if self.LastAxis != self.Data['CurrentAxis']:
            return True
        return False

    # calculate the sum of last 'BufferLength' values
    # if sum is bigger than 'threshold' return true
    def count(self, threshold):
        BufferLength = self.Settings.CountBufferLength
        buffer = [0] * BufferLength
        index = 0
        sumOfMovement = 0

        while -threshold < sumOfMovement < threshold:
            self.recieve_tcp()

            buffer[index] = self.Data['GyroValue']
            # check if changed orientation
            if self.changed_axis():
                return False
            # calculate sumOfMovement
            sumOfMovement += buffer[index] - buffer[(index + 1) % BufferLength]
            logging.debug("sumOfMovement = " + str(sumOfMovement))
            index += 1
            index = index % BufferLength
        return sumOfMovement

    # change volumed
    def Change_Volume(self, threshold=AppConfig.Face1_sensitivity):
        result = self.count(threshold)

        while result is not False:
            result = self.count(threshold)
            change_volume(result)

    # change songs
    def Change_Song(self, threshold=AppConfig.Face2_sensitivity):
        result = self.count(threshold)
        while result is not False:
            result = self.count(threshold)
            change_song(result, AfterDelay=0.2)

    # switch between windows
    def Switch_Windows(self, threshold=AppConfig.Face3_sensitivity):
        Keyboard.keyDown(Keyboard.VK_ALT)
        Keyboard.key(Keyboard.VK_TAB)

        result = self.count(threshold)
        while result is not False:
            result = self.count(threshold)
            arrow_key(result, AfterDelay=0.6)

        Keyboard.keyUp(Keyboard.VK_ALT)

    # Change Desktops
    def Switch_Desktop(self, threshold=AppConfig.face4_sensitivity):

        result = self.count(threshold)
        while result is not False:
            result = self.count(threshold)
            change_desktop(result)

    def call(self, face):
        FuncKey = self.Settings.Func_Key[face]
        if FuncKey is not None:
            FuncDict = self.Settings.AppFunctionDict[FuncKey]
            FuncDict['call'](threshold=FuncDict['threshold'])

    def main(self):

        self.recieve_tcp()

        # call the according function
        self.call(self.Data['CurrentAxis'])


class Graphic_Interface:
    port = 123

    def __init__(self):
        # initialize and start the main GUI
        self.MainWindow = tk_interface.GUI()
        self.main_window()
        # initialize and start the Cube Object
        self.Cube = MagicCube(self.port)
        self.ConfigWindow = None
        self.IP = None

    def main_window(self):
        self.MW_Label_IP = self.MainWindow.Lable('IP:')
        self.MW_Label_IP.grid(row=0, column=0, pady=3)

        self.MW_Entry_IP = self.MainWindow.Entry()
        self.MW_Entry_IP.grid(row=0, column=1, pady=3)

        self.MW_Button_Connect = self.MainWindow.Button('Connect', self.connect_disconnect)
        self.MW_Button_Connect.grid(row=0, column=2, padx=15, pady=3)

        self.MW_Label_Status_static = self.MainWindow.Lable('Status:')
        self.MW_Label_Status_static.grid(row=1, column=0, pady=3)

        self.MW_Label_Status = self.MainWindow.Lable('Disconnected')
        self.MW_Label_Status.grid(row=1, column=1, pady=3)

        self.MW_Button_Start = self.MainWindow.Button('Strat', self.start_stop)
        self.MW_Button_Start.grid(row=2, column=0, pady=3)

    def config_window(self):
        self.ConfigWindow = tk_interface.GUI(title='Configuration')

    @staticmethod
    def valid_ip(ip):
        if len(ip) > 15:
            print('long ip')
            return False

        try:
            a, b, c, d = ip.split('.')
        except ValueError:
            print('split error')
            return False

        if 0 <= int(a) < 255 and 0 <= int(b) < 255 and 0 <= int(c) < 255 and 0 <= int(d) < 255:
            return True

    # get the ip in entry and if it's valid save it
    def get_ip(self):
        ip = self.MW_Entry_IP.get()
        if self.valid_ip(ip):
            self.IP = ip
        else:
            self.IP = None

    # connect and disconnect from the cube
    def connect_disconnect(self):
        if self.Cube.connected:
            if self.Cube.ReadValues:
                self.start_stop()
            self.Cube.disconnect()
            self.MW_Label_Status['text'] = 'Disconnected'
            self.MW_Button_Connect['text'] = "Connect"
        else:
            self.get_ip()
            if self.IP is not None and self.Cube.connected is False:
                self.Cube.connect(self.IP)
                self.MW_Label_Status['text'] = 'Connected'
                self.MW_Button_Connect['text'] = "Disconnect"

    def start_stop(self):
        # stop
        if self.Cube.ReadValues:
            self.Cube.send(self.Cube.Request_Stop)
            self.Cube.ReadValues = False
            self.MW_Button_Start['text'] = 'Start'
        #start
        else:
            self.Cube.send(self.Cube.Request_Run)
            self.Cube.ReadValues = True
            self.MW_Button_Start['text'] = 'Stop'
            self.MainWindow.master.iconify()

    def Run(self):
        try:
            self.Cube.main()
        except EOFError:
            self.connect_disconnect()
            self.MW_Button_Start['text'] = 'Start'
        except Client.socket.timeout:
            self.connect_disconnect()
            self.MW_Button_Start['text'] = 'Start'


Cube = MagicCube(1234)

Cube.connect('10.0.0.30')
Cube.send(Cube.Request_Run)
Cube.ReadValues = True

while True:
    try:
        Cube.main()
    except EOFError:
        print("EOF ERROR")
    except Client.socket.timeout:
        print("TimeOut ERROR")

# GUI
"""

app = Graphic_Interface()

try:
    while True:
        tk.Tk.update_idletasks(app.MainWindow.master)
        tk.Tk.update(app.MainWindow.master)
        if app.Cube is not None:
            if app.Cube.connected:
                if app.Cube.ReadValues:

                    app.Run()

except tk.TclError:
    print()

"""
