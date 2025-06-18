# -----------------------------------------
# source/domain_overlay.py
# ------------------------------------------

import pygame
from on_signal import on_signal
from display import Display
from frame import Frame
from tick import Tick
import math

# --- TODO: have a common domain.json object that we grab domain colors and names from
domain_fill_colors = {
    'ghost town': (50, 11, 23, 140),
    'echo valley': (20, 70, 63, 150),
    'cream tunnel': (30, 10, 120, 150),
    'muddy york': (10, 10, 20, 160),
    'swampifornia': (10, 10, 20, 160),
    'crystalline': (170, 50, 100, 120),
    'bridge ruby': (100, 110, 120, 170),
    'pirate ship': (100, 0, 0, 160),
    'madness': (40, 30, 80, 160),
    'ufo': (0, 0, 0, 200),
    'infernoasia': (0, 0, 0, 200),
    'babylonia': (0, 50, 10, 200),
}
# ---


def frame_to_position(frame):
    fake_frame = frame + 12
    if fake_frame / 60 > math.pi/2:
        fake_frame = fake_frame - math.pi*30
        if fake_frame < 26:
            return 0
        fake_frame -= 26
        return - 1 + math.sin(fake_frame/60+math.pi/2)
    return 1 - math.sin(fake_frame/60)


class DomainOverlay:

    start_fade = None
    font_entering = None
    font_domain = None

    @on_signal(type='on setup', order=213)
    def on_setup(message):
        pygame.font.init()
        screen = Display.screen
        DomainOverlay.font_entering, DomainOverlay.font_domain = [
            pygame.font.SysFont(
                "quicksandmedium", round(screen.get_size()[1]*f)) for f in [0.06, 0.14]]

    @on_signal(type='on hero reach room', order=213)
    def on_hero_reach_room(message):
        from persistence import Persistence
        room = message
        domain = room.domain
        if domain.name == 'unknown':
            return

        trigger = ('show-entering-domain', domain.name)

        if trigger in Persistence.current.triggers:
            return

        DomainOverlay.start_fade = Frame.frame
        DomainOverlay.domain = domain
        Tick.speed_buffer = [0]*200  # paus the game for 200 frames
        Persistence.current.triggers.add(trigger)

    @on_signal(type='on draw', order=213)
    def on_draw(message):
        cls = DomainOverlay
        if DomainOverlay.start_fade is None:
            return

        frame = Frame.frame-DomainOverlay.start_fade

        # hide overlay if it has been visible for more than x number of frames
        if frame > 187:
            return

        screen = Display.screen

        overlay = pygame.Surface(
            (screen.get_size()[0], screen.get_size()[1]*0.4), pygame.SRCALPHA)

        domain_name = DomainOverlay.domain.name
        overlay.fill(domain_fill_colors[domain_name])

        text_entering = cls.font_entering.render("Entering...", True, "white")
        text_domain = cls.font_domain.render(
            domain_name.upper(), True, "white")

        offset = screen.get_size()[0] * frame_to_position(frame)

        # --- blit domain
        dest = pygame.math.Vector2(
            text_domain.get_rect(
                center=overlay.get_rect().center)[:2]) + (
                    -offset, round(screen.get_size()[1]*0.04))
        overlay.blit(text_domain, dest)
        # ---

        # --- blit "entering..."
        dest = pygame.math.Vector2(
            text_entering.get_rect(
                center=overlay.get_rect().center)[:2]) - (
                    -offset, round(screen.get_size()[1]*0.09))
        overlay.blit(text_entering, dest)
        # ---

        screen.blit(overlay, (0, screen.get_size()[1]*0.135))
