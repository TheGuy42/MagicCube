#import Client
import multiprocessing
import queue
from sys import exit
from time import sleep
import logging
logger = logging.getLogger("Logger")
logging.basicConfig(level=logging.WARNING, format="%(levelname)s:%(processName)s.%(funcName)s()-> %(message)s")

import configuration
import tk_interface
from Pickle_Interface import Pickler
import Client1 as Client
import os
import time


class Configure:

    AppSettingsPath = "Profiles\AppSettings.pickle"

    def __init__(self):
        self.Settings = configuration.CubeDefaultSettings()
        self.load_app_settings()

    # load the pickled settings
    def load_app_settings(self):
        tmp = Pickler.load(self.AppSettingsPath)
        if tmp is not None:
            self.Settings = tmp
            return True
        else:
            logging.warning('No configuration file found')
            return False

    # save settings to a pickle file
    def save(self, path):
        Pickler.dump(path, self.Settings)

    # return the pi hostname
    def get_hostname(self):
        return self.Settings.pi_hostname

    # set the pi hostname
    def set_hostname(self, hostname):
        self.Settings.pi_hostname = hostname

    # return the application port
    def get_port(self):
        return self.Settings.port

    # set the application port
    def set_port(self, port):
        self.Settings.port = int(port)

    # set a function to specific face, given the dictionary key for the function
    def set_face_func(self, face, FuncDictKey):
        self.Settings.Func_Key[face] = FuncDictKey

    def get_face_func(self, face):
        return self.Settings.Func_Key[face]

    def set_func_threshold(self, funcKey, threshold):
        self.Settings.AppFunctionDict[funcKey]['threshold'] = threshold

    # return a list of all function keys
    def get_AppFunctionDict_keys(self):
        return list(self.Settings.AppFunctionDict.keys())

    # return the color of face
    def get_face_color(self, face, hex=False):
        if hex:
            return self.rgb_to_hex(self.Settings.Color.Face_List[face]['Color'][self.Settings.Color.Led_pos[face]])
        else:
            return self.Settings.Color.Face_List[face]['Color'][self.Settings.Color.Led_pos[face]]

    # set face color(also updating on edge color)
    def set_face_color(self, face, color):
        self.Settings.Color.Face_List[face]['Color'][self.Settings.Color.Led_pos[face]] = color
        self.Settings.Color.PRST_ON_EDGE['Color'][face] = color

    @staticmethod
    def rgb_to_hex(rgb):
        return '#%02x%02x%02x'%rgb

    @staticmethod
    def hex_to_rgb(hex):
        return tuple(int(hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

    # apply the app settings changes to the cube object
    def get_app_settings(self):
        return self.Settings


class CubeProcess:
    class Cube_Queue:

        GUIRequest = configuration.MultiProcess_config.GUIRequest
        Response = configuration.MultiProcess_config.Response

        CubeState = {'Connected': False,
                     'ReadValues': False,
                     'IP': None,
                     'CurrentFace': None}

        def __init__(self, Queue, ResponseQ):
            self.Queue = Queue
            self.ResponseQ = ResponseQ
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

        def request_arrived(self):
            if self.Queue.empty():
                return False
            return True

        def put_response(self, response):
            self.ResponseQ.put(response)

    def __init__(self, Queue, ResponseQ):
        logging.info("============Cube process started============")
        self.Queue = self.Cube_Queue(Queue, ResponseQ)
        self.Cube = MagicCube(self.Queue.request_arrived)
        self.main()

    # handle requests sent by GUI
    def handle_request(self):
        logging.debug(f"Request: {self.Queue.Request}")
        if self.Queue.Request[0] == self.Queue.GUIRequest['Connect']:  # if request is to connect
            if self.Cube.connect(self.Queue.Request[1]): # connect request is list[request, ip]
                self.Queue.put_response(self.Queue.Response['Connect'])
            else:
                self.Queue.put_response(self.Queue.Response['Failed'])

        elif self.Queue.Request[0] == self.Queue.GUIRequest['Disconnect']:  # if request is to disconnect
            self.Cube.disconnect()
            self.Queue.put_response(self.Queue.Response['Disconnect'])

        elif self.Queue.Request[0] == self.Queue.GUIRequest['Start']:  # if request is to start reading values
            if self.Cube.start():
                self.Queue.put_response(self.Queue.Response['Start'])
            else:
                self.Queue.put_response(self.Queue.Response['Failed'])

        elif self.Queue.Request[0] == self.Queue.GUIRequest['Stop']:  # if request is to stop reading values
            self.Cube.stop()
            self.Queue.put_response(self.Queue.Response['Stop'])

        elif self.Queue.Request[0] == self.Queue.GUIRequest['UpdateSettings']: # if request is to update settings
            if self.Cube.update_settings():
                self.Queue.put_response(self.Queue.Response['UpdateSettings'])
            else:
                self.Queue.put_response(self.Queue.Response['Failed'])

        elif self.Queue.Request[0] == self.Queue.GUIRequest['EndProcess']:  # end the Cube process
            if self.Cube.connected:
                if self.Cube.ReadValues:
                    self.Cube.stop()
                self.Cube.disconnect()
            self.Queue.put_response(self.Queue.Response['EndProcess'])
            self.Queue.Queue.close()
            exit()

    def main(self):
        logging.debug("============CubeProcess.main()============")
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

    Request = {'Start': '12',
               'Stop': '13',
               'Disconnect': '14'}

    def __init__(self, gui_request_arrived):
        self.GUI_Request_Arrived = gui_request_arrived
        # initialize settings Object and apply settings to cube object
        self.Config = Configure()
        self.Settings = self.Config.Settings
        # initialize a socket
        self.Socket = Client.Client(self.Settings.port)

        self.LastAxis = 0
        self.Data = {'CurrentAxis': 0,
                     'GyroValue': 0}
        self.IP = None
        self.connected = False
        self.ReadValues = False


    def _connect_to(self, ip):
        if self.Socket.connect(ip):
            self.connected = True
            return True
        return False

    # connect and send Settings
    def connect(self, ip):
        if self._connect_to(ip):
            self.send(self.Settings.Color)
            return True
        return False


    def disconnect(self):
        if self.connected:
            if self.ReadValues:
                self.send(self.Request['Stop'])
                self.ReadValues = False

            self.send(self.Request['Disconnect'])
            self.Socket.disconnect()
            self.connected = False

    # update the last axis variable and read new data
    # TODO: check if no factor is viable
    def recieve_tcp(self, factor=1):
        self.LastAxis = self.Data['CurrentAxis']
        self.Data = self.Socket.receive()

        if self.Data is False:
            self.Data = {'CurrentAxis': self.LastAxis,
                         'GyroValue': 0}
        else:
            self.Data['GyroValue'] = int(self.Data['GyroValue'] / factor)

    def send(self, value):
        self.Socket.send_tcp(value)

    # start reading values:
    # send cube request to send values
    def start(self):
        if self.connected:
            self.send(self.Request['Start'])
            self.ReadValues = True
            return True
        return False

    # stop reading values:
    # send cube request to stop sending values
    def stop(self):
        self.send(self.Request['Stop'])
        self.ReadValues = False

    # load new settings from disk and apply them, return True/False
    def update_settings(self):
        if self.Config.load_app_settings():
            self.Settings = self.Config.get_app_settings()
            return True
        return False

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
            if self.GUI_Request_Arrived():
                return False

            self.recieve_tcp()
            self.times += 1
            buffer[index] = self.Data['GyroValue']
            # check if changed orientation
            if self.changed_axis():
                return False
            # calculate sumOfMovement
            sumOfMovement += buffer[index] - buffer[(index + 1) % BufferLength]
            #logging.warning(f"sumOfMovement = {sumOfMovement}, threshold: {threshold}")
            index += 1
            index = index % BufferLength
        for i in range(int(0.004*threshold)):
            self.recieve_tcp()
        return sumOfMovement

    # call the configured function based on the current face
    def call(self, face):
        FuncKey = self.Settings.Func_Key[face]
        if FuncKey is not None:
            FuncDict = self.Settings.AppFunctionDict[FuncKey] # get the function dictionary containing its parameters
            args = list(FuncDict.values())  # the values of the function to be called(parameters)
            args.pop(0)  # remove the function call object from arg list

            FuncDict['call'](self.count, *args)

    def main(self):
        self.t1 = time.time()
        self.times = 1
        self.recieve_tcp()
        # call the according function
        self.call(self.Data['CurrentAxis'])
        self.total = time.time() - self.t1
        if self.total != 0:
            logger.warning(f"second: {self.total}, times: {self.times}")
            logger.warning(f"{self.times/self.total} times/second\n")


class Graphic_Interface:

    def __init__(self, Queue, exit_protocol):
        self.Queue = Queue
        self.Style = configuration.GUIConfig.Main_Window()
        # initialize and start the main GUI
        self.MainWindow = tk_interface.GUI(style=self.Style, exit_protocol=exit_protocol)

        self.ConfigWindow = None
        self.IP = self._get_settings_ip()
        self.init_main_window()
        #self.config_window()

    # get hostname/ip from config class
    @staticmethod
    def _get_settings_ip():
        return Configure().get_hostname()

    def main_window(self):
        # Row: 0
        self.Frame_Config = self.MainWindow.Frame()
        self.config_icon = self.MainWindow.get_image("settings-icon20.png")
        self.Button_Configure = self.MainWindow.Button(' Configure ', self.config_window, master=self.Frame_Config)
        self.Button_Configure.configure(image=self.config_icon, background='#4A4A4A',
                                           relief=tk_interface.tk.RAISED, compound='left')

        # Row: 1
        self.Frame_Connect = self.MainWindow.Frame()
        self.Label_IP = self.MainWindow.Label('IP:', master=self.Frame_Connect)
        self.Entry_IP = self.MainWindow.Entry(master=self.Frame_Connect)
        self.Entry_IP.bind("<Key-Return>", lambda event: self.connect_disconnect())
        self.Button_Connect = self.MainWindow.Button('Connect', self.connect_disconnect, master=self.Frame_Connect)

        # Row: 2
        self.Frame_Status = self.MainWindow.Frame()
        self.Label_Status = self.MainWindow.Label('Status:', master=self.Frame_Status)
        self.Label_Current_Status = self.MainWindow.Label('Disconnected', master=self.Frame_Status)

        # Row: 3
        self.Frame_Start = self.MainWindow.Frame()
        self.Button_Start = self.MainWindow.Button('Start', self.start_stop, master=self.Frame_Start)

    def pack_widgets(self):
        self.Frame_Config.grid(row=0, pady=3, sticky='nesw')
        self.Button_Configure.grid(row=0, column=0, padx=15, sticky='w')

        self.Frame_Connect.grid(row=1, pady=3, sticky='nesw')
        self.Label_IP.grid(row=0, column=0)
        self.Entry_IP.grid(row=0, column=1)
        self.Button_Connect.grid(row=0, column=2, padx=15)

        self.Frame_Status.grid(row=2, pady=3, sticky='nesw')
        self.Label_Status.grid(row=0, column=0)
        self.Label_Current_Status.grid(row=0, column=1)

        self.Frame_Start.grid(row=3, pady=3, sticky='nesw')
        self.Button_Start.grid(row=0, column=0)

    def init_main_window(self):
        self.main_window()
        self.pack_widgets()
        self.MainWindow.make_stretchy()
        self.MainWindow.make_stretchy(master=self.Frame_Config)
        self.MainWindow.make_stretchy(master=self.Frame_Connect)
        self.MainWindow.make_stretchy(master=self.Frame_Status)
        self.MainWindow.make_stretchy(master=self.Frame_Start)
        self.update_entry_ip()
        self.Entry_IP.focus()
        self.MainWindow.fix_size()

    def config_window(self):
        self.disconnect()
        self.ConfigWindow = Config_Window(self.Queue, save_protocol=self.update_entry_ip)
        # check ReadValues == False

    def update_entry_ip(self):
        hostname_len = len(self.Entry_IP.get())
        self.Entry_IP.delete(0, hostname_len)
        self.Entry_IP.insert(0, self._get_settings_ip())

    @staticmethod
    def valid_ip(ip):
        if len(ip) > 15:
            logging.warning('valid_ip(): long ip')
            return False

        try:
            a, b, c, d = ip.split('.')
        except ValueError:
            logging.warning('split error')
            return False

        if 0 <= int(a) < 255 and 0 <= int(b) < 255 and 0 <= int(c) < 255 and 0 <= int(d) < 255:
            return True

    # get the ip in entry and if it's valid save it
    def get_ip(self):
        ip = self.Entry_IP.get()
        self.IP = ip
        return self.IP

    # send request to connect and update local variables
    def connect(self):
        self.get_ip()
        if self.IP is not None and self.Queue.CubeState['Connected'] is False:
            if self.Queue.put_connect(self.IP):
                self.Label_Current_Status['text'] = 'Connected'
                self.Button_Connect['text'] = "Disconnect"

    # send request to disconnect and update local variables
    def disconnect(self):
        if self.Queue.CubeState['ReadValues']:
            self.start_stop()
        if self.Queue.put_disconnect():
            self.Label_Current_Status['text'] = 'Disconnected'
            self.Button_Connect['text'] = "Connect"

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
        if self.Queue.put_start():
            self.Button_Start['text'] = 'Stop'
            # self.MainWindow.master.iconify()

    # send request to stop reading values from the cube and update local variables
    def stop_read_values(self):
        if self.Queue.put_stop():
            self.Button_Start['text'] = 'Start'

    def start_stop(self):
        # stop
        if self.Queue.CubeState['ReadValues']:
            self.stop_read_values()
        # start
        else:
            self.start_read_values()

class Config_Window:

    def __init__(self, Queue, save_protocol):
        logging.info(f"============Config Window============")
        self.save_protocol = save_protocol
        self.Queue = Queue
        self.Config = Configure()
        self.Style = configuration.GUIConfig.Config_window()
        self.Menu_Options = ["General", "Face Function", "Function Parameters"]
        self.current_menu_selection = 0
        # initialize and start the main GUI
        self.MainWindow = tk_interface.GUI(style=self.Style, title="MagicCube - Configuration",
                                           TopLevel=True, exit_protocol=self.cancel)
        self.MainWindow.fix_size(width=800, height=500)

        self.init_main_window()
        self.show_General_Menu(True)

    def set_main_window_size(self):
        window_width, window_height = self.MainWindow.get_size()
        self.Frame_Listbox.configure(width=200)
        self.Frame_Buttons.configure(width=200, height=50)
        #self.Menu.configure(selectmode='single', height=int(window_height * 0.05))
        self.Frame_Main.configure(width=200)

    def main_window(self):

        # Listbox Frame
        self.Frame_Listbox = self.MainWindow.Frame()

        self.Menu = self.MainWindow.Listbox(self.Frame_Listbox)
        self.Menu.bind("<ButtonRelease-1>", self.get_Menu_listbox_selection)

        self.Frame_Buttons = self.MainWindow.Frame()
        self.Button_Save = self.MainWindow.Button("Save", self.save, master=self.Frame_Buttons)
        self.Button_Cancel = self.MainWindow.Button("Cancel", self.cancel, master=self.Frame_Buttons)

        self.Frame_Main = self.MainWindow.Frame()

    def general_menu(self):
        self.Frame_Menu_General = self.MainWindow.Frame(self.Frame_Main)

        self.Label_Hostname = self.MainWindow.Label("Default Hostname", self.Frame_Menu_General)
        self.Entry_Hostname = self.MainWindow.Entry(self.Frame_Menu_General)
        self.Entry_Hostname.insert(0, self.Config.get_hostname())
        self.Label_Hostname.configure(padx=len("Default Hostname"))

        self.Label_Port = self.MainWindow.Label("Port", self.Frame_Menu_General)
        self.Entry_Port = self.MainWindow.Entry(self.Frame_Menu_General)
        self.Entry_Port.insert(0, self.Config.get_port())

    def face_func_menu(self):
        self.Frame_Menu_Face_Func = self.MainWindow.Frame(self.Frame_Main)
        self.Frame_Menu_Face_Func.configure(border=0)
        self.Frame_Face_List = [self.MainWindow.Frame(self.Frame_Menu_Face_Func) for i in range(6)]
        self.Lable_Face = list()
        self.DropDown_Func_Menu = list()
        self.DropDown_Icon = self.MainWindow.get_image("arrow-dropdown-icon10.png")
        self.Color_Picker_List = list()
        self.Color_Picker_Icon = self.MainWindow.get_image("color-palette-icon20.png")

        index = 0
        for Frame_Face in self.Frame_Face_List:
            self.Lable_Face.append(self.MainWindow.Label("Face " + str(index + 1), Frame_Face))
            self.DropDown_Func_Menu.append(self.MainWindow.DropDown(self._get_current_face_func(index), Frame_Face))
            self._create_func_menu(self.DropDown_Func_Menu, index)
            self._create_color_chooser(Frame_Face, index)
            index += 1

    # return the current setting func for face, return "Choose a function" if none
    def _get_current_face_func(self, face_num):
        if self.Config.get_face_func(face_num) is None:
            return "Choose a function"
        return self.Config.get_face_func(face_num).ljust(20)

    # create the menu for the menubutton, and add the options
    def _create_func_menu(self, DropDown, index):
        def add_option(DropDown, index, func_key):
            DropDown[index].Options.add_command(label=func_key, command=lambda: self.set_Face_Func_selection(index, func_key))

        DropDown[index].configure(width=200, image=self.DropDown_Icon, compound='right') # add icon to dropdown
        DropDown[index].Options = (self.MainWindow.Menu(DropDown[index])) # add menu to dropdown
        #DropDown[index].Options.configure(background="#4A4A4A")

        #add the options
        Func_Key_list = self.Config.get_AppFunctionDict_keys()
        # insert None option if function already assigned
        Func_Key_list.insert(0, "None")
        for func_key in Func_Key_list:
            add_option(DropDown, index, func_key)

        DropDown[index]['menu'] = DropDown[index].Options

    def _create_color_chooser(self, Frame, index):
        self.Color_Picker_List.append(self.MainWindow.Button("", lambda: self.set_Face_Color(index), Frame))
        self.Color_Picker_List[index].configure(background=self.Config.get_face_color(index, hex=True),
                                                image=self.Color_Picker_Icon)

    def pack_widgets(self):
        self.Frame_Listbox.grid(row=0, column=0, sticky='nesw')
        self.Menu.grid(row=0, column=0, sticky='nesw')

        self.Frame_Buttons.grid(row=1, column=0, sticky='nesw')
        self.Button_Save.grid(row=0, column=0, sticky='nesw')
        self.Button_Cancel.grid(row=0, column=1, sticky='nesw')

        self.Frame_Main.grid(row=0, column=1, rowspan=2, sticky='nesw')

    def pack_general_widgets(self):
        #self.Frame_Menu_General.grid(row=0, column=0, pady=40)
        self.Label_Hostname.grid(row=0, column=0, padx=15, pady=10)
        self.Entry_Hostname.grid(row=0, column=1, padx=15)
        self.Label_Port.grid(row=1, column=0, pady=10)
        self.Entry_Port.grid(row=1, column=1)

    def pack_face_func_menu(self):
        index = 0
        for Frame_Face in self.Frame_Face_List:
            Frame_Face.grid(row=index, column = 0, ipadx=20)
            self.Lable_Face[index].grid(row=0, column=0)
            self.DropDown_Func_Menu[index].grid(row=0, column=1, pady=15, padx=20)
            self.Color_Picker_List[index].grid(row=0, column=2)
            index += 1

    # pack the General menu frame
    def show_General_Menu(self, show):
        if show:
            self.Frame_Menu_General.grid(row=0, column=0, pady=40)
            self.MainWindow.make_stretchy(master=self.Frame_Main, make_row=False)
        elif show is False:
            self.Frame_Menu_General.grid_forget()

    # pack the Face_Func menu frame
    def show_Face_Func_Menu(self, show):
        if show:
            self.Frame_Menu_Face_Func.grid(row=0, column=0, pady=40)
            self.MainWindow.make_stretchy(master=self.Frame_Main, make_row=False)
        elif show is False:
            self.Frame_Menu_Face_Func.grid_forget()

    # initialize the main window, not packing any specific menu frame
    def init_main_window(self):
        self.main_window()
        #self.set_main_window_size()
        self.pack_widgets()

        # add options to listbox menu
        for option in self.Menu_Options:
            self.Menu.insert(tk_interface.tk.END, option)

        # make the frames stretchy
        self.make_stretchy()
        self.MainWindow.make_stretchy(master=self.Frame_Listbox)
        self.MainWindow.make_stretchy(master=self.Frame_Buttons)
        self.MainWindow.make_stretchy(master=self.Frame_Main)
        # pack all the Menus
        self.general_menu()
        self.pack_general_widgets()
        self.face_func_menu()
        self.pack_face_func_menu()

    # like the tk_interface but specially made for this window
    def make_stretchy(self):
        self.MainWindow.master.rowconfigure(0, weight=1)
        #self.MainWindow.master.columnconfigure(0, weight=1)
        self.MainWindow.master.columnconfigure(1, weight=1)

    # show the desired menu(called on click release on self.Menu)
    def get_Menu_listbox_selection(self, event):
        selection = self.Menu.curselection()[0]
        if self.current_menu_selection != selection:
            self.current_menu_selection = selection

            if self.current_menu_selection == 0:
                self.show_Face_Func_Menu(False)
                self.show_General_Menu(True)
            elif self.current_menu_selection == 1:
                self.show_General_Menu(False)
                self.show_Face_Func_Menu(True)
            elif self.current_menu_selection == 2:
                self.show_General_Menu(False)
                self.show_Face_Func_Menu(False)
            else:
                self.show_Face_Func_Menu(False)
                self.show_General_Menu(False)
            logging.info(f"selected: {self.Menu.get(self.Menu.curselection()[0])}")

    # set the face function and change the text accordingly
    def set_Face_Func_selection(self, face, func):
        if func == "None":
            func = None
        self.Config.set_face_func(face, func)
        self.DropDown_Func_Menu[face]['text'] = self._get_current_face_func(face)
        logging.info(f'Face: {face}, Func: {func}')

    # prompt the user to choose color and set it accordingly
    def set_Face_Color(self, face):
        color = self.MainWindow.Color_Picker(self.Config.get_face_color(face), self.Color_Picker_List[face])
        rgb_color = self.Config.hex_to_rgb(color[1])
        self.Config.set_face_color(face, rgb_color)
        self.Color_Picker_List[face].configure(background=color[1])
        logging.info(f"Face: {face}, Color: {rgb_color}")

    # save changes to disk and quit
    def save(self):
        self.Config.set_hostname(self.Entry_Hostname.get())
        self.Config.set_port(self.Entry_Port.get())
        self.Config.save(self.Config.AppSettingsPath)
        del self.Config
        self.Queue.put_update_settings()
        self.save_protocol()
        self.MainWindow.destroy()
        logging.info(f"============Configuration saved============")

    def cancel(self):
        self.MainWindow.destroy()
        logging.info(f"============Configuration discarded============")


class GUIProcess:
    class GUI_Queue:

        GUIRequest = configuration.MultiProcess_config.GUIRequest
        Response_id = configuration.MultiProcess_config.Response

        CubeState = {'Connected': False,
                     'ReadValues': False,
                     'IP': None,
                     'CurrentFace': None}

        def __init__(self):
            self.Queue = multiprocessing.Queue()
            self.ResponseQ = multiprocessing.Queue()

        # fetch a response
        # return it if response fetched
        # return False if Queue is empty
        def get_response(self, **kwargs):
            try:
                return self.ResponseQ.get(**kwargs)
            except queue.Empty:
                return False

        # Put a request and wait for a response
        # if it's the same as request return True
        def put_connect(self, ip):
            request = [self.GUIRequest['Connect'], ip]
            self.Queue.put(request)
            if self.get_response() == self.Response_id['Connect']:
                self.CubeState['Connected'] = True
                return True
            logging.warning(f"Could't connect")
            return False

        def put_disconnect(self):
            self.Queue.put([self.GUIRequest['Disconnect']])  # request is expected as a list!
            if self.get_response() == self.Response_id['Disconnect']:
                self.CubeState['Connected'] = False
                return True
            return False

        def put_start(self):
            self.Queue.put([self.GUIRequest['Start']])  # request is expected as a list!
            if self.get_response() == self.Response_id['Start']:
                self.CubeState['ReadValues'] = True
                return True
            return False

        def put_stop(self):
            self.Queue.put([self.GUIRequest['Stop']])  # request is expected as a list!
            if self.get_response() == self.Response_id['Stop']:
                self.CubeState['ReadValues'] = False
                return True
            return False

        def put_update_settings(self):
            self.Queue.put([self.GUIRequest['UpdateSettings']])# request is expected as a list!
            if self.get_response() == self.Response_id['UpdateSettings']:
                return True
            return False

        def put_end_process(self):
            self.Queue.put([self.GUIRequest['EndProcess']])  # request is expected as a list!
            if self.get_response() == self.Response_id['EndProcess']:
                self.CubeState['Connected'] = False
                self.CubeState['ReadValues'] = False
                return True
            return False

    def __init__(self):
        self.Queue = self.GUI_Queue()
        self.GUI = Graphic_Interface(self.Queue, self.exit)
        self.Cube = multiprocessing.Process(target=CubeProcess, args=(self.Queue.Queue, self.Queue.ResponseQ), name="Cube")

        logging.info("============GUI Process Started============")

    def start(self):
        self.Cube.start()
        self.GUI.MainWindow.master.mainloop()
        #self.exit()

    #passed to a GUI object as exit_protocol
    def exit(self):
        self.Queue.put_end_process()
        self.Queue.Queue.close()
        self.GUI.MainWindow.destroy()


if __name__ == '__main__':

    GUI = GUIProcess()
    GUI.start()



