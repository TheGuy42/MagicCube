import Server
import mpu6050_Interface
from time import sleep
import LED_Interface
from config import Color
from config import CubeConfig


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
        print(self.Data)

    def changed_axis(self):
        if self.last_axis != self.Data['CurrentAxis']:
            return True
        return False


class MagicCube:
    Received_Data_Flag = 9
    Command_Run = 10
    Command_Stop = 11

    def __init__(self):
        self.Settings = Color()
        self.Running = False
        self.MPU = MPU_6050()

        self.server = Server.Server(CubeConfig.ip, CubeConfig.port)
        self.accept_connection()

        self.led = LED_Interface.LED(6)

    # wait for a connection
    def accept_connection(self):
        self.server.accept_connection()
        # server.send_tcp(Data)

    # ask if user want to reconnect and act accordingly
    def reconnect(self):
        ask = input("client disconnected, do you want to continue(Y/N)")
        if ask == 'y':
            self.accept_connection()
        else:
            self.led.set_preset(Color.PRST_OFF)
            self.Running = False
            return False

    def process_request(self):
        if type(self.server.Received) == str:
            if self.server.Received == str(self.Command_Run):
                self.Running = True
            elif self.server.Received == str(self.Command_Stop):
                self.Running = False

        elif type(self.server.Received) == type(Color):
            self.Settings = self.server.Received

    def main(self):
        while self.Running is False:
            if self.server.recieve_tcp():
                self.process_request()

        while self.Running:
            if self.run() == self.Received_Data_Flag:
                self.process_request()

    # start sending the sensor data
    def run(self):
        while self.server.recieve_tcp() is False:

            # send values
            self.MPU.update_values()

            if self.MPU.Data['CurrentAxis'] is not None:
                self.server.send_tcp(self.MPU.Data)
                if self.MPU.changed_axis():
                    self.led.brightness_fade_down()
                    self.led.set_preset(self.Settings.Led_Face_List[self.MPU.Data['CurrentAxis']])
                    self.led.brightness_fade_up(self.Settings.PRST_ON_EDGE['Brightness'])
            else:
                if self.MPU.changed_axis():
                    self.led.brightness_fade_down()
                    self.led.set_preset(self.Settings.PRST_ON_EDGE, change_brightness=True)
                    self.led.brightness_fade_up(self.Settings.PRST_ON_EDGE['Brightness'])

        return self.Received_Data_Flag


Cube = MagicCube()

while True:
    try:
        Cube.main()
        
    except ConnectionResetError as err:
        print(err)
        if not Cube.reconnect():
            break
    except EOFError as err:
        print(err)
        if not Cube.reconnect():
            break
    except BrokenPipeError as err:
        print(err)
        if not Cube.reconnect():
            break



