import socket
from _thread import *
import pickle
import logging
logging.basicConfig(level=logging.DEBUG, format="server: %(message)s")

from player import (Player, Board)

server = "192.168.0.11"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
logging.info("Waiting for a connection, server started")

players = []


def threaded_client(conn, player_id):
    player = Player(player_id)

    global players
    players.append(player)

    logging.info(f"client connected")
    conn.send(pickle.dumps(player_id))

    reply = ""
    while True:
        # try:

        data = pickle.loads(conn.recv(2048))
        logging.info(data)

        if not data:
            print("Disconnected")
            break
        elif data == "n_connected":
            logging.info("n_connected")
            conn.sendall(pickle.dumps(len(players)))
        elif data == "get_players":
            logging.info("get_players")
            conn.sendall(pickle.dumps(players))


        else:
            if player == 1:
                reply = players[0]
            else:
                reply = players[1]

            print("Received: ", data)
            print("Sending: ", reply)
        # print("sendall")
        # conn.sendall(pickle.dumps(reply))
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
