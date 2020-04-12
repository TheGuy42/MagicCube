import socket               # Import socket module
import pickle
from time import sleep
import logging

cpu_speed_ghz = 3.6

logger = logging.getLogger("Logger")

class Client:
    def __init__(self, port):
        self.Client = socket.socket()
        self.port = port
        #self.Client.settimeout(1)

        self.Received = bytes()

        self.header = int()
        self.header_received = False
        self.header_len = 3
        self.data = str()
        self.data_received = False

    def _connect(self, server_ip):
        try:
            self.Client.connect((server_ip, self.port))
            #self.Client.setblocking(False)
            logging.info(self.Client)
            return True
        except OSError as err:
            logging.warning(f"ERROR: {err}" )
            logging.debug(f'{self.Client}')
            return False

    # connect to the cube, returns False if failed
    def connect(self, server_ip):
        try:
            self.Client.connect((server_ip, self.port))
            #self.Client.setblocking(False)
            logging.info(self.Client)
            return True
        except OSError:
            self.Client = socket.socket()
            return  self._connect(server_ip)

    # close the connection to the server
    def disconnect(self):
        logging.info(f"Disconnecting from {self.Client}")
        self.Client.close()

    # receive data. store it in the 'self.Received' buffer
    # the data received might still be pickled
    def receive_tcp(self, size=1024):
        try:
            if self.Client is not None:
                self.Received += self.Client.recv(size)
                return self.Received
            return False
        except BlockingIOError:
            #self.Received = bytes()
            return False

    # send the value, add a header of fixed length containing the length of the data sent
    def send_tcp(self, value):
        if self.Client is not None:
            value = pickle.dumps(value)
            header = str(len(value)).zfill(self.header_len).encode('utf-8')
            logging.debug(f'>> Sent header: {header}, data: {value}')
            self.Client.sendall(bytes(header))
            self.Client.sendall(value)
        sleep(0.0032 * cpu_speed_ghz)

    # get the header of the data, containing it's length
    # return false if there is nothing to read
    def get_header(self):
        if  self.header_received is False:
            while len(self.Received) < self.header_len:
                if not self.receive_tcp():
                    return False

            self.header = int(self.Received[:self.header_len])
            self.Received = self.Received[self.header_len:]
            self.header_received = True
            logging.debug(f'<< Received header: {self.header} of type: {type(self.header)}')
            return True

    # get the data, based on the value of the header
    # store the data and return it (unpickle if necessary)
    def get_data(self):
        if self.header_received:
            while len(self.Received) < self.header:
                if not self.receive_tcp():
                    return False

            self.data = pickle.loads(self.Received[:self.header])
            if type(self.data) == type(bytes()):
                self.data = pickle.loads(self.data)
            self.Received = self.Received[self.header:]
            self.data_received = True
            logging.debug(f'<< Received data: {self.data} of type: {type(self.data)}\n')
            return True

    # initialize a new read, get the header and data
    # return the data on success and False on failure(or no data to read)
    def receive(self):
        self.header_received = False
        self.data_received = False

        if self.get_header():
            if not self.get_data():
                # server.clear_values()
                return False
        else:
            # server.clear_values()
            return False

        return self.data


"""
client = Client(4444)
client.connect('10.0.0.26')
#client.send_tcp(10)
Input = ''
send = threading.Thread(target=print)
send.start()

while Input != "exit":
    #Input = input("what to send: ")
    client.receive()
    #if Input == 'exit':
        #client.send_tcp(Input)
        #send = threading.Thread(target=client.send_tcp, args=(Input, ))
        #send.start()
        #send.join()
        #break

    #for i in range(1000):
        #send.join()
        #Input = pickle.dumps(Color())
        #client.send_tcp(Input)
        #send = threading.Thread(target=client.send_tcp, args=(Input, ))
        #send.start()
        #client.receive()

    #send.join()




client.disconnect()
"""