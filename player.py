import pygame
import random

SPACE = 10
CARD_SIZE = 30
WIDTH = 500

CARD_EMPTY = -1
CARD_SELECTABLE = -2
CARD_HOVER = -3

EMPTY = (200, 200, 200)
SELECTABLE = (255,0,0)


PLAYER_COLORS = [(27,158,119), (217,95,2), (117,112,179), (231,41,138)]
PLAYER_POS = [(WIDTH/2, 0), (WIDTH/2, WIDTH), (0, WIDTH/2), (WIDTH, WIDTH/2)]

N_COL = 11
N_ROW = N_COL
N_SPACE = N_COL - 1

MARGIN = (WIDTH - N_COL*CARD_SIZE - N_SPACE*SPACE)/2


def pos_to_xy(pos):
    x = MARGIN + pos[0] * CARD_SIZE + pos[0] * SPACE
    y = MARGIN + pos[1] * CARD_SIZE + pos[1] * SPACE
    return x, y


class Player:
    def __init__(self, p):
        self.p = p
        self.color = PLAYER_COLORS[self.p]
        self.pos = PLAYER_POS[self.p]
        self.deck = list(range(1, 10)) + list(range(1, 10))
        random.shuffle(self.deck)
        self.playing = False
        self.current_card = None

    def draw_card(self):
        self.current_card = self.deck.pop()
        return self.current_card

    def draw(self, win):
        font_obj = pygame.font.SysFont('Sans Serif', 40)
        if self.playing and self.current_card:
            text = f"Player {self.p}: play {self.current_card}"
        else:
            text = f"Player {self.p}: waiting"
        text_surface_obj = font_obj.render(text, False, PLAYER_COLORS[self.p])

        if self.p == 0:
            text_rect_obj = text_surface_obj.get_rect()
            text_rect_obj.midtop = PLAYER_POS[self.p]
        elif self.p == 1:
            text_rect_obj = text_surface_obj.get_rect()
            text_rect_obj.midbottom = PLAYER_POS[self.p]
        elif self.p == 2:
            text_surface_obj = pygame.transform.rotate(text_surface_obj, 90)
            text_rect_obj = text_surface_obj.get_rect()
            text_rect_obj.midleft = PLAYER_POS[self.p]
        else:
            text_surface_obj = pygame.transform.rotate(text_surface_obj, 270)
            text_rect_obj = text_surface_obj.get_rect()
            text_rect_obj.midright = PLAYER_POS[self.p]

        win.blit(text_surface_obj, text_rect_obj)


class Board:
    def __init__(self):
        self.round = 0
        self.game_start = True
        self.board = {}
        for i in range(N_COL):
            for j in range(N_ROW):
                self.board[(i, j)] = (-1, CARD_EMPTY)

        self.set_selectable()

    def update(self, pos, data):
        self.board[pos] = data
        if self.game_start:
            self.game_start = False
        self.set_selectable()

    def set_selectable(self):
        res = []
        for pos in self.get_all_selectables():
            self.board[pos] = (-1, CARD_SELECTABLE)
            res.append(pos)

        return res

    def get_all_selectables(self):
        if self.game_start:
            yield 5, 5
        else:
            for (x, y), (p, card_value) in self.board.items():
                if card_value < 0:
                    continue
                for pos in self.get_selectables_from_pos(x, y, card_value):
                    yield pos

    def get_selectables_from_pos(self, x, y, val):
        for x_shift in [-1, 0, 1]:
            for y_shift in [-1, 0, 1]:
                if (x_shift, y_shift) == (0, 0):
                    continue
                new_pos = (x+x_shift, y+y_shift)
                if new_pos in self.board:
                    if self.board[new_pos][1] == CARD_EMPTY:
                        yield new_pos
                    elif self.board[new_pos][1] > val:
                        yield new_pos

    def draw(self, win):

        for pos, data in self.board.items():
            x, y = pos_to_xy(pos)
            rect = (x, y, CARD_SIZE, CARD_SIZE)

            p, card_value = data

            if card_value == CARD_EMPTY:
                pygame.draw.rect(win, EMPTY, rect, 1)
            elif card_value == CARD_SELECTABLE:
                pygame.draw.rect(win, SELECTABLE, rect, 1)
            elif card_value == CARD_HOVER:
                pygame.draw.rect(win, EMPTY, rect)
            else:
                card_rect = pygame.draw.rect(win, EMPTY, rect, 1)
                font_obj = pygame.font.SysFont('Sans Serif', 40)
                text_surface_obj = font_obj.render(str(card_value), False, PLAYER_COLORS[p])
                text_rect_obj = text_surface_obj.get_rect()
                text_rect_obj.center = card_rect.center
                win.blit(text_surface_obj, text_rect_obj)


class Game:
    def __init__(self, n_player):
        self.n_player = n_player
        self.board = Board()
        self.players = [Player(i) for i in range(n_player)]
        self.current_player = self.players[0]
        self.start_game()

    def start_game(self):
        self.current_player.playing = True
        self.current_player.draw_card()

    def next_player(self):
        self.current_player.playing = False
        self.current_player = self.players[
            (self.current_player.p + 1) % self.n_player]
        self.current_player.playing = True
        self.current_player.draw_card()

    def draw(self, win):
        mouse_pos = pygame.mouse.get_pos()
        font_obj = pygame.font.SysFont('Sans Serif', 20)
        text = f"mouse: {mouse_pos}"
        text_surface_obj = font_obj.render(text, False, EMPTY)

        text_rect_obj = text_surface_obj.get_rect()
        text_rect_obj.topright = (WIDTH, 0)
        win.blit(text_surface_obj, text_rect_obj)

        for card_pos in self.board.set_selectable():
            card_xy = pos_to_xy(card_pos)
            rect = pygame.Rect(card_xy, (CARD_SIZE, CARD_SIZE))
            if rect.collidepoint(mouse_pos):
                p, value = self.board.board[card_pos]
                self.board.board[card_pos] = (p, CARD_HOVER)

        for player in self.players:
            player.draw(win)
        self.board.draw(win)



