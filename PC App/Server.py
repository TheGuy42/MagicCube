import socket


class Server:
    def __init__(self):
        self.Socket = socket.socket()
        self.host = socket.gethostname()
        self.port = 12345
        self.Socket.bind((self.host, self.port))
        self.Socket.listen(5)
        # Client variables
        self.Client = None
        self.ClientAddress = None
        #
        self.send_bytes = b''
        self.recieve_bytes = b''
        self.END_CONNECTION = 999999

    def accept_connection(self):
        self.Client, self.ClientAddress = self.Socket.accept()

    def recieve_tcp(self, size):
        if self.Client is not None:
            self.recieve_bytes = self.Client.recv(size)

    def send_tcp(self, value):
        if self.Client is not None:
            self.Client.send(bytes(str(value), 'utf-8'))
            return True
        return False

    def close_connection(self):
        if self.Client is not None:
            self.Client.close()


server = Server()
server.accept_connection()
while server.recieve_bytes != server.END_CONNECTION:

    server.recieve_tcp(1024)
    print(server.recieve_bytes)

server.close_connection()
