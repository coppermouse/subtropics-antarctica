# -----------------------------------------
# source/hidden_and_disabled.py
# ------------------------------------------

import pygame


class HiddenAndDisabled:

    hide_shadow = True

    def __init__(self, owner, state_when_enabled_again):
        self.owner = owner
        self.state_when_enabled_again = state_when_enabled_again

    def enable_back(self):
        self.owner.state = self.state_when_enabled_again

    @property
    def inner_surface_args(self):
        hidden_pixel = pygame.Surface((1, 1), pygame.SRCALPHA)
        return (hidden_pixel, 0, 0, False)

    @property
    def image_offset(self):
        return [0, 0]

    def update(self, tick_delta):
        pass

    def on_event(self, event):
        pass
