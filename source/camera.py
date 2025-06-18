# -----------------------------------------
# source/camera.py
# ------------------------------------------

import pygame
from common import factor2d
from display import Display
from functools import lru_cache

PREFERRED_VIEW = pygame.FRect(0, 0, 23, 23)


class Camera:

    @classmethod
    def get_camera_zoom(cls):
        screen_size = Display.screen_size
        return min([screen_size[i]/Camera.get_rect()[i+2] for i in range(2)])

    def get_rect():
        from hero import Hero
        p = Hero.hero.scene_position.copy()
        return Camera.inner_get_rect(tuple(p))

    @lru_cache(maxsize=2**7)
    def inner_get_rect(p):
        from room import Room
        r = PREFERRED_VIEW.copy()  # start base the rect on preferred view
        r.center = p
        room = Room.get_current_room().get_rect()

        # fit rect into room rect
        for i in [2, 3]:
            r[i] = min(r[i], room[i])

        # make sure rect does not leave room rect
        for i in [0, 1]:
            r[i] = max(r[i], room[i])
            m = (r[i] + r[i+2]) - (room[i]+room[i+2])
            if m > 0:
                r[i] -= m

        return r

    @classmethod
    def unproject(cls, p):
        ss = Display.screen_size
        c = Camera.get_rect().center
        f = cls.get_camera_zoom()
        sshs = [c/2 for c in ss]
        return [p[i]/f-sshs[i]/f+c[i] for i in range(2)]

    @classmethod
    def project_rect(cls, rect):
        return pygame.Rect(
            *cls.project(rect[:2]),
            *factor2d(rect[2:], cls.get_final_camera_zoom())
        )

    @classmethod
    def project(cls, p):
        ss = Display.screen_size
        c = Camera.get_rect().center
        f = cls.get_camera_zoom()
        sshs = [c/2 for c in ss]
        return [(p[i]-c[i])*f+sshs[i] for i in range(2)]
