import socket               # Import socket module
import pickle


class Client:
    def __init__(self, port):
        self.Socket = socket.socket()
        self.port = port
        self.Socket.settimeout(10)

        # Client variables
        # self.Client = None
        # self.ClientAddress = None
        #
        # self.Data = dict()

    # connect to the cube, throws exception if failed
    def connect(self, server_ip):
        try:
            self.Socket.connect((server_ip, self.port))
        except OSError as err:
            # if socket was closed(error 10038) create a new one
            if '[WinError 10038]' in str(format(err)):
                self.Socket = socket.socket()
                self.Socket.settimeout(10)
                self.Socket.connect((server_ip, self.port))

    def disconnect(self):
        self.Socket.close()

    def recieve_tcp(self, size=1024):
        try:
            return pickle.loads(self.Socket.recv(size))
        except pickle.UnpicklingError:
            return False

    def send_tcp(self, value):
            self.Socket.send(pickle.dumps(value, -1))

