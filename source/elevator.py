# -----------------------------------------
# source/elevator.py
# ------------------------------------------

import pygame
from tick import Tick
from tile import Tile
from on_signal import on_signal
from resource_handler import ResourceHandler
from common import offset2d
from property_listener import PropertyListener
from property_listener import property_listener
from display import Display
from camera import Camera
from functools import lru_cache
from staticmethod_listener import staticmethod_listener
from room_surface import RoomSurface
from board import Board
from line import Line
from hidden_and_disabled import HiddenAndDisabled

# lower and upper height threshold for when to switch room
THRESHOLDS = (-290, 512)


class Elevator:

    tile_position_elevator = dict()

    def __init__(self, tile_position):
        from hero import Hero

        self.tile_position = tile_position
        self.reset()

        # if init when hero on it, it means that it starts moving towards the current floor, not away from it
        if tile_position == Hero.hero.tile_position:
            self.start_move_tick = Tick.tick
            self.start_height = {
                'top': THRESHOLDS[0], 'bottom': THRESHOLDS[1]}[self.get_level()]
            self.direction = {'top': 'up', 'bottom': 'down'}[self.get_level()]
            self.stop_at_next = True

        Elevator.tile_position_elevator[tile_position] = self
        PropertyListener.__init__(self)

    def reset(self):
        self.direction = None
        self.stop_at_next = False
        self.start_move_tick = None
        self.start_height = 0

    @property
    def room(self):
        return Board.get_board_by_tile_position(self.tile_position).get_room()

    @lru_cache(maxsize=2**4)
    def get_platform_surface(height):
        from hero import Hero
        final = pygame.Surface((128, 128*6), pygame.SRCALPHA)
        ResourceHandler.images['elevator'].set_colorkey((128,255,255))
        final.blit(ResourceHandler.images['elevator'], (-128, 128*4-height))

        # draw hero on platform if it has "landed"
        if height != 0:
            final.blit(Hero.inner_surface(
                ResourceHandler.images['idle'], 5, 3, 0, 128/72),
                # HACK: hardcoded values... it works good assuming images does not change
                (-64, -height+503)
            )

        return final

    def get_all_elevators_by_room(room):
        for tp in room.get_tile_positions():
            if tile_type := Tile.get_tile_type_by_tile_position(tp):
                if tile_type == 'elevator':
                    yield Elevator.aquire_elevator(tp)

    @classmethod
    def aquire_elevator(cls, tile_position):
        if elevator := cls.tile_position_elevator.get(tile_position):
            return elevator
        return Elevator(tile_position)

    @lru_cache
    def get_room_surface(height):
        s = pygame.Surface((128, 128*4))
        s.fill((128,255,255))
        s.set_colorkey((128,255,255))

        if height == 0:
            s.blit(ResourceHandler.images['elevator'], (-128, 128*2))

        elif height < 0:
            pygame.draw.rect(s, (9,)*3, (0, 128*3, 256, 256))
        else:  # height > 0
            ResourceHandler.images['elevator'].set_colorkey(None)
            for i in range(3):
                s.blit(ResourceHandler.images['elevator'], (0, 128*i))
            pygame.draw.rect(s, (128,255,255), (0, 0, 128, min(448-height, 384)))

        return s

    @property
    def height(self):
        sh = self.start_height

        if not self.start_move_tick:
            return sh

        f = (Tick.tick - self.start_move_tick)*7

        h = f * (1 if self.direction == 'up' else -1) + sh
        if self.stop_at_next:
            if self.direction == 'down' and h < 0:
                return 0
            if self.direction == 'up' and h > 0:
                return 0
        return h

    @property_listener("height")
    def on_height_change(self, _from, to):
        from hero import Hero

        # blit on room surface takes a performance so just do every so often.
        # also the effect looks just as good if it is every other 75 pixels in height
        if _from == 0 or abs(to-self.last_height_room_surface_blit) > 75:
            self.blit_on_room_surface()

        # hero has landed after taking the elevator
        if to == 0:
            self.blit_on_room_surface()
            Hero.hero.state.enable_back()

        # the elevator has left the room
        if to < THRESHOLDS[0] or to > THRESHOLDS[1]:
            line_index = 0 if to < 0 else 1

            for line in Line.get_all_lines_assosiated_with_associated_with_tile_position(
                    self.tile_position):
                Hero.hero.move_to_scene_position_snap_to_tile(
                    line.data[line_index])
                PropertyListener.property_listener_instances.discard(self)
                Hero.hero.last_dir = (0, 1)

    @on_signal(type='on hero reach tile position', order=11)
    def on_hero_reach_tile_position(message):
        from hero import Hero

        tile_position = message

        for elevator in Elevator.tile_position_elevator.values():
            if tile_position != elevator.tile_position:
                elevator.reset()

            if tile_position == elevator.tile_position:
                if elevator.start_move_tick:
                    continue

                # add a bit extra "time" to make sure it has left when being drawn
                elevator.start_move_tick = Tick.tick - 0.0001

                Hero.hero.state = HiddenAndDisabled(Hero.hero, Hero.hero.state)
                if elevator.get_level() == 'top':
                    elevator.direction = 'down'
                elif elevator.get_level() == 'bottom':
                    elevator.direction = 'up'
                else:
                    raise Exception(elevator.level)

    def blit_on_room_surface(self):
        self.last_height_room_surface_blit = self.height
        RoomSurface.blit_on_room_surface(
            self.room,
            Elevator.get_room_surface(self.height),
            offset2d(self.tile_position,  (0, -3)))

    @on_signal(type='on draw', order=11)
    def on_draw(message):

        screen = Display.screen
        for elevator in Elevator.tile_position_elevator.values():
            if elevator.height == 0:
                continue
            surface = pygame.transform.smoothscale_by(
                Elevator.get_platform_surface(elevator.height),
                Camera.get_camera_zoom()/128)

            sp = Tile.get_scene_position_by_tile_position(
                elevator.tile_position)
            screen.blit(
                surface,
                surface.get_rect(midbottom=Camera.project(sp + (0, .5))))

    @staticmethod_listener("Room.get_current_room")
    def on_change_current_room(_from, to):

        # clean up elevators from other room(s) when switching to a new room
        for elevator in Elevator.tile_position_elevator.copy().values():
            if elevator.room != to:
                elevator.remove()

    def remove(self):
        PropertyListener.property_listener_instances.discard(self)
        Elevator.tile_position_elevator.pop(self.tile_position)

    @lru_cache
    def get_level(self):

        # the level of  a elevator is based on the direction of the
        # line that connects it to the other elevato tile

        for line in Line.get_all_lines_assosiated_with_associated_with_tile_position(
                self.tile_position):
            if Tile.get_tile_position_by_scene_position(line.data[0]) == self.tile_position:
                return 'bottom'
            else:
                return 'top'
        raise Exception("No level could be detected")

    @on_signal(type='on room surface refresh', order=2)
    def on_room_surface_refresh(message):
        room = message
        for elevator in Elevator.get_all_elevators_by_room(room):
            elevator.blit_on_room_surface()
