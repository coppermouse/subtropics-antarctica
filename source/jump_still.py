# -----------------------------------------
# source/jump_still.py
# ------------------------------------------

import math
from jump import Jump
from tick import Tick


class JumpStill(Jump):

    def update(self, tick_delta):
        from ground import Ground
        if self.cycle >= 1:
            self.landed = True
        if self.cycle >= 1.1:  # require hero to wait after landed before moving again
            self.owner.state = Ground(self.owner)

    def __init__(self, owner):
        self.owner = owner
        self.start_jump_tick = Tick.tick

    @property
    def cycle(self):
        return (Tick.tick - self.start_jump_tick)/30

    @property
    def height(self):
        c = self.cycle
        if c > 1:
            c = 1
        return min(math.sin(c*math.pi)*0.7, 0.63)
