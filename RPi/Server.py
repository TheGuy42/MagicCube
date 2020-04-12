import socket
import pickle


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
        self.Received = None

    def accept_connection(self):
        self.Client, self.ClientAddress = self.Socket.accept()
        self.Client.setblocking(False)

    def recieve_tcp(self, size=1024):
        try:
            if self.Client is not None:
                self.Received = pickle.loads(self.Client.recv(size))
                return True
        except BlockingIOErrr: # Resource temporarily unavailable
            self.Received = None
            return False

    def send_tcp(self, value):
        if self.Client is not None:
            self.Client.send(pickle.dumps(value, -1))

    def close_connection(self):
        if self.Client is not None:
            self.Client.close()
