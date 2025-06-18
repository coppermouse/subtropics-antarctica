# -----------------------------------------
# source/map.py
# ------------------------------------------

import os
import pygame
from on_signal import on_signal
from board import Board
from display import Display
from paths import user_folder
from room import Room
from room_static_surface import make_room_surface
from hero import Hero
from dicts import key_delta
from resource_handler import ResourceHandler
from common import diff2d
from world import World
from common import factor2d
from common import range2d
from tile import Tile
from frame import Frame

BOARD_PIXEL_SIZE_ON_MAP = 96

# NOTE/TODO: this class is not very clean, it has a lot of hard coded values


class Map:

    state = 0
    pan = pygame.math.Vector2()
    font = None

    @on_signal(type='on setup', order=97)
    def on_setup(message):
        cls = Map
        if not os.path.isfile(os.path.join(user_folder, 'cached_map.png')):
            cls.make_and_store_map_image()
        cls.load_map_image()

        if not pygame.font.get_init():
            pygame.font.init()

        cls.font = pygame.font.Font(None, 32)

    @on_signal(type='on update', order=-2)
    def on_update(message):
        cls = Map
        if not cls.is_open():
            return
        for k, v in key_delta.items():
            if pygame.key.get_pressed()[k]:
                cls.pan -= v*9
        return 'break'

    @on_signal(type='on draw', order=-4)
    def on_draw(message):
        from persistence import Persistence
        cls = Map
        if not cls.is_open():
            return

        bs = BOARD_PIXEL_SIZE_ON_MAP
        screen = Display.screen

        screen.blit(cls.static)

        # normal map
        if cls.state == 1:
            _map = cls.surface
            ss = screen.get_size()

            # --- draw map
            p = [
                -World.get_room_position_in_top_left_corner()[i]*bs-45+ss[i]//2+cls.pan[i]
                for i in range(2)]
            Display.screen.blit(_map, p)
            # ---

            # --- draw hero head
            if (Frame.frame//24) % 2:
                p = [
                    ss[i]//2+cls.pan[i] +
                    Hero.hero.scene_position[i]*6 - [15, 45][i]
                    for i in range(2)
                ]

                Display.screen.blit(ResourceHandler.images['cursor'], p)
            # ---

            # --- draw hover room cursor
            r = pygame.Rect((0, 0, bs, bs))
            m = Board.get_board_position_by_scene_position(
                cls.pan * -1/6 - (.5, .5))
            r.move_ip(cls.pan + [bs*m[i]+ss[i]//2-45 for i in range(2)])
            pygame.draw.rect(screen, 'cyan', r, 1)
            # ---

        # explored map view
        elif cls.state == 2:
            square_size = 32
            _map = pygame.Surface(
                factor2d(World.get_size_in_rooms(), square_size))
            _map.fill('darkblue')
            screen.blit(_map)

            explored_rooms = set()
            unexplored_rooms = set()
            for xy in range2d(*World.get_size_in_rooms()):
                if room := Board(
                        diff2d(xy, World.get_room_position_in_top_left_corner())).get_room():
                    explored = ('hero reach room',
                                room) in Persistence.current.triggers

                    (explored_rooms if explored else unexplored_rooms).add(room)

                    color = 'green' if explored else 'red'
                    r = pygame.Rect(0, 0, 32, 32).move(
                        factor2d(xy, square_size))
                    pygame.draw.rect(screen, color, r, 2)

            screen.blit(cls.font.render(
                f"Rooms explored: {len(explored_rooms)}",
                True, 'white'), (800, 400))
            screen.blit(cls.font.render(
                f"Rooms left to explore: {len(unexplored_rooms)}",
                True, 'white'), (800, 450))

        return 'break'

    @classmethod
    def is_open(cls):
        return cls.state > 0

    @on_signal(type='on event', order=-3)
    def on_event(message):
        cls = Map
        event = message

        if event.type == pygame.KEYDOWN:

            # teleport hero
            if event.key == pygame.K_j:
                if not cls.is_open():
                    return
                board = Board.get_board_by_scene_position(
                    cls.pan * -1/6 - (.5, .5))
                for tp in board.get_tile_positions():
                    if Tile(tp).tile_object == 'start-position':
                        Hero.hero.move_to_tile_position(tp)

            # switch between (and off) maps
            if event.key == pygame.K_TAB:
                cls.state = (cls.state + 1) % 3

                cls.pan = - Hero.hero.scene_position * 6 - (3, 3)

                # when switch to an "open map" state copy game display and blur it
                # to later have some background under map
                if cls.is_open():
                    static = Display.screen.copy()
                    grey = pygame.Surface(
                        Display.screen.get_size(), pygame.SRCALPHA)
                    grey.fill((40, 50, 60, 188))
                    static.blit(grey)
                    static = pygame.transform.box_blur(static, 2)
                    cls.static = static

    @classmethod
    def make_and_store_map_image(cls):
        bs = BOARD_PIXEL_SIZE_ON_MAP
        _map = pygame.Surface(factor2d(World.get_size_in_rooms(), bs))

        scale = (BOARD_PIXEL_SIZE_ON_MAP / 128)/16

        for room in Room.get_rooms():
            _map.blit(pygame.transform.scale_by(make_room_surface(room), scale),
                      [(c + World.get_room_position_in_top_left_corner()[e])*bs for e, c in enumerate(room.top_left_corner)])

        pygame.image.save(_map, os.path.join(user_folder, 'cached_map.png'))

    @classmethod
    def load_map_image(cls):
        cls.surface = pygame.image.load(os.path.join(
            user_folder, 'cached_map.png')).convert()
        cls.surface.set_colorkey((0, 0, 0))
