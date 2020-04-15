import pickle
import logging
import socket
from _thread import *

from player import (Player, Move)
logging.basicConfig(level=logging.DEBUG, format="server: %(message)s")

server = "192.168.0.11"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
logging.info("Waiting for a connection, server started")


PLAYERS = []

MOVES = [None, None, None, None]


def threaded_client(conn, player_id):
    global PLAYERS
    PLAYERS.append(Player(player_id))

    logging.info(f"client connected")
    conn.send(pickle.dumps(player_id))

    while True:
        try:

            data = pickle.loads(conn.recv(2048))
            logging.info(data)

            if not data:
                print("Disconnected")
                break
            # connection
            elif data == "n_connected":
                logging.info("n_connected")
                conn.sendall(pickle.dumps(len(PLAYERS)))
            elif data == "get_players":
                logging.info("get_players")
                conn.sendall(pickle.dumps(PLAYERS))
            # game
            elif isinstance(data, Move):
                # tell other players that you moved
                for i in range(len(MOVES)):
                    if i == player_id:
                        continue
                    MOVES[i] = data
                conn.sendall(pickle.dumps("Move sent"))
            elif data == "get_move":
                # check if other players moved
                move = MOVES[player_id]
                if move:
                    # clear move
                    MOVES[player_id] = None
                # send move
                conn.sendall(pickle.dumps(move))
            else:
                break
        except:
            break

    logging.info("Lost connection")
    conn.close()


current_player = 0
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    start_new_thread(threaded_client, (conn, current_player))
    current_player += 1
