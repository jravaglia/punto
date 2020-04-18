import pygame
import random
import numpy as np

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


class Move:
    def __init__(self, p, xy_pos):
        self.p = p
        self.xy_pos = xy_pos


class Card:
    def __init__(self, x, y, width, p, value):
        self.x = x
        self.y = y
        self.width = width
        self.p = p
        self.value = value
        self.border = COLOR_EMPTY
        self.selectable = False

    def __repr__(self):
        return f"Card(p={self.p}, value={self.value})"

    @property
    def rect(self):
        return self.x, self.y, self.width, self.width

    def is_empty(self):
        return self.value < 1

    def update_pos(self, x, y):
        self.x = x
        self.y = y

    def draw(self, win):
        card_rect = pygame.Rect(self.rect)
        pygame.draw.rect(win, self.border, card_rect, 1)

        if self.value > 0:
            font_obj = pygame.font.SysFont('Sans Serif', 40)
            text_surface_obj = font_obj.render(str(self.value), False, PLAYER_COLORS[self.p])
            text_rect_obj = text_surface_obj.get_rect()
            text_rect_obj.center = card_rect.center
            win.blit(text_surface_obj, text_rect_obj)


class EmptyCard(Card):
    def __init__(self, x, y, width):
        Card.__init__(self, x, y, width, p=-1, value=-1)


class Player:
    def __init__(self, p):
        self.p = p
        self.color = PLAYER_COLORS[self.p]
        self.pos = PLAYER_POS[self.p]
        self.deck = self.make_deck()
        self.playing = False
        self.current_card = None
        self.name = f"Player {self.p}"

    def __repr__(self):
        return f"Player(p={self.p})"

    def make_deck(self):
        res = []
        for val in range(1, 10):
            # deck contain each value twice
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
            text = f"{self.name}: play {self.current_card.value}"
        else:
            text = f"{self.name}: waiting"
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

    def set_selectable(self, value, player_id):
        """Set to True the selectable attribute and
        set the color of the border of selectable cards.
        Return a list of selectable card"""
        res = []
        for pos in self.get_all_selectables(value):
            card = self.board[pos]
            card.selectable = True
            card.border = PLAYER_COLORS[player_id]
            res.append(pos)
        return res

    def unset_selectable(self):
        """Reset the selectable attribute and border color of all cards."""
        for card in self.board.values():
            card.selectable = False
            card.border = COLOR_EMPTY

    def get_all_selectables(self, value):
        """Return the grid coords of selectable cards"""
        res = set()
        if self.game_start:
            # first turn, select the middle card
            res.add((5, 5))
        else:
            for (x, y), card in self.board.items():
                if card.is_empty():
                    continue
                # lower card
                elif card.value < value:
                    res.add((x, y))
                # check all surrounding cards
                for pos in self.get_surrounding_pos(x, y):
                    surrounding_card = self.board[pos]
                    # lower card
                    if surrounding_card.value < value:
                        res.add(pos)
        return res

    def get_surrounding_pos(self, x, y):
        """Return the (x, y) grid coords of the surrounding cards.
        Let 0 be the card at grid coordinates (x, y), this method returns
        the grid coordinates of al the cards Xs surrounding 0.
        XXX
        X0X
        XXX
        """
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
    def __init__(self, player_id, players):
        self.player_id = player_id
        self.players = players
        self.board = Board()
        self.current_player = self.players[0]
        self.start_game()
        self.players[self.player_id].name = f"(You) {self.players[self.player_id].name}"

    @property
    def n_player(self):
        return len(self.players)

    @property
    def goal(self):
        if self.n_player == 2:
            return 5
        else:
            return 4

    def start_game(self):
        self.current_player.playing = True
        self.current_player.draw_card()
        self.board.set_selectable(self.current_player.current_card.value,
                                  self.current_player.p)

    def next_player(self):
        self.board.unset_selectable()
        self.current_player.playing = False
        self.current_player = self.players[
            (self.current_player.p + 1) % self.n_player]
        self.current_player.playing = True
        self.current_player.draw_card()
        self.board.set_selectable(self.current_player.current_card.value,
                                  self.current_player.p)

    def play_card(self, pos):
        new_card = self.current_player.current_card
        for card_pos in self.board.get_all_selectables(new_card.value):
            card_xy = pos_to_xy(card_pos)
            rect = pygame.Rect(card_xy, (CARD_SIZE, CARD_SIZE))
            if rect.collidepoint(pos):
                logging.info(card_pos)
                prev_card = self.board.board[card_pos]
                new_card.update_pos(prev_card.x, prev_card.y)
                self.board.board[card_pos] = new_card
                self.board.game_start = False
                self.next_player()
                return card_pos
        return False

    def is_winner(self):

        board = np.zeros((N_COL, N_ROW))
        board.fill(-1)
        for (x, y), card in self.board.board.items():
            board[x, y] = card.p

        # transpose board so the columns become the rows
        # thus we only need to check the rows
        for m in [board, board.T]:
        # check all rows
            for i in range(N_ROW):
                winner = self.is_winning_list(m[i])
                if winner >= 0:
                    return winner

        # flip the board so the antidiagonals become the diagonals
        # thus we only need to check the diagonals
        for m in [board, np.fliplr(board)]:
            # offset of all diagonals
            for offset in range(-N_ROW + 1, N_ROW):
                winner = self.is_winning_list(m.diagonal(offset))
                if winner >= 0:
                    return winner
        return -1

    def is_winning_list(self, l):
        if len(l) < self.goal:
            return -1

        prev_card = -1
        cumul = 0
        for card in l:
            if prev_card is None:
                prev_card = card
            if card == -1:
                cumul = 0
            elif prev_card == card:
                cumul += 1
            else: # cards differ
                prev_card = card
                cumul = 1
            if cumul == self.goal:
                return card
        return -1

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


