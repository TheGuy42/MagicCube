import Client
from time import sleep
from keyboard import Keyboard
import logging
import configuration
import tk_interface
from sys import exit
from Pickle_Interface import Pickler
import os

import multiprocessing
import queue

logging.basicConfig(level=logging.DEBUG)
logging.info("=======================")


def arrow_key(value, AfterDelay=1.0):
    if value < 0:
        Keyboard.key(Keyboard.VK_RIGHT)
    elif value > 0:
        Keyboard.key(Keyboard.VK_LEFT)
    sleep(AfterDelay)


def change_volume(iterator, threshold, AfterDelay):
    result = iterator(threshold)
    while result is not False:
        result = iterator(threshold)
        if result < 0:
            Keyboard.key(Keyboard.VK_VOLUME_DOWN)
        elif result > 0:
            Keyboard.key(Keyboard.VK_VOLUME_UP)

    sleep(AfterDelay)


def change_song(iterator, threshold, AfterDelay):
    result = iterator(threshold)
    while result is not False:
        result = iterator(threshold)
        if result < 0:
            Keyboard.key(Keyboard.VK_MEDIA_PREV_TRACK)
        elif result > 0:
            Keyboard.key(Keyboard.VK_MEDIA_NEXT_TRACK)
        sleep(AfterDelay)


def change_desktop(iterator, threshold, AfterDelay):
    result = iterator(threshold)
    while result is not False:
        result = iterator(threshold)

        Keyboard.keyDown(Keyboard.VK_CONTROL)
        Keyboard.keyDown(Keyboard.VK_LWIN)
        arrow_key(-result, AfterDelay=0.0)
        Keyboard.keyUp(Keyboard.VK_LWIN)
        Keyboard.keyUp(Keyboard.VK_CONTROL)

    sleep(AfterDelay)


def change_window(iterator, threshold, AfterDelay):
    Keyboard.keyDown(Keyboard.VK_ALT)
    Keyboard.key(Keyboard.VK_TAB)

    result = iterator(threshold)
    while result is not False:
        result = iterator(threshold)
        arrow_key(result, AfterDelay=0.6)

    Keyboard.keyUp(Keyboard.VK_ALT)

    sleep(AfterDelay)


class Configure:
    class AppDefaultSettings:
        def __init__(self):
            self.pi_hostname = "MagicCube"
            self.port = 123
            self.CountBufferLength = 25
            self.GyroValueFactor = 10
            # Dictionary for function settings
            self.AppFunctionDict = {'change volume': {'call': change_volume, 'threshold': 10, 'AfterDelay': 0},
                                    'change song': {'call': change_song, 'threshold': 100, 'AfterDelay': 0.3},
                                    'switch windows': {'call': change_window, 'threshold': 10, 'AfterDelay': 1.0},
                                    'switch desktops': {'call': change_desktop, 'threshold': 110, 'AfterDelay': 1.0}}
            # function key list for corresponding face
            self.Func_Key = ['switch desktops', 'switch windows', None, 'change song', 'change volume', None]

    AppSettingsPath = "AppSettings.pickle"

    def __init__(self, MagicCubeObj):
        self.Cube = MagicCubeObj
        self.AppSettings = self.AppDefaultSettings()
        self.load_app_settings()

    # load the pickled settings
    def load_app_settings(self):
        tmp = Pickler.load(self.AppSettingsPath)
        if tmp is not None:
            self.AppSettings = tmp
        else:
            logging.warning('load config error')
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


class CubeProcess:
    class Cube_Queue:

        GUIRequest = configuration.MultiProcess_config.GUIRequest

        CubeState = {'Connected': False,
                     'ReadValues': False,
                     'IP': None,
                     'CurrentFace': None}

        def __init__(self, Queue):
            self.Queue = Queue
            self.Request = list()

        # fetch a request
        # return True if request fetched
        # return False if Queue is empty
        def get_request(self):
            try:
                self.Request = self.Queue.get_nowait()
                return True
            except queue.Empty:
                return False

    def __init__(self, Queue):
        logging.info("Cube process created")
        self.Cube = MagicCube()
        self.Queue = self.Cube_Queue(Queue)
        self.main()

    # start reading values:
    # send cube request to send values
    def start(self):
        self.Cube.send(self.Cube.Request_Run)
        self.Cube.ReadValues = True

    # stop reading values:
    # send cube request to stop sending values
    def stop(self):
        self.Cube.send(self.Cube.Request_Stop)
        self.Cube.ReadValues = False

    # handle requests sent by GUI
    def handle_request(self):
        if self.Queue.Request[0] == self.Queue.GUIRequest['Connect']:  # if request is to connect
            self.Cube.connect(self.Queue.Request[1])

        elif self.Queue.Request[0] == self.Queue.GUIRequest['Disconnect']:  # if request is to disconnect
            self.Cube.disconnect()

        elif self.Queue.Request[0] == self.Queue.GUIRequest['Start']:  # if request is to start reading values
            self.start()

        elif self.Queue.Request[0] == self.Queue.GUIRequest['Stop']:  # if request is to stop reading values
            self.stop()

        elif self.Queue.Request[0] == self.Queue.GUIRequest['EndProcess']:  # end the Cube process
            if self.Cube.connected:
                if self.Cube.ReadValues:
                    self.stop()
                self.Cube.disconnect()
            self.Queue.Queue.close()
            exit()

    def main(self):
        while True:
            if self.Queue.get_request():
                self.handle_request()
                continue

            if self.Cube.connected:
                if self.Cube.ReadValues:
                    try:
                        self.Cube.main()
                    except EOFError:
                        self.Cube.disconnect()
                        # TODO: send GUI info that cube disconnected
                    except Client.socket.timeout:
                        self.Cube.disconnect()
                        # TODO: send GUI info that cube disconnected


class MagicCube:
    CUBE_FACE_0 = 0
    CUBE_FACE_1 = 1
    CUBE_FACE_2 = 2
    CUBE_FACE_3 = 3
    CUBE_FACE_4 = 4
    CUBE_FACE_5 = 5

    Request_Run = '10'
    Request_Stop = '11'

    def __init__(self):
        # initialize settings Object and apply settings to cube object
        self.Config = Configure(self)
        self.Settings = self.Config.AppSettings
        # initialize a socket
        self.Socket = Client.Client(self.Settings.port)

        self.LastAxis = 0
        self.Data = {'CurrentAxis': 0,
                     'GyroValue': 0}
        self.IP = None
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
        #print(str(self.Data))

    def send(self, value):
        self.Socket.send_tcp(value)

    def connect(self, ip):
        self.Socket.connect(ip)
        self.connected = True

    def disconnect(self):
        if self.ReadValues:
            self.send(self.Request_Stop)
            self.ReadValues = False

        self.Socket.disconnect()
        self.connected = False

    # connect or disconnect according to current state
    def connect_disconnect(self):
        # disconnect
        if self.connected:
            if self.ReadValues:
                self.start_stop()
            self.disconnect()
        # connect
        else:
            if self.IP is not None and self.connected is False:
                self.connect(self.IP)

    # send a request to start or stop sending values according to current state
    def start_stop(self):
        # stop reading values
        if self.ReadValues:
            self.send(self.Request_Stop)
            self.ReadValues = False
        # start reading values
        else:
            self.send(self.Request_Run)
            self.ReadValues = True

    # check if changed axis since last read
    def changed_axis(self):
        if self.LastAxis != self.Data['CurrentAxis']:
            return True
        return False

    # calculate the sum of last 'BufferLength' values
    # if sum is bigger than 'threshold' return the sum of movement including the direction(+/- sign)
    # if changed axis return False
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

    # call the configured function based on the current face
    def call(self, face):
        FuncKey = self.Settings.Func_Key[face]
        if FuncKey is not None:
            FuncDict = self.Settings.AppFunctionDict[FuncKey]
            args = list(FuncDict.values())  # the values of the function to be called(parameters)
            args.pop(0)  # remove the function call object from arg list

            FuncDict['call'](self.count, *args)

    def main(self):

        self.recieve_tcp()
        # call the according function
        self.call(self.Data['CurrentAxis'])


class Graphic_Interface:
    AppPath = os.path.dirname(os.path.realpath(__file__))

    def __init__(self, Queue, exit_protocol):
        self.Queue = Queue
        # initialize and start the main GUI
        self.MainWindow = tk_interface.GUI(exit_protocol=exit_protocol)
        self.main_window()
        # initialize and start the Cube Object
        self.ConfigWindow = None
        self.IP = None

    def main_window(self):
        # Row: 0
        Row = 0
        self.config_icon = self.MainWindow.get_image(self.AppPath + "\settings-icon20.png")
        self.MW_Button_Configure = self.MainWindow.Button(' Configure ', self.config_window, **configuration.GUIConfig.Button)
        self.MW_Button_Configure.configure(image=self.config_icon, background='#4A4A4A',
                                           relief=tk_interface.tk.RAISED, compound='left')
        self.MW_Button_Configure.grid(row=Row, column=0, padx=15, pady=3)

        # Row: 1
        Row += 1
        self.MW_Label_IP = self.MainWindow.Label('IP:', **configuration.GUIConfig.Label)
        self.MW_Label_IP.grid(row=Row, column=0, pady=3)

        self.MW_Entry_IP = self.MainWindow.Entry(**configuration.GUIConfig.Entry)
        self.MW_Entry_IP.bind("<Key-Return>", lambda event: self.connect_disconnect())
        self.MW_Entry_IP.grid(row=Row, column=1, pady=3)

        self.MW_Button_Connect = self.MainWindow.Button('Connect', self.connect_disconnect, **configuration.GUIConfig.Button)
        self.MW_Button_Connect.grid(row=Row, column=2, padx=15, pady=3)

        # Row: 1
        Row += 1
        self.MW_Label_Status_static = self.MainWindow.Label('Status:', **configuration.GUIConfig.Label)
        self.MW_Label_Status_static.grid(row=Row, column=0, pady=3)

        self.MW_Label_Status = self.MainWindow.Label('Disconnected', **configuration.GUIConfig.Label)
        self.MW_Label_Status.grid(row=Row, column=1, pady=3)

        # Row: 2
        Row += 1
        self.MW_Button_Start = self.MainWindow.Button('Start', self.start_stop, **configuration.GUIConfig.Button)
        self.MW_Button_Start.grid(row=Row, column=0, pady=3)

    def config_window(self):
        self.ConfigWindow = tk_interface.GUI(title="MagicCube - Configuration", TopLevel=True)  # TODO: add exit_protocol()


    @staticmethod
    def valid_ip(ip):
        if len(ip) > 15:
            logging.warning('valid_ip(): long ip')
            return False

        try:
            a, b, c, d = ip.split('.')
        except ValueError:
            logging.warning('valid_ip(): split error')
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

    # send request to connect and update local variables
    def connect(self):
        self.get_ip()
        if self.IP is not None and self.Queue.CubeState['Connected'] is False:
            self.Queue.put_connect(self.IP)
            self.MW_Label_Status['text'] = 'Connected'
            self.MW_Button_Connect['text'] = "Disconnect"

    # send request to disconnect and update local variables
    def disconnect(self):
        if self.Queue.CubeState['ReadValues']:
            self.start_stop()
        self.Queue.put_disconnect()
        self.MW_Label_Status['text'] = 'Disconnected'
        self.MW_Button_Connect['text'] = "Connect"

    # connect and disconnect from the cube
    def connect_disconnect(self):
        # Disconnect
        if self.Queue.CubeState['Connected']:
            self.disconnect()
        # Connect
        else:
            self.connect()

    # send request to start reading values from the cube and update local variables
    def start_read_values(self):
        self.Queue.put_start()
        self.MW_Button_Start['text'] = 'Stop'
        # self.MainWindow.master.iconify()

    # send request to stop reading values from the cube and update local variables
    def stop_read_values(self):
        self.Queue.put_stop()
        self.MW_Button_Start['text'] = 'Start'

    def start_stop(self):
        # stop
        if self.Queue.CubeState['ReadValues']:
            self.stop_read_values()
        # start
        else:
            self.start_read_values()


"""
Cube = MagicCube()
# can connect via hostname/ip
Cube.connect(Cube.Settings.pi_hostname)
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


class GUIProcess:
    class GUI_Queue:

        GUIRequest = configuration.MultiProcess_config.GUIRequest

        CubeState = {'Connected': False,
                     'ReadValues': False,
                     'IP': None,
                     'CurrentFace': None}

        def __init__(self):
            self.Queue = multiprocessing.Queue()

        def put_connect(self, ip):
            request = [self.GUIRequest['Connect'], ip]
            self.Queue.put(request)
            self.CubeState['Connected'] = True

        def put_disconnect(self):
            self.Queue.put([self.GUIRequest['Disconnect']])  # request is expected as a list!
            self.CubeState['Connected'] = False

        def put_start(self):
            self.Queue.put([self.GUIRequest['Start']])  # request is expected as a list!
            self.CubeState['ReadValues'] = True

        def put_stop(self):
            self.Queue.put([self.GUIRequest['Stop']])  # request is expected as a list!
            self.CubeState['ReadValues'] = False

        def put_end_process(self):
            self.Queue.put([self.GUIRequest['EndProcess']])  # request is expected as a list!
            self.CubeState['Connected'] = False
            self.CubeState['ReadValues'] = False

    def __init__(self):
        self.Queue = self.GUI_Queue()
        self.GUI = Graphic_Interface(self.Queue, self.exit)
        self.Cube = multiprocessing.Process(target=CubeProcess, args=(self.GUI.Queue.Queue,))

    def start(self):
        self.Cube.start()
        self.GUI.MainWindow.master.mainloop()
        #self.exit()

    def exit(self):
        self.Queue.put_end_process()
        self.Queue.Queue.close()
        self.GUI.MainWindow.destroy()

"""

    def main(self):
        try:
            while True:
                tk.Tk.update_idletasks(self.GUI.MainWindow.master)
                tk.Tk.update(self.GUI.MainWindow.master)
                if self.GUI.Cube is not None:
                    if self.GUI.Cube.connected:
                        if self.GUI.Cube.ReadValues:
                            self.GUI.Run()

        except tk.TclError:
            print()
"""

if __name__ == '__main__':
    GUI = GUIProcess()
    GUI.start()


