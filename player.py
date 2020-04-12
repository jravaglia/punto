import pygame
import random

import logging
logging.basicConfig(level=logging.DEBUG)

SPACE = 10
CARD_SIZE = 30
WIDTH = 500

CARD_EMPTY = -1
CARD_SELECTABLE = -2
CARD_HOVER = -3

COLOR_EMPTY = (200, 200, 200)
COLOR_SELECTABLE = (255, 0, 0)


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


class Card:
    def __init__(self, x, y, width, p, value):
        self.x = x
        self.y = y
        self.width = width
        self.p = p
        self.value = value
        # self.state = CARD_EMPTY
        self.selectable = False

    @property
    def rect(self):
        return self.x, self.y, self.width, self.width

    def is_empty(self):
        return self.value < 1

    def update_pos(self, x, y):
        self.x = x
        self.y = y

    def draw(self, win):

        if self.selectable:
            border_color = COLOR_SELECTABLE
        else:
            border_color = COLOR_EMPTY

        card_rect = pygame.Rect(self.rect)
        pygame.draw.rect(win, border_color, card_rect, 1)

        if self.value > 0:

            font_obj = pygame.font.SysFont('Sans Serif', 40)
            text_surface_obj = font_obj.render(str(self.value), False, PLAYER_COLORS[self.p])
            text_rect_obj = text_surface_obj.get_rect()
            text_rect_obj.center = card_rect.center
            win.blit(text_surface_obj, text_rect_obj)


class EmptyCard(Card):
    def __init__(self, x, y, width):
        Card.__init__(self, x, y, width, -1, -1)


class Player:
    def __init__(self, p):
        self.p = p
        self.color = PLAYER_COLORS[self.p]
        self.pos = PLAYER_POS[self.p]
        self.deck = self.make_deck()
        self.playing = False
        self.current_card = None

    def make_deck(self):
        res = []
        for val in range(1, 10):
            card = Card(0, 0, CARD_SIZE, self.p, val)
            res.append(card)
            card = Card(0, 0, CARD_SIZE, self.p, val)
            res.append(card)
        random.shuffle(res)
        return res

    def draw_card(self):
        self.current_card = self.deck.pop()
        return self.current_card

    def draw(self, win):
        font_obj = pygame.font.SysFont('Sans Serif', 40)
        if self.playing and self.current_card:
            text = f"Player {self.p}: play {self.current_card.value}"
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
                x, y = pos_to_xy((i, j))
                self.board[(i, j)] = EmptyCard(x, y, CARD_SIZE)

    def set_selectable(self, value):
        res = []
        for pos in self.get_all_selectables(value):
            card = self.board[pos]
            card.selectable = True
            res.append(pos)

        return res

    def unset_selectable(self):
        for card in self.board.values():
            card.selectable = False

    def get_all_selectables(self, value):
        res = set()
        if self.game_start:
            res.add((5, 5))
        else:
            for (x, y), card in self.board.items():
                if card.is_empty():
                    continue
                elif card.value < value:
                    res.add((x, y))
                for pos in self.get_surrounding_pos(x, y):
                    surrounding_card = self.board[pos]
                    if surrounding_card.value < value:
                        res.add(pos)
        return res

    def get_surrounding_pos(self, x, y):
        res = []
        for x_shift in [-1, 0, 1]:
            for y_shift in [-1, 0, 1]:
                if (x_shift, y_shift) == (0, 0):
                    continue
                new_pos = (x+x_shift, y+y_shift)
                if new_pos in self.board:
                    res.append(new_pos)
        return res

    def draw(self, win):

        for pos, card in self.board.items():
            card.draw(win)


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
        self.board.set_selectable(self.current_player.current_card.value)

    def next_player(self):
        self.board.unset_selectable()
        self.current_player.playing = False
        self.current_player = self.players[
            (self.current_player.p + 1) % self.n_player]
        self.current_player.playing = True
        self.current_player.draw_card()
        self.board.set_selectable(self.current_player.current_card.value)

    def update_board(self):
        # # highlight selectable cards on mouse hover
        # mouse_pos = pygame.mouse.get_pos()
        # for card_pos in self.board.set_selectable():
        #     card_xy = pos_to_xy(card_pos)
        #     rect = pygame.Rect(card_xy, (CARD_SIZE, CARD_SIZE))
        #     if rect.collidepoint(mouse_pos):
        #         p, value = self.board.board[card_pos]
        #         self.board.board[card_pos] = (p, CARD_HOVER)
        pass

    def play_card(self, pos):
        new_card = self.current_player.current_card
        for card_pos in self.board.get_all_selectables(new_card.value):
            card_xy = pos_to_xy(card_pos)
            rect = pygame.Rect(card_xy, (CARD_SIZE, CARD_SIZE))
            if rect.collidepoint(pos):
                prev_card = self.board.board[card_pos]
                new_card.update_pos(prev_card.x, prev_card.y)
                self.board.board[card_pos] = new_card
                self.board.game_start = False
                self.next_player()
                break

    def draw(self, win):
        mouse_pos = pygame.mouse.get_pos()
        font_obj = pygame.font.SysFont('Sans Serif', 20)
        text = f"mouse: {mouse_pos}"
        text_surface_obj = font_obj.render(text, False, COLOR_EMPTY)

        text_rect_obj = text_surface_obj.get_rect()
        text_rect_obj.topright = (WIDTH, 0)
        win.blit(text_surface_obj, text_rect_obj)

        for player in self.players:
            player.draw(win)
        self.board.draw(win)


