#import Server
import Server1 as Server
import threading
import mpu6050_Interface
from time import sleep
import LED_Interface
from configuration import CubeDefaultSettings
from configuration import CubeConfig
from sys import exit



class MPU_6050:
    def __init__(self):
        self.Data = {'CurrentAxis': 0,
                     'GyroValue': 0}
        self.last_axis = 0

        self.gyro = mpu6050_Interface.Gyro()
        self.accel = mpu6050_Interface.Accelerometer()
        self.update_values()

    #  when wait is True it will wait until the cube is on an axis
    def update_values(self, wait=False):
        self.gyro.get_gyro_average(10)
        self.last_axis = self.Data['CurrentAxis']  # update last axis
        if self.gyro.changed_axis():

            sleep(CubeConfig.Gyro_Axis_Change_Delay)
            self.gyro.set_axis(self.accel.get_orientation(wait_for_axis=wait))
            self.Data['CurrentAxis'] = self.accel.data['CurrentAxis']

        # if cube is at None axis than gyro value should be ignored and set to 0
        if self.Data['CurrentAxis'] is None:
            self.Data['GyroValue'] = 0
        else:
            self.Data['GyroValue'] = self.gyro.data[self.gyro.current_axis]
        #print(self.Data)

    def changed_axis(self):
        if self.last_axis != self.Data['CurrentAxis']:
            return True
        return False

    def get_data(self):
        return self.Data


class MagicCube:
    Received_Data_Flag = '9'
    Command = {'Start': '12',
               'Stop': '13',
               'Disconnect': '14'}

    def __init__(self):
        self.Settings = CubeDefaultSettings.ColorSettings()
        self.send_values = False
        self.MPU = MPU_6050()

        self.server = Server.Server(CubeConfig.ip, CubeConfig.port)
        self.led = LED_Interface.LED(6, self.Settings)

        self.accept_connection()



    # wait for a connection
    def accept_connection(self):
        self.server.accept_connection()
        self.server.receive() # Receive Cube Settings
        self.process_request()
        self.led.startup_effect()
        # server.send_tcp(Data)

    # ask if user want to reconnect and act accordingly
    def reconnect(self):
        self.server.close_connection()
        ask = input("client disconnected, do you want to continue(Y/N)")
        if ask == 'y':
            self.accept_connection()
            return True
        else:
            self.led.set_preset(self.Settings.PRST_OFF)
            self.send_values = False
            return False

    def process_request(self):
        #print("type(self.server.data): " + str(type(self.server.data)))
        if type(self.server.data) == str:
            if self.server.data == self.Command['Start']:
                self.send_values = True

            elif self.server.data == self.Command['Stop']:
                self.send_values = False

            elif self.server.data == self.Command['Disconnect']:
                self.server.close_connection()
                self.send_values = False
                if not self.reconnect():
                    exit()

        elif type(self.server.data) == type(self.Settings):
            print("==========Received color settings!==========")
            self.update_settings()

    def update_settings(self):
        self.Settings = self.server.data
        self.led.set_settings(self.Settings)

    def main(self):
        while self.send_values is False:
            if self.server.receive():
                self.process_request()

        while self.send_values:
            if self.run() == self.Received_Data_Flag:
                self.process_request()

    # start sending the sensor data
    def run(self):
        listen = threading.Thread(target=self.server.receive)
        listen.start()

        while listen.isAlive():
            self.MPU.update_values() # update sensor values

            #data = self.MPU.get_data()
            #self.send_thread = threading.Thread(target=self.server.send_tcp, args=(data,))
            #self.send_thread.daemon = True
            #if self.send_thread.isAlive():
            #    self.send_thread.join()
            if self.MPU.Data['CurrentAxis'] is not None:
            #    self.send_thread.start()
                self.server.send_tcp(self.MPU.Data)
                if self.MPU.changed_axis():
                    self.led.brightness_fade_down()
                    self.led.set_preset(self.Settings.Face_List[self.MPU.Data['CurrentAxis']])
                    self.led.brightness_fade_up(self.Settings.PRST_ON_EDGE['Brightness'])
            else:
                if self.MPU.changed_axis():
                    self.led.brightness_fade_down()
                    self.led.set_preset(self.Settings.PRST_ON_EDGE, change_brightness=True)
                    self.led.brightness_fade_up(self.Settings.PRST_ON_EDGE['Brightness'])

        listen.join()
        return self.Received_Data_Flag


Cube = MagicCube()

while True:
    try:
        Cube.main()
        
    except ConnectionResetError as err:
        print(err)
        if Cube.reconnect():
            continue
        else:
            exit()
    except EOFError as err:
        print(err)
        if Cube.reconnect():
            continue
        else:
            exit()
    except BrokenPipeError as err:
        print(err)
        if Cube.reconnect():
            continue
        else:
            exit()


