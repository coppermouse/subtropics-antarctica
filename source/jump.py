# -----------------------------------------
# source/jump.py
# ------------------------------------------

import pygame
from resource_handler import ResourceHandler


class Jump:

    jump_buffer = False
    landed = False

    @property
    def image_offset(self):
        return [0.5, 0.24-self.height]

    @property
    def inner_surface_args(self):
        ri = ResourceHandler.images
        x = 0
        y = {
            (0, 1): 3,
            (0, -1): 7,
            (1, 0): 5,
            (-1, 0): 5,
        }[tuple(self.owner.direction)]

        if self.landed:
            return (ri['idle'], x, y, tuple(self.owner.direction) == (-1, 0))

        return (ri['jump'], x, y, tuple(self.owner.direction) == (-1, 0))

    def on_event(self, event):
        if event.key == pygame.K_j:
            self.jump_buffer = True
