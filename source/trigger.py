# -----------------------------------------
# source/trigger.py
# ------------------------------------------

from functools import lru_cache


class Trigger:

    triggers = set()

    @classmethod
    def is_ready(cls, tile_position):
        from tile import Tile
        tt = frozenset(Trigger.get_triggered_triggers())
        return cls.inner_is_ready(tile_position, tt)

    @lru_cache(maxsize=2**12)
    def inner_is_ready(tile_position, tt):
        from line import Line
        from tile import Tile
        for line in Line.get_all_lines_assosiated_with_associated_with_tile_position(
                tile_position):
            line = line.data
            if Tile.get_tile_position_by_scene_position(line[1]) == tile_position:
                if Tile.get_tile_position_by_scene_position(line[0]) in tt:
                    return True
        return False

    def get_triggered_triggers():
        from room_bound_triggers import RoomBoundTriggers
        from persistence import Persistence
        r = (
            RoomBoundTriggers.triggers | (Persistence.current.triggers
                                          if Persistence.current else set()))
        return r
