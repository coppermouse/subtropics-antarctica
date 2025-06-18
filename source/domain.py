# -----------------------------------------
# source/domain.py
# ------------------------------------------

import pygame
from on_signal import on_signal
from domain_palette import DomainPalette
from resource_handler import ResourceHandler
from world import World


class Domain:

    @on_signal(type='on setup', order=90)
    def on_setup(message):
        Domain.map = ResourceHandler.images['world_data'].convert()
        Domain.color_domain = ResourceHandler.jsons['world_data_color_domain']

    def __init__(self, name):
        self.name = name

    @classmethod
    def get_domain_by_board_position(cls, board_position):
        pixel_position = [c + World.get_room_position_in_top_left_corner()[e]
                          for e, c in enumerate(board_position)]
        pixel_color = cls.map.get_at(pixel_position)

        for color, domain_name in cls.color_domain.items():
            if pixel_color.hex == color+'ff':  # adds alpha at end
                return Domain(domain_name)

        raise Exception(
            f"could not detect domain for board position: {board_position}")

    @property
    def palette(self):
        return DomainPalette(self.name)
