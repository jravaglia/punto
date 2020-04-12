import socket
from _thread import *

from player import (Player, Board)
import pickle
server = "192.168.0.11"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, server started")

players = [Player(i) for i in range(4)]


def threaded_client(conn, player):
    conn.send(pickle.dumps(players[player]))
    reply = ""
    while True:
        # try:

        data = pickle.loads(conn.recv(2048))
        players[player] = data
        if not data:
            print("Disconnected")
            break
        else:
            if player == 1:
                reply = players[0]
            else:
                reply = players[1]

            print("Received: ", data)
            print("Sending: ", reply)
        print("sendall")
        conn.sendall(pickle.dumps(reply))
        # except:
        #     break

    print("Lost connection")
    conn.close()

current_player = 0
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    start_new_thread(threaded_client, (conn, current_player))
    current_player += 1
