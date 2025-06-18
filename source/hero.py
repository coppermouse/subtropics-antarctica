# -----------------------------------------
# source/hero.py
# ------------------------------------------

import pygame
from camera import Camera
from display import Display
from room import Room
from tile import Tile
from common import offset2d
from common import factor2d
from edge_walk import EdgeWalk
from on_signal import send_signal
from on_signal import on_signal
from resource_handler import ResourceHandler
from jump_still import JumpStill
from jump_walk import JumpWalk
from ground import Ground
from dicts import key_delta
from functools import lru_cache
from config import SOUND
from common import round2d
from dicts import delta_word


class Hero():

    hero = None

    def __init__(self):
        Hero.hero = self
        scene_position = Tile.get_scene_position_by_tile_position((8, 20))
        self.edge_walk = EdgeWalk((scene_position, )*2, self)
        self.state = Ground(self)
        self.recent_directions = []
        self.last_dir = (0, -1)

    @property
    def direction(self):
        hold_directions = set()
        for k, v in key_delta.items():
            if pygame.key.get_pressed()[k]:
                hold_directions.add(tuple(v))

        recent_directions = [
            c for c in self.recent_directions if c in hold_directions]
        if not recent_directions:
            return self.last_dir

        self.last_dir = recent_directions[-1]

        return self.last_dir

    def get_surface(self, scale):
        return Hero.inner_surface(*(self.state.inner_surface_args + (scale,)))

    @lru_cache(maxsize=2**4)
    def inner_surface(surface, x, y, flip, scale):
        final = pygame.Surface((144, 144), pygame.SRCALPHA)
        final.blit(surface, (x*-144, y*-144))
        final = pygame.transform.flip(final, flip, False)
        return pygame.transform.smoothscale_by(final, scale)

    @property
    def scene_position(self):
        return self.edge_walk.get_scene_position()

    @property
    def tile_position(self):
        return Tile.get_tile_position_by_scene_position(self.scene_position)

    def draw(self):
        screen = Display.screen

        scale = Camera.get_camera_zoom()/72

        if not (hasattr(self.state, 'hide_shadow') and self.state.hide_shadow):
            shadow = pygame.transform.scale_by(
                ResourceHandler.images['shadow'], scale*1.1)
            screen.blit(shadow,
                        shadow.get_rect(center=Camera.project(self.scene_position + (0, 0.14))))

        surface = self.get_surface(scale)
        screen.blit(surface, round2d([c-surface.get_size()[e]*(1-self.state.image_offset[e])
                                      for e, c in enumerate(Camera.project(self.scene_position))]))

    def on_reach_edge_walk_to(self, rest):

        self.state.on_reach_edge_walk_to()

        if SOUND:
            ResourceHandler.sounds['foot'].play()
        ntp = Tile.get_tile_position_by_scene_position(self.edge_walk.to)
        send_signal('on hero reach tile position', ntp)

        # jump to next room
        if direction := Room.get_current_room().get_jump_to_next(self.tile_position):
            delta = factor2d(direction, 4)
            self.state = JumpWalk(self)
            self.edge_walk = EdgeWalk(
                (self.scene_position, offset2d(self.scene_position, delta)),
                self)

    def move_delta(self, delta, rest=0):
        from door import Door
        sp = self.scene_position
        sp = Tile.get_scene_position_by_tile_position(
            Tile.get_tile_position_by_scene_position(sp))
        nsp = offset2d(sp, delta)
        ntp = Tile.get_tile_position_by_scene_position(nsp)

        if Tile.get_tile_type_by_tile_position(ntp) in ('void', 'block', 'water'):
            return False

        if door := Door.tile_position_door.get(ntp):
            if not door.open:
                return False

        self.edge_walk = EdgeWalk((sp, nsp), self, lp=rest)

        return True

    @on_signal(type='on hero land recovered', order=2)
    def on_hero_land_recovered(message):
        from ground import Ground

        self = Hero.hero.state

        if pygame.key.get_pressed()[pygame.K_j] and self.jump_buffer:
            self.owner.try_jump()
        else:
            self.owner.state = Ground(self.owner)

    @on_signal(type='on draw', order=12)
    def on_draw(message):
        if not Hero.hero:
            return
        Hero.hero.draw()

    @on_signal(type='on setup', order=2)
    def on_setup(message):
        Hero.hero = Hero()

    @on_signal(type='on event', order=2)
    def on_event(message):
        event = message
        if event.type != pygame.KEYDOWN:
            return
        d = key_delta.get(event.key)
        if d:
            d = tuple(d)
            if d in Hero.hero.recent_directions:
                Hero.hero.recent_directions.remove(d)
            Hero.hero.recent_directions.append(d)

        Hero.hero.state.on_event(event)

    @on_signal(type='on tick', order=2)
    def on_update(message):
        from tunnel import Tunnel
        self = Hero.hero
        self.state.update(message)

        # TODO: have a general on hoverable type of object instead of calling the very
        #       specific tunnel
        if hover := Tunnel.tile_position_tunnel.get(self.tile_position):
            hover.when_hovered_by(self)

    def refresh_jump_dest(self):
        self.jump_dest = self.scene_position
        for key, delta in key_delta.items():
            if pygame.key.get_pressed()[key]:
                ntp = Tile.get_tile_position_by_scene_position(
                    self.scene_position + delta)
                if Tile.get_tile_type_by_tile_position(ntp) in ('block', 'floor'):
                    self.jump_dest = Tile.snap_scene_position_to_tile(
                        self.scene_position + delta)
                    return True

                jump_distance = 2
                dw = delta_word[tuple(delta)]
                for tp in Room.get_current_room().get_edge_tile_positions(margin=1)[dw]:
                    # detect on the edge of the room to make a bit longer jump to the next
                    # (this is not to be confused with the automatic long jump
                    # between rooms through an entrance)

                    if self.tile_position == tp:
                        jump_distance = 3
                        break
                self.jump_dest = self.scene_position + delta*jump_distance

    def try_jump(self):
        if not self.edge_walk.done:
            self.state = JumpStill(self)
            return

        if self.scene_position.distance_to(self.jump_dest) < 0.1:
            self.state = JumpStill(self)
        else:
            self.state = JumpWalk(self)
            self.edge_walk._from = self.scene_position.copy()
            self.edge_walk.lp = 0
            self.edge_walk.done = False
            self.edge_walk.to = self.jump_dest.copy()

    def move_to_scene_position_snap_to_tile(self, sp):
        sp = Tile.snap_scene_position_to_tile(sp)
        self.edge_walk.reset(sp)
        self.state.update(0)

    def move_to_tile_position(self, tp):
        sp = Tile.get_scene_position_by_tile_position(tp)
        self.edge_walk.reset(sp)
        self.state.update(0)
