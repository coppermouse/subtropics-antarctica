# -----------------------------------------
# source/room.py
# ------------------------------------------

import pygame
from functools import lru_cache
from display import Display
from camera import Camera
from on_signal import on_signal
from on_signal import send_signal
from common import offset2d
from common import diff2d
from board import Board
from common import factor2d
from common import range2d
from tile import Tile
from room_surface import RoomSurface
from collections import defaultdict
from world import World
from resource_handler import ResourceHandler
from board import Board

BSIT = Board.size_in_tiles


class Room():
    """
        A Room either have one or many Boards. In other words a Room with many Boards 
        is a bigger Room.
    """

    last_current_room_on_hero_reach_tile_position = None

    @lru_cache
    def get_rooms():
        return frozenset(Room.inner_get_rooms())

    def inner_get_rooms():

        world_size = World.get_size_in_rooms()
        pixel_offset_to_room_origin = World.get_room_position_in_top_left_corner()
        world_data_groups_by_color = pygame.Surface(world_size)
        world_data_groups_by_color.blit(
            ResourceHandler.images['world_data'].convert(), (-world_size[0], 0))

        color_groups = defaultdict(set)

        for xy in range2d(*world_data_groups_by_color.get_size()):

            # black pixel = no board
            if world_data_groups_by_color.get_at(xy).hex == '#000000ff':
                continue

            # white pixel = single board room
            if world_data_groups_by_color.get_at(xy).hex == '#ffffffff':
                xy = diff2d(xy, pixel_offset_to_room_origin)
                yield Room(frozenset({xy}))

            # any other color = rooms with many boards
            else:
                color_groups[world_data_groups_by_color.get_at(xy).hex].add(
                    diff2d(xy, pixel_offset_to_room_origin))

        for color_group in color_groups.values():
            yield Room(frozenset(color_group))

    @staticmethod
    def get_current_room():
        from hero import Hero
        hero = Hero.hero
        return Board.get_board_by_scene_position(hero.scene_position).get_room()

    @property
    def domain(self):
        from domain import Domain
        return Domain.get_domain_by_board_position(self.top_left_corner)

    def __init__(self, boards):
        self.boards = boards
        self.area = tuple(
            max([c[i] for c in boards]) - min([c[i] for c in boards]) + 1 for i in range(2))
        self.top_left_corner = tuple(
            min([c[i] for c in boards]) for i in range(2))

    @property
    def size_in_tiles(self):
        return factor2d(self.area, BSIT)

    def get_room_tile_position_by_tile_position(self, tile_position):
        c = tile_position
        return [c[i]-self.position[i]*BSIT for i in range(2)]

    @property
    def position(self):
        return self.top_left_corner

    def get_jump_to_next(self, xy):
        gttbtp = Tile.get_tile_type_by_tile_position
        sit = Board.size_in_tiles
        tlc, area = self.top_left_corner, self.area

        if gttbtp(xy) != 'floor':
            return False

        # TODO: I think we could use get_edge_tile_positions here to find all
        #       the edge tiles.

        for d, f in [(0, -1),  (0, 1), (1, -1), (1, 1)]:
            s = 1 if d == 0 else -1
            if (xy[d] == tlc[d]*sit-f + (area[d]*sit-1)*(f == 1)
                    and gttbtp(offset2d(xy, (f, 0)[::s])) == 'floor'):
                return (f, 0)[::s]
        return False

    def get_tile_positions(self):
        sit = Board.size_in_tiles
        tlc = self.top_left_corner
        for rxy in range2d(*factor2d(self.area, sit)):
            xy = tuple(tlc[i]*sit+rxy[i] for i in range(2))
            yield xy

    def get_edge_tile_positions(self, margin=0):
        sit = Board.size_in_tiles
        tlc = self.top_left_corner
        r = {'left': set(), 'right': set(), 'up': set(), 'down': set()}
        d = factor2d(self.area, sit)
        for rxy in range2d(*d):
            xy = tuple(tlc[i]*sit+rxy[i] for i in range(2))
            for i in range(2):
                if rxy[i] == margin:
                    r['left' if i == 0 else 'up'].add(xy)
                if rxy[i] == d[i]-1-margin:
                    r['right' if i == 0 else 'down'].add(xy)
        return r

    def crop_side(self):
        width, height = self.size_in_tiles
        d = dict()
        for i in range(4):
            stop = False
            l = None
            for a in range(width if i < 2 else height):
                m = a
                if i % 2 == 1:
                    a = (width if i < 2 else height) - a-1
                for b in range(height if i < 2 else width):
                    p = tuple(
                        self.position[q]*BSIT+[a, b][::1 if i < 2 else -1][q] for q in range(2))
                    if Tile.get_tile_type_by_tile_position(p) != 'void':
                        l = m
                        break
                if l is not None:
                    break
            d[i] = l

            d[i] -= 1 if i != 2 else 2
            if d[i] < 0:
                d[i] = 0

        return {'left': d[0], 'top': d[2], 'right': d[1], 'bottom': d[3]}

    def get_rect(self):
        p = self.position
        crop = self.crop_side()
        width, height = self.size_in_tiles
        width -= (crop['left'] + crop['right'])
        height -= (crop['top'] + crop['bottom'])
        return pygame.FRect(
            -BSIT//2+p[0]*BSIT+crop['left'],
            -BSIT//2+p[1]*BSIT+crop['top'],
            width, height)

    def scale(self, factor):
        size = self.size_in_tiles
        return RoomSurface.get_room_dynamic_surface_scaled(self, factor2d(size, factor))

    def draw(self):
        cs = self.crop_side()
        Display.screen.fill(self.domain.palette.palette[0])
        Display.screen.blit(self.scale(Camera.get_camera_zoom()), Camera.project(
            (self.get_rect()[0] - cs['left'], self.get_rect()[1] - cs['top'])))

    def get_center(self):
        return self.get_rect().center

    @on_signal(type='on draw', order=-1)
    def on_draw(message):
        Room.get_current_room().draw()

    @on_signal(type='on hero reach tile position', order=-1)
    def on_hero_reach_tile_position(message):
        from persistence import Persistence
        cls = Room
        room = cls.get_current_room()
        if cls.last_current_room_on_hero_reach_tile_position != cls.get_current_room():
            Persistence.current.triggers.add(('hero reach room', room))
            send_signal('on hero reach room', room)

        cls.last_current_room_on_hero_reach_tile_position = cls.get_current_room()

    def __hash__(self):
        return hash(self.top_left_corner)

    def __eq__(self, other):
        if other is None:
            return False
        return self.top_left_corner == other.top_left_corner

    def __str__(self):
        return f"Room {self.position}"
