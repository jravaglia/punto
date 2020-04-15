import sys
import logging
import pygame

from network import Network
from player import (Game, Move, Player, WIDTH)


logging.basicConfig(level=logging.DEBUG, format="gui: %(message)s")
pygame.font.init()

caption = "Client"
# TODO: use argparse
# assign a caption name
if len(sys.argv) > 1:
    caption = sys.argv[1]


HEIGHT = WIDTH
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(caption)


class ConnectionWindow:
    def __init__(self, n, win, max_player):
        self.n = n
        self.win = win
        # self.player = 1
        self.player_id = n.get_player_id()
        self.player_in = 1
        self.max_player = max_player
        self.players = None
        logging.info(f"ConnectionWindow: player_in: {self.player_in}")
        logging.info(f"ConnectionWindow: player_id: {self.player_id}")

    def loop(self):
        self.player_in = self.n.send("n_connected")
        if self.player_in == self.max_player:
            self.players = self.n.send("get_players")
            return False
        else:
            self.redraw_window()
            return True

    def redraw_window(self):
        logging.info(f"ConnectionWindow: redrawing")
        self.win.fill((0, 0, 0))
        font_obj = pygame.font.SysFont('Sans Serif', 40)
        text = f"Waiting for other players ({self.player_in}/{self.max_player})"
        text_surface_obj = font_obj.render(text, False, (255,255,255))

        text_rect_obj = text_surface_obj.get_rect()
        text_rect_obj.center = (WIDTH / 2, HEIGHT / 2)
        self.win.blit(text_surface_obj, text_rect_obj)
        pygame.display.update()


def redraw_window(win, game):
    win.fill((255,255,255))
    game.draw(win)
    pygame.display.update()


def main_online():
    run = True
    n = Network()
    n_player = 2

    game = None
    clock = pygame.time.Clock()
    connection_window = ConnectionWindow(n, win, n_player)

    state = "connection"
    while run:
        clock.tick(60)
        # need this loop to prevent game from crashing: why?
        events = [e.type for e in pygame.event.get()]

        if pygame.QUIT in events:
            run = False
            pygame.quit()

        if state == "connection":
            if not connection_window.loop():
                game = Game(connection_window.player_id,
                            connection_window.players)
                state = "game"

            logging.info("main: after connection loop")

        elif state == "game":
            # your turn
            if game.current_player.p == connection_window.player_id:
                if pygame.MOUSEBUTTONUP in events:
                    logging.info("button up")
                    mouse_pos = pygame.mouse.get_pos()
                    card_pos = game.play_card(mouse_pos)
                    if card_pos:
                        res = n.send(Move(connection_window.player_id, mouse_pos))
                    winner = game.is_winner()
                    logging.info(f"winner: {winner}")
                    if winner >= 0:
                        logging.info("reset game")
                        game = Game(connection_window.player_id,
                                    connection_window.players)

            # others turn
            else:
                move = n.send("get_move")
                logging.info(f"other: {move}")
                if move:
                    game.play_card(move.xy_pos)
                    winner = game.is_winner()
                    logging.info(f"winner: {winner}")
                    if winner >= 0:
                        logging.info("reset game")
                        game = Game(connection_window.player_id,
                                    connection_window.players)

            redraw_window(win, game)


def main_local():
    run = True
    n_player = 2

    game = Game(0, [Player(i) for i in range(n_player)])
    clock = pygame.time.Clock()

    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_pos = pygame.mouse.get_pos()
                card_pos = game.play_card(mouse_pos)
                winner = game.is_winner()
                logging.info(f"winner: {winner}")
                if winner >= 0:
                    logging.info("reset game")
                    game = Game(0, [Player(i) for i in range(n_player)])

        redraw_window(win, game)

# main_online()
main_local()

