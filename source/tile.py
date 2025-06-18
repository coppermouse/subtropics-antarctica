# -----------------------------------------
# source/tile.py
# ------------------------------------------

import pygame
from on_signal import on_signal
from trigger import Trigger
from resource_handler import ResourceHandler

object_index_to_str = {
    5: 'door',
    15: 'start-position',
    18: 'jelly',
}


class Tile:

    data_tile_type = dict()
    data_object = dict()

    def __init__(self, position):
        self.position = position

    @on_signal(type='on setup', order=79)
    def on_setup(message):
        cls = Tile
        for where, value in ResourceHandler.jsons['level-data'][1].items():
            where = eval(where)
            [cls.data_tile_type, cls.data_object][where[1]][where[0]] = value

    @property
    def tile_object(self):
        cls = Tile
        if tile_object_index := cls.data_object.get((self.position)):
            return object_index_to_str[tile_object_index]

        return None

    @staticmethod
    def get_tile_type_by_scene_position(p):
        p = Tile.get_tile_position_by_scene_position(p)
        return Tile.get_tile_type_by_tile_position(p)

    @staticmethod
    def get_tile_object_by_tile_position(p):
        cls = Tile
        data_object = cls.data_object
        if p in data_object:
            return object_index_to_str[data_object[p]]
        return None

    @staticmethod
    def get_tile_type_by_tile_position(p):
        cls = Tile
        data = cls.data_tile_type
        index = data[p]+1 if p in data else 0
        try:
            t = ['void', 'floor', 'water', 'block', 'elevator', 'tunnel'][index]
            if t == 'water':
                if Trigger.is_ready(p):
                    return 'block'
            return t
        except IndexError as e:
            raise e

    @staticmethod
    def get_tile_position_by_scene_position(p):
        return tuple(int(c//1+8) for c in p)

    @staticmethod
    def get_scene_position_by_tile_position(p):
        return pygame.math.Vector2(tuple(c-7.5 for c in p))

    def snap_scene_position_to_tile(sp):
        return pygame.math.Vector2(Tile.get_scene_position_by_tile_position(
            Tile.get_tile_position_by_scene_position(sp)))
