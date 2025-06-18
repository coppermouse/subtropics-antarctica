# -----------------------------------------
# source/door.py
# ------------------------------------------

import pygame
from tile import Tile
from on_signal import on_signal
from functools import lru_cache
from board import Board
from trigger import Trigger
from palette_swap import palette_swap
from property_listener import property_listener
from property_listener import PropertyListener
from resource_handler import ResourceHandler
from tick import Tick
from staticmethod_listener import staticmethod_listener
from room_surface import RoomSurface
from common import offset2d
from consts import TILE_PIXEL_SIZE as TPS

BLAST_FRAMES = 14


@lru_cache(maxsize=16)
def get_door(p_index):
    from resource_handler import ResourceHandler
    p = ResourceHandler.images['palette0']
    door = ResourceHandler.images['door']
    palette_map = {tuple(p.get_at((x, 0))): p.get_at((x, p_index))
                   for x in range(p.get_size()[0])}
    return palette_swap(door, palette_map)


class Door:

    tile_position_door = dict()

    def __init__(self, tile_position):
        self.tile_position = tile_position
        self.back = pygame.Surface((TPS, TPS*2))

        x, y = self.room.get_room_tile_position_by_tile_position(
            self.tile_position)
        y -= 1
        self.back.blit(RoomSurface.get_room_static_surface(
            self.room), (-x*TPS, -y*TPS))
        Door.tile_position_door[tile_position] = self
        PropertyListener.__init__(self)
        self.open_at_tick = None
        self.force_open_until = None
        self.should_blast_open = True
        self.blit_on_room_surface()

    @property
    @lru_cache
    def data(self):
        return ResourceHandler.jsons['doors'][",".join(map(str, self.tile_position))]

    @property
    def room(self):
        return Board.get_board_by_tile_position(self.tile_position).get_room()

    def blit_on_room_surface(self):
        room = self.room
        y_offset = -1 if self.side in ('top', 'left', 'right') else 0
        RoomSurface.blit_on_room_surface(
            room, self.surface, offset2d(self.tile_position, (0, y_offset)))

    @property
    def side(self):
        # HACK: this is a bit ugly way to detect on what side a door is at.
        #       a better way is to use the tiles from the
        #       Room.get_edge_tile_positions method as reference
        l = self.room.get_room_tile_position_by_tile_position(
            self.tile_position)
        if l[0] / self.room.size_in_tiles[0] > 0.85:
            return 'right'
        if l[0] / self.room.size_in_tiles[0] < 0.15:
            return 'left'
        if l[1] / self.room.size_in_tiles[1] < 0.5:
            return 'top'
        return 'bottom'

    @on_signal(type='on hero reach room', order=12)
    def on_hero_reach_room(message):
        # remove doors from other rooms when enter a new one
        Door.tile_position_door = {
            k: v for k, v in
            Door.tile_position_door.items()
            if v.room == message
        }

    @property
    def open(self):
        from persistence import Persistence
        from monster_spawner import MonsterSpawner

        # door is open if...

        # ...all monsters been defeated (if that is the condition for being open by that door)
        if self.data.get("open-on-all-monsters-defeated"):
            l = set(MonsterSpawner.get_monster_tiles(self.room))
            u = {c[1] for c in Persistence.current.triggers if c[0]
                 == 'monster-defeated'}
            if u >= l:
                return True

        # ...is forced to be open
        if self.force_open_until and Tick.tick < self.force_open_until:
            return True

        # ...if its tile is been "ready" by trigger
        if Trigger.is_ready(self.tile_position):
            return True

        return False

    @property
    def open_animation(self):
        if self.open_at_tick is None:
            return None

        if not self.should_blast_open:
            return None

        r = (Tick.tick - self.open_at_tick) / ((1/64)*BLAST_FRAMES)

        if r >= 1:
            return None
        return r

    @property_listener("open")
    def on_open_change(self, _from, to):
        if to:
            self.open_at_tick = Tick.tick

        if self.should_blast_open and to:
            # during a blast open, slow down the game
            Tick.speed_buffer = [1/64 for _ in range(BLAST_FRAMES)]
        else:
            # this will make the game freeze a short time when door is being closed
            if not Tick.speed_buffer:
                Tick.speed_buffer = [1/128 for _ in range(6)]

        self.blit_on_room_surface()

    @property_listener("open_animation")
    def on_open_change(self, _from, to):
        self.blit_on_room_surface()

    @property
    def surface(self):
        final = pygame.Surface(self.back.get_size())
        final.blit(self.back)

        if self.open_animation is None:
            state = 'open' if self.open else 'closed'
        else:
            h = round(self.open_animation * BLAST_FRAMES)
            state = 'blast' if h % 4 < 2 else 'closed'

        if state == 'open':
            pass
        else:
            final.blit(get_door(
                ['closed', 'blast'].index(state)),
                (0, -24 if self.side == 'bottom' else 0))

        return final

    @staticmethod
    def get_doors_by_room(room):
        for tp in room.get_tile_positions():
            if tile_object := Tile.get_tile_object_by_tile_position(tp):
                if tile_object == 'door':
                    yield Door.aquire_door(tp)

    @staticmethod_listener("Room.get_current_room")
    def on_change_current_room(_from, to):
        from hero import Hero

        # --- will open doors that hero jumps through when enter a new room
        delta = Hero.hero.edge_walk._from - Hero.hero.edge_walk.to
        if delta.length() < 1:
            return
        direction = delta.normalize()

        # force all doors to be created if not already
        list(Door.get_doors_by_room(to))

        for i in range(round(delta.length())):
            door = Door.tile_position_door.get(Tile.get_tile_position_by_scene_position(
                Hero.hero.edge_walk._from.copy() - direction*i))
            if not door:
                continue

            if door.room != to:
                continue

            door.force_open_until = Tick.tick + 36
            door.blit_on_room_surface()
        # ---

    @classmethod
    def aquire_door(cls, tile_position):
        if door := cls.tile_position_door.get(tile_position):
            return door
        return Door(tile_position)

    def __str__(self):
        return f"Door {self.tile_position}"
