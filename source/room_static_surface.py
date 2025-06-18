# -----------------------------------------
# source/room_static_surface.py
# ------------------------------------------

import pygame
from tile import Tile
from common import offset2d
from common import range2d
from common import factor2d

TILE_PIXEL_SIZE = 128


class RoomStaticSurface:

    current_room = None
    current_surface = None

    @classmethod
    def get_room_static_surface(cls, room):

        if room != cls.current_room:
            cls.current_surface = None

        cls.current_room = room

        if cls.current_surface:
            return cls.current_surface

        cls.current_surface = make_room_surface(room)

        return cls.current_surface


def make_surface(adjacent_visual_tile_types, palette):

    adjtt = adjacent_visual_tile_types
    ts = tile_size = TILE_PIXEL_SIZE

    tile = pygame.Surface((tile_size,)*2)
    (c_void, c_wall, c_floor, c_side_wall, c_side_wall_edge, c_floor_edge,
     c_darkwater, c_water) = palette.palette

    # --- floor
    if adjtt[(0, 0)] == 'floor':
        tile.fill(c_floor)

    # do not blit every tile type here, some are being drawn in their own classes
    elif adjtt[(0, 0)] in ('elevator', 'block', 'tunnel'):
        return pygame.Surface((1, 1))

    # water
    elif adjtt[(0, 0)] == 'water':
        tile.fill(c_water)
        s = 12
        if adjtt[(0, -1)] != 'water':

            for _dir, x, side in [((-1, 0), 0, 'left'), ((1, 0), ts-s, 'right')]:
                if adjtt[_dir] != 'water':
                    pygame.draw.rect(tile, c_floor, (x, 0, s, s))
                    pygame.draw.rect(tile, c_floor_edge, (x, s, s, s))
                    pygame.draw.rect(tile, c_darkwater, (x, s*2, s, s))
                    kwargs = {f"border_top_{side}_radius": s}
                    pygame.draw.rect(tile, c_floor_edge,
                                     (x, 0, s, s), **kwargs)
                    pygame.draw.rect(tile, c_darkwater, (x, s, s, s), **kwargs)
                    pygame.draw.rect(tile, c_water, (x, s*2, s, s), **kwargs)
                else:
                    pygame.draw.rect(tile, c_floor_edge, (x, 0, s, s))
                    pygame.draw.rect(tile, c_darkwater, (x, s, s, s))

            pygame.draw.rect(tile, c_floor_edge, (s, 0, ts-s*2, s))
            pygame.draw.rect(tile, c_darkwater, (s, s, ts-s*2, s))

        for dd, x, side in [(-1, 0, 'left'), (1, ts-s, 'right')]:
            if adjtt[(dd, 1)] == 'floor' and adjtt[(dd, 0)] != 'water' and adjtt[(0, 1)] != 'water':
                kwargs = {f"border_bottom_{side}_radius": s}
                pygame.draw.rect(tile, c_floor, (x, ts-s, s, s))
                pygame.draw.rect(tile, c_water, (x, ts-s, s, s), **kwargs)

    # front walls
    elif adjtt[(0, 0)] == 'front-wall':
        s = 12
        tile.fill(c_side_wall)
        pygame.draw.rect(tile, c_side_wall_edge, (0, ts-s, ts, s))

        for d, x in [(-1, 0), (1, ts-s)]:
            if adjtt[(d, 0)] not in ('void', 'front-wall'):
                pygame.draw.rect(tile, c_side_wall_edge, (x, 0, s, ts))

    # inside walls
    elif adjtt[(0, 0)] == 'void':  # wall

        tile.fill(c_void)
        s = 20
        radius = 19

        for _dir in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
            if adjtt[_dir] != 'void':
                v = 'top' if _dir[1] == 1 else 'bottom'
                h = 'left' if _dir[0] == 1 else 'right'
                kwargs = {f"border_{v}_{h}_radius": radius}
                pygame.draw.rect(tile, c_wall, (
                    *[(tile_size-s) * 1 if _dir[i] ==
                      1 else 0 for i in range(2)],
                    s, s), **kwargs)

        for d in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            if adjtt[d] != 'void':
                v = tile_size - s
                t = tile_size
                pygame.draw.rect(tile, c_wall, {
                    (0, -1): (0, 0, t, s),
                    (-1, 0): (0, 0, s, t),
                    (0, 1): (0, v, t, s),
                    (1, 0): (v, 0, s, t),
                }[d])

    # Borders
    for _dir in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        bw = border_width = 2
        border_color = (0, 0, 0, 180)  # black with some opacity
        if adjtt[_dir] in ('void', 'front-wall') and adjtt[(0, 0)] in ('floor', 'water'):
            border = pygame.Surface(
                (bw, ts)[::1 if _dir[0] != 0 else -1], pygame.SRCALPHA)
            border.fill(border_color)
            if _dir[0] != 0:
                tile.blit(border, (0 if _dir[0] == -1 else ts-bw, 0))
            else:
                tile.blit(border, (0, 0 if _dir[1] == -1 else ts-bw))

    return tile


def get_visual_tile_type_by_tile_position(tp):
    _type = Tile.get_tile_type_by_tile_position(tp)
    if _type == 'void':
        if Tile.get_tile_type_by_tile_position(offset2d(tp, (0, 1))) == 'void':
            return 'void'
        return 'front-wall'
    return _type


def make_room_surface(room):

    final = pygame.Surface(factor2d(room.size_in_tiles, TILE_PIXEL_SIZE))
    palette = room.domain.palette

    for tp in room.get_tile_positions():
        # TODO: it might be enough to only have 5 deltas,
        deltas = range2d((-1, 2), (-1, 2))
        #       corners might not be needed...

        adjtt = {delta: get_visual_tile_type_by_tile_position(offset2d(tp, delta))
                 for delta in deltas}

        surface = make_surface(adjtt,  palette)
        dest = factor2d(
            room.get_room_tile_position_by_tile_position(tp), TILE_PIXEL_SIZE)
        final.blit(surface, dest)

    return final
