# -----------------------------------------
# source/monster_spawner.py
# ------------------------------------------

from on_signal import on_signal
from jelly import Jelly
from tile import Tile
from persistence import Persistence


class MonsterSpawner:

    @on_signal(type='on hero reach room', order=1)
    def on_hero_reach_room(message):
        Jelly.jellies.clear()
        for tp in message.get_tile_positions():
            if Tile(tp).tile_object == 'jelly':
                if ('monster-defeated', tp) in Persistence.current.triggers:
                    continue
                Jelly(id=tp, scene_position=Tile.get_scene_position_by_tile_position(tp))

    def get_monster_tiles(room):
        for tp in room.get_tile_positions():
            if Tile(tp).tile_object == 'jelly':
                yield tp
