import socket
import pickle
from time import sleep

class Server:
    def __init__(self, ip, port):
        self.Socket = socket.socket()
        self.host = socket.gethostname()
        self.port = port
        # self.ip = '10.0.0.30'
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        self.Socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # start a socket
        self.Socket.bind((str(ip), self.port))
        self.Socket.listen(1)
        # Client variables
        self.Client = None
        self.ClientAddress = None
        self.Received = bytes()

        self.header = int()
        self.header_received = False
        self.header_len = 3
        self.data = str()
        self.data_received = False
        self.data_len = None

    # accept a connection
    def accept_connection(self):
        self.Client, self.ClientAddress = self.Socket.accept()
        #self.Client.setblocking(False)
        print(self.Client)

    # close the connection to the client
    def close_connection(self):
        if self.Client is not None:
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
            # self.Received = bytes()
            return False

    # send the value, add a header of fixed length containing the length of the data sent
    def send_tcp(self, value):
        if self.Client is not None:
            value = pickle.dumps(value)
            header = str(len(value)).zfill(self.header_len).encode('utf-8')
            ###print('>> Sent header: ' + str(header) + ' , data: ' + str(value))
            self.Client.sendall(bytes(header))
            self.Client.sendall(value)
            sleep(0.0015)


    # get the header of the data, containing it's length
    # return false if there is nothing to read
    def get_header(self):
        if self.header_received is False:
            while len(self.Received) < self.header_len:
                if not self.receive_tcp():
                    return False

            self.header = int(self.Received[:self.header_len])
            self.Received = self.Received[self.header_len:]
            self.header_received = True
            #print('<< Received header: ' + str(self.header))
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
            print('\n<< Received data: ' + str(self.data))
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
server = Server("10.0.0.26", 4444)
server.accept_connection()
i = 0
lost = 0

while server.data != 'exit':
    #if not server.receive():
     #   lost += 1
      #  continue

    server.send_tcp(pickle.dumps('Hello'))
    i += 1
    #print(f'received {i} messages, lost: {lost} \n')


server.close_connection()
"""