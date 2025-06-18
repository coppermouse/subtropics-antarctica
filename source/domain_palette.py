# -----------------------------------------
# source/domain_palette.py
# ------------------------------------------

import pygame
from on_signal import on_signal
from resource_handler import ResourceHandler


class DomainPalette:

    def __init__(self, name):

        # --- TODO: move to a json object
        index = {
            'unknown': 3,
            'echo valley': 0,
            'ghost town': 1,
            'swampifornia': 2,
            'cream tunnel': 4,
            'muddy york': 5,
            'pirate ship': 6,
            'crystalline': 7,
            'babylonia': 8,
            'bridge ruby': 9,
            'madness': 10,
            'infernoasia': 11,
            'ufo': 12,
        }[name]
        # ---

        self.index = index

        y = index
        self.palette = [
            pygame.Color(
                ResourceHandler.images['domain_palette'].get_at((x, y)))
            for x in range(8)
        ]

    def get_map(self, from_index):
        palette = ResourceHandler.images['domain_palette']
        palette_map = dict()
        for i in range(palette.get_size()[0]):
            palette_map[tuple(palette.get_at((i, from_index)))] = tuple(
                palette.get_at((i, self.index)))
        return palette_map

    def __eq__(self, other):
        return self.index == other.index

    def __hash__(self):
        return hash(self.index)
