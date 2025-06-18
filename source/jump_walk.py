# -----------------------------------------
# source/jump_walk.py
# ------------------------------------------

import math
from jump import Jump
from future_signal import FutureSignal


class JumpWalk(Jump):

    def __init__(self, owner):
        self.owner = owner

    @property
    def cycle(self):

        # --- a long jump (such as those between rooms) has another special type of arc
        if round(self.owner.edge_walk.length) == 4:
            if self.owner.edge_walk.cycle < 0.25:
                return self.owner.edge_walk.cycle*2
            if self.owner.edge_walk.cycle < 0.75:
                return 0.5
            return (self.owner.edge_walk.cycle-0.75)*2+0.5
        # ---

        return self.owner.edge_walk.cycle

    @property
    def height(self):
        f = 1 if round(self.owner.edge_walk.length) == 2 else .8
        return min(math.sin(self.cycle*math.pi)*0.7, 0.65)*f

    def update(self, tick_delta):

        if round(self.owner.edge_walk.length) == 1:
            self.owner.edge_walk.update((0.085/2.5)*tick_delta)
        elif round(self.owner.edge_walk.length) == 4:
            self.owner.edge_walk.update(0.085*tick_delta)
        else:
            self.owner.edge_walk.update((0.085/1.35)*tick_delta)

        self.owner.refresh_jump_dest()

    def on_reach_edge_walk_to(self):
        self.landed = True
        recovery = 5 if round(self.owner.edge_walk.length) == 4 else 3
        FutureSignal.send_signal(recovery, 'on hero land recovered')
