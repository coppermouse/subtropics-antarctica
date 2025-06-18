# -----------------------------------------
# source/block.py
# ------------------------------------------

import pygame
from on_signal import on_signal
from trigger import Trigger
from functools import lru_cache
from property_listener import property_listener
from staticmethod_listener import staticmethod_listener
from property_listener import PropertyListener
from board import Board
from resource_handler import ResourceHandler
from palette_swap import palette_swap


@lru_cache(maxsize=16)
def get_block(palette, _type):
    final = pygame.Surface((128, 128))
    offset = ['normal', 'foot', 'button-ready', 'button-pressed'].index(_type)
    final.blit(ResourceHandler.images['block'], (-128*offset, 0))
    palette_map = palette.get_map(0)
    final = palette_swap(final, palette_map)
    return final


class Block:

    tile_position_block = dict()

    def __init__(self, tile_position):
        self.tile_position = tile_position

        Block.tile_position_block[tile_position] = self

        self.palette = Board.get_board_by_tile_position(
            tile_position).domain.palette
        PropertyListener.__init__(self)

    @property
    def tile_type(self):
        return Block.get_block_type_by_tile_position(self.tile_position)

    @property_listener("tile_type")
    def on_tile_type_change(self, _from, to):
        self.blit_on_room_surface()

    @property
    def surface(self):
        return get_block(self.palette, self.tile_type)

    @classmethod
    def aquire_block(cls, tile_position):
        if block := cls.tile_position_block.get(tile_position):
            return block
        return Block(tile_position)

    def get_blocks_by_room(room):
        from tile import Tile
        for tp in room.get_tile_positions():
            if tile_type := Tile.get_tile_type_by_tile_position(tp):
                if tile_type == 'block':
                    yield Block.aquire_block(tp)

    @on_signal(type='on room surface refresh', order=1)
    def on_room_surface_refresh(message):
        room = message
        for block in Block.get_blocks_by_room(room):
            block.blit_on_room_surface()

    def blit_on_room_surface(self):
        from room_surface import RoomSurface
        RoomSurface.blit_on_room_surface(
            self.room, self.surface, self.tile_position)

    @property
    def room(self):
        from board import Board
        return Board.get_board_by_tile_position(self.tile_position).get_room()

    @staticmethod_listener("Room.get_current_room")
    def on_change_current_room(_from, to):
        # clean up blocks from other room(s) when switching to a new room
        for block in Block.tile_position_block.copy().values():
            if block.room != to:
                block.remove()

    @on_signal(type='on hero reach tile position', order=1)
    def on_hero_reach_tile_position(tile):
        from line import Line
        from tile import Tile
        from room_bound_triggers import RoomBoundTriggers
        from persistence import Persistence

        if Tile.get_tile_type_by_tile_position(tile) != 'block':
            return

        for line in Line.lines:
            # the line has a direction and (I think) a is start and b is end
            a, b = line.data
            tile_a = Tile.get_tile_position_by_scene_position(a)
            tile_b = Tile.get_tile_position_by_scene_position(b)
            if tile == tile_a:
                if line.type == 'J':
                    RoomBoundTriggers.triggers.add(tile_a)
                elif line.type == 'K':
                    Persistence.current.triggers.add(tile_a)

                if Tile.get_tile_type_by_tile_position(tile_b) == 'block':
                    block = Block.aquire_block(tile_b)
                    block.blit_on_room_surface()

    @classmethod
    def get_block_type_by_tile_position(cls, tile_position):
        pressed = Trigger.get_triggered_triggers()
        index = 0
        index += 1 if tile_position in pressed else 0
        index += 2 if Trigger.is_ready(tile_position) else 0
        return ['normal', 'foot', 'button-ready', 'button-pressed'][index]

    def remove(self):
        PropertyListener.property_listener_instances.discard(self)
        Block.tile_position_block.pop(self.tile_position)
