# -----------------------------------------
# source/dicts.py
# ------------------------------------------

import pygame

key_delta = {
    pygame.K_w: (0, -1),
    pygame.K_s: (0, 1),
    pygame.K_a: (-1, 0),
    pygame.K_d: (1, 0),
}
key_delta = {k: pygame.math.Vector2(v) for k, v in key_delta.items()}

word_delta = {
    'up': (0, -1),
    'down': (0, 1),
    'left': (-1, 0),
    'right': (1, 0),
}
delta_word = {v: k for k, v in word_delta.items()}
word_delta = {k: pygame.math.Vector2(v) for k, v in word_delta.items()}

directions = [pygame.math.Vector2(v)
              for v in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
