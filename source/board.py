# -----------------------------------------
# source/board.py
# ------------------------------------------

from functools import lru_cache
from common import range2d


class Board:

    size_in_tiles = 16

    def __init__(self, position):
        self.position = position

    def get_room(self):
        return Board.get_room_by_board_position(self.position)

    @lru_cache(maxsize=2**12)
    def get_room_by_board_position(board_position):
        from room import Room
        for room in Room.get_rooms():
            if board_position in room.boards:
                return room

    @classmethod
    def get_board_by_scene_position(cls, scene_position):
        board_position = cls.get_board_position_by_scene_position(
            scene_position)
        return Board(board_position)

    @property
    def domain(self):
        from domain import Domain
        return Domain.get_domain_by_board_position(self.position)

    @classmethod
    def get_board_position_by_scene_position(cls, scene_position):
        sit = cls.size_in_tiles
        return tuple([(c+sit//2)//sit for c in scene_position])

    @classmethod
    def get_board_position_by_tile_position(cls, tile_position):
        sit = cls.size_in_tiles
        return tuple([c//sit for c in tile_position])

    @classmethod
    def get_board_by_tile_position(cls, tile_position):
        board_position = cls.get_board_position_by_tile_position(tile_position)
        return Board(board_position)

    def get_tile_positions(self):
        sit = Board.size_in_tiles
        tlc = self.position
        for rxy in range2d(sit, sit):
            xy = tuple(tlc[i]*sit+rxy[i] for i in range(2))
            yield xy
