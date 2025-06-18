# -----------------------------------------
# source/room_surface.py
# ------------------------------------------

import pygame
from on_signal import send_signal
from common import factor2d
from room_static_surface import RoomStaticSurface
from consts import TILE_PIXEL_SIZE as TPS


class RoomSurface:

    current_room = None
    current_dynamic_surface = None
    current_static_surface = None
    current_dynamic_scaled_surface = None

    @classmethod
    def blit_on_room_surface(cls, room, surface, tile_position):
        if not cls.current_room or (cls.current_room != room):
            return

        pixel_position = factor2d(
            cls.current_room.get_room_tile_position_by_tile_position(tile_position), TPS)
        cls.current_dynamic_surface.blit(
            cls.current_static_surface,
            pixel_position, surface.get_rect(topleft=pixel_position))

        # clear scaled surface so it also updates when fetched
        cls.current_dynamic_scaled_surface = None

        RoomSurface.current_dynamic_surface.blit(surface, pixel_position)

    @classmethod
    def refresh(cls, room):
        if room == cls.current_room:
            return

        cls.current_dynamic_scaled_surface = None
        cls.current_room = room

        cls.current_static_surface = RoomStaticSurface.get_room_static_surface(
            room)
        cls.current_dynamic_surface = cls.current_static_surface.copy()

        send_signal("on room surface refresh", room)

    @classmethod
    def get_room_static_surface(cls, room):
        cls.refresh(room)
        return cls.current_static_surface

    @classmethod
    def get_room_dynamic_surface(cls, room):
        cls.refresh(room)
        return cls.current_dynamic_surface

    @classmethod
    def get_room_dynamic_surface_scaled(cls, room, factor):
        cls.refresh(room)
        if not cls.current_dynamic_scaled_surface:
            cls.current_dynamic_scaled_surface = pygame.transform.scale(
                cls.current_dynamic_surface, factor)
        return cls.current_dynamic_scaled_surface
