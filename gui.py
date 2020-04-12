import pygame
from network import Network
from player import (Player, Board, Game)


width = 500
height = 500
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Client")

client_number = 0


def redraw_window(win, game):
    win.fill((255,255,255))
    game.draw(win)
    pygame.display.update()


def main():
    run = True
    # n = Network()
    # p1 = n.get_p()

    game = Game(2)
    pygame.init()
    clock = pygame.time.Clock()

    while run:
        clock.tick(60)
        # p2 = n.send(p1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        # p1.move()
        redraw_window(win, game)

main()
