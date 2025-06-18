# -----------------------------------------
# source/tunnel.py
# ------------------------------------------

import pygame
from tile import Tile
from on_signal import on_signal
from room_surface import RoomSurface
from common import round2d
from board import Board
from dicts import key_delta
from dicts import directions
from functools import lru_cache
from consts import TILE_PIXEL_SIZE as TPS


class Tunnel:

    tile_position_tunnel = dict()

    def __init__(self, tile_position):
        self.tile_position = tile_position
        Tunnel.tile_position_tunnel[tile_position] = self

    @property
    def room(self):
        return Board.get_board_by_tile_position(self.tile_position).get_room()

    def when_hovered_by(self, other):
        for k, v in key_delta.items():
            if v != self.direction:
                continue

            if pygame.key.get_pressed()[k] and other.edge_walk.done:
                other.edge_walk._from = other.edge_walk.to.copy()
                other.edge_walk.done = False
                other.edge_walk.lp = 0
                other.edge_walk.to += v*self.length

    @classmethod
    def get_tunnel_surface(cls, palette, direction):
        floor_color = palette.palette[2]
        tile = pygame.Surface((TPS,)*2)
        tile.fill(floor_color)

        # TODO: have these colors in palette
        pygame.draw.polygon(
            tile, '#141414', [(6 if i % 2 == 0 else TPS/4+6, i*(TPS/4)) for i in range(5)])
        pygame.draw.polygon(
            tile, '#2a2928', [(0 if i % 2 == 0 else TPS/4, i*(TPS/4)) for i in range(5)])
        pygame.draw.rect(tile, '#2a2928', (0, 0, 6, TPS))

        return pygame.transform.rotate(
            tile,
            [(-1, 0), (0, 1), (1, 0), (0, -1)].index(direction)*90
        )

    @property
    def direction(self):
        return self.get_direction_and_length()[0]

    @property
    def length(self):
        return self.get_direction_and_length()[1]

    @lru_cache(maxsize=2**7)
    def get_direction_and_length(self):
        tp = self.tile_position
        search_length = 24  # try find exit for 24 tiles then give up
        for delta in range(1, search_length):
            for direction in directions:
                n = pygame.math.Vector2(
                    tp) + pygame.math.Vector2(direction) * delta
                if Tile.get_tile_type_by_tile_position(round2d(n)) == 'tunnel':
                    return direction, delta
        raise Exception("no exit found, try increase search length if your are "
                        "sure there should be an exit connected to the tunnel")

    def blit_on_room_surface(self):
        RoomSurface.blit_on_room_surface(
            self.room,
            Tunnel.get_tunnel_surface(
                self.room.domain.palette, self.direction),
            self.tile_position)

    @on_signal(type='on room surface refresh', order=4)
    def on_room_surface_refresh(message):
        room = message
        for tunnel in Tunnel.get_all_tunnels_by_room(room):
            tunnel.blit_on_room_surface()

    def get_all_tunnels_by_room(room):
        for tp in room.get_tile_positions():
            if tile_type := Tile.get_tile_type_by_tile_position(tp):
                if tile_type == 'tunnel':
                    yield Tunnel.aquire_tunnel(tp)

    @classmethod
    def aquire_tunnel(cls, tile_position):
        if tunnel := cls.tile_position_tunnel.get(tile_position):
            return tunnel
        return Tunnel(tile_position)
