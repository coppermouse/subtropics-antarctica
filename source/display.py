# -----------------------------------------
# source/display.py
# ------------------------------------------

import pygame
from on_signal import on_signal
from config import RESOLUTION

SHOW_CENTER_LINES = False  # <-- good for debug


class Display:
    screen_size = RESOLUTION

    @on_signal(type='on setup', order=-19)
    def on_setup(message):
        Display.screen = pygame.display.set_mode(
            Display.screen_size, pygame.NOFRAME, vsync=True)

    @on_signal(type='on draw', order=99)
    def on_draw(message):
        if SHOW_CENTER_LINES:
            screen = Display.screen
            pygame.draw.rect(
                screen, 'magenta', (screen.get_size()[0]//2-1, 0, 2, screen.get_size()[1]))
            pygame.draw.rect(
                screen, 'magenta', (0, screen.get_size()[1]//2-1, screen.get_size()[0], 2))
