import socket
import pickle
import logging
logging.basicConfig(level=logging.DEBUG, format="network: %(message)s")


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.0.11"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.player_id = self.connect()

    def get_player_id(self):
        return self.player_id

    def connect(self):
        try:
            logging.info("connect try")
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(2048))
        except:
            logging.info("connect except")
            pass

    def send(self, data):
        try:
            logging.info("send try")
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048))
        except socket.error as e:
            logging.info("send except")
            print(e)


