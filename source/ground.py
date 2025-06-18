# -----------------------------------------
# source/ground.py
# ------------------------------------------

import pygame
from tick import Tick
from resource_handler import ResourceHandler
from tile import Tile
from dicts import key_delta
from dicts import delta_word


class Ground:

    def __init__(self, owner):
        self.owner = owner

    @property
    def image_offset(self):
        return [0.5, 1-0.76]

    def update(self, tick):
        self.owner.edge_walk.update(0.085*tick)
        self = self.owner
        self.refresh_jump_dest()

        ntp = Tile.get_tile_position_by_scene_position(self.edge_walk.to)
        if Tile.get_tile_type_by_tile_position(ntp) == 'block':
            return

        if not self.edge_walk.done:
            return
        self.refresh_jump_dest()
        for key, delta in key_delta.items():
            if pygame.key.get_pressed()[key]:
                if not self.move_delta(delta):
                    self.refresh_jump_dest()

    @property
    def inner_surface_args(self):

        owner = self.owner

        # --- to make hero hidden while in tunnel
        if (owner.edge_walk._from.distance_to(owner.edge_walk.to) > 1
                and not owner.edge_walk.done):
            hidden_pixel = pygame.Surface((1, 1), pygame.SRCALPHA)
            return (hidden_pixel, 0, 0, False)
        # ---

        x, y = 0, 3
        y = {(0, 1): 3, (0, -1): 7, (1, 0): 5,
             (-1, 0): 5}[tuple(owner.direction)]

        flip = self.owner.direction == (-1, 0)

        x, img = (((Tick.tick//14.5) % 12, 'idle')
                  if owner.edge_walk.done else ((Tick.tick//3.3) % 8, 'walk'))

        return (ResourceHandler.images[img], x, y, flip)

    def on_event(self, event):
        if event.key == pygame.K_j:
            self.owner.try_jump()

    def on_reach_edge_walk_to(self):
        pass
