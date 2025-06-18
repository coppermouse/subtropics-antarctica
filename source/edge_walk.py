# -----------------------------------------
# source/edge_walk.py
# ------------------------------------------

import pygame


class EdgeWalk:

    def __init__(self, from_to, owner, lp=0):
        self._from, self.to = [pygame.math.Vector2(c) for c in from_to]
        self.lp = lp
        self.owner = owner
        self.done = False

    def reset(self, scene_position):
        self._from, self.to = [pygame.math.Vector2(c) for c in [
            scene_position]*2]
        self.lp = 0
        self.done = True

    @property
    def length(self):
        return self.to.distance_to(self._from)

    def get_scene_position(self):
        try:
            return self._from.lerp(self.to, self.lp / self.length)
        except ZeroDivisionError:
            return self.to

    @property
    def cycle(self):
        return self.lp / self.length

    def update(self, slp=0.085):
        if self.done:
            return
        self.lp += slp
        if self.lp >= self.length:
            rest = self.lp - self.length
            self.lp = self.length
            self.done = True
            self.owner.on_reach_edge_walk_to(rest=rest)
