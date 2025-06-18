# -----------------------------------------
# source/jelly.py
# ------------------------------------------

from on_signal import on_signal
import pygame
from camera import Camera
from display import Display
from tile import Tile
from tick import Tick
import random
from functools import lru_cache
from persistence import Persistence


class Jelly():

    jellies = set()

    @on_signal(type='on hero reach tile position', order=19)
    def on_hero_reach_tile_position(message):
        for jelly in Jelly.jellies.copy():
            if Tile.get_tile_position_by_scene_position(jelly.scene_position) == message:
                Jelly.jellies.discard(jelly)
                Persistence.current.triggers.add(
                    ('monster-defeated', jelly.id))

    @on_signal(type='on draw', order=1)
    def on_draw(message):
        for jelly in Jelly.jellies:
            jelly.draw()

    @lru_cache(maxsize=2**5)
    def get_surface(index):
        surface = pygame.image.load("res/jelly.png").convert()
        surface.set_colorkey((128,255,255))
        final = pygame.Surface((128, 128), pygame.SRCALPHA)
        final.blit(surface, (-128*index, 0))
        return final

    def __init__(self, id, scene_position):
        self.id = id
        self.anim_offset = random.randrange(20)
        Jelly.jellies.add(self)
        self.scene_position = scene_position

    def draw(self):
        screen = Display.screen
        p = Camera.project(self.scene_position)

        scaled_surface = pygame.transform.scale_by(
            Jelly.get_surface(((Tick.tick + self.anim_offset)//20) % 2 == 0),
            Camera.get_camera_zoom()/128)

        dest = pygame.math.Vector2(
            scaled_surface.get_rect(midbottom=p)[:2]).lerp(
                scaled_surface.get_rect(center=p)[:2], 0.8)
        screen.blit(scaled_surface, dest)
