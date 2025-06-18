# -----------------------------------------
# source/line.py
# ------------------------------------------

import pygame
from camera import Camera
from display import Display
from tile import Tile
from on_signal import on_signal
from functools import lru_cache
from resource_handler import ResourceHandler


class Line:

    def __init__(self, data):
        self.data = data[:2]
        self.type = 'J' if data[2] else 'K'

    @on_signal(type='on setup', order=78)
    def on_setup(message):
        cls = Line

        cls.lines = [
            Line((
                (line[0][0], line[0][1]),
                (line[1][0], line[1][1]),
                line[2]
            )) for line in ResourceHandler.jsons['level-data'][0]]

    @property
    def color(self):
        return {
            'J': 'red',
            'K': 'cyan'
        }[self.type]

    @lru_cache(maxsize=2**7)
    def get_all_lines_assosiated_with_associated_with_tile_position(tile_position):
        r = set()
        for line in Line.lines:
            for p in line.data:
                if Tile.get_tile_position_by_scene_position(p) == tile_position:
                    r.add(line)
        return frozenset(r)

    @on_signal(type='on draw', order=18)
    def on_draw(message):
        return
        for line in Line.lines:
            screen = Display.screen
            a, b = [pygame.math.Vector2(Camera.project(p)) for p in line.data]

            c = b + (b-a).rotate(90+45).normalize()*8
            d = b + (b-a).rotate(-90-45).normalize()*8
            color = line.color

            pygame.draw.line(screen, color, a, b,  1)
            pygame.draw.line(screen, color, b, c, 2)
            pygame.draw.line(screen, color, b, d, 2)
            pygame.draw.circle(screen, color, a, 7, 2)
