# -----------------------------------------
# source/tile_cursor.py
# ------------------------------------------

import pygame
from tile import Tile
from camera import Camera
from display import Display
from hero import Hero
from on_signal import on_signal
from consts import TILE_PIXEL_SIZE as TPS


class TileCursor:

    def get_current_tile_position():
        return Tile.get_tile_position_by_scene_position(
            Camera.unproject(pygame.mouse.get_pos()))

    @on_signal(type='on event', order=4)
    def on_event(message):
        event = message
        if event.type == pygame.MOUSEBUTTONDOWN:
            pass
            # implement events when click here...

    @on_signal(type='on draw', order=3)
    def draw(message):
        screen = Display.screen

        tp = TileCursor.get_current_tile_position()
        f = Camera.get_camera_zoom()/TPS
        r = pygame.Rect(0, 0, f*TPS, f*TPS)
        r.center = Camera.project(Tile.get_scene_position_by_tile_position(tp))

        pygame.draw.rect(screen, 'orange', r, 2)
        pygame.draw.rect(screen, '#ccddee', r.inflate((4, 4)), 1)
