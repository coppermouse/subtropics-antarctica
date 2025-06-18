# -----------------------------------------
# source/radio.py
# ------------------------------------------

import pygame
from on_signal import on_signal
from hero import Hero
from camera import Camera
from room import Room
from tile import Tile
from dicts import word_delta
from board import Board
from config import MUSIC

stations = {
    "crystalline":   [0,            4*60 + 18],  # 0:00
    "muddy york":    [4*60 + 23,            8*60 + 32],  # 4:23
    "ghost town":    [8*60 + 35,           11*60 + 50],  # 8:35
    "echo valley":   [15*60 + 18,           18*60 + 13],  # 15:18
    'ufo':           [35*60 + 36,           38*60 + 46],  # 35:36
    'babylonia':     [42*60 + 35,           45*60 + 35],  # 42:35
    "pirate ship":   [52*60 + 51,           57*60 + 2],  # 52:51
    "madness":       [1*3600 + 8*60 + 25,  1*3600 + 11*60 + 24],  # 1:08:25
    'infernoasia':   [1*3600 + 33*60 + 18,  1*3600 + 36*60 + 50],  # 1:33:18
    "swampifornia":  [1*3600 + 41*60 + 19,  1*3600 + 44*60 + 32],  # 1:41:19
    "bridge ruby":   [1*3600 + 57*60 + 42,  2*3600 + 1*60 + 22],  # 1:57:42
    "cream tunnel":  [2*3600 + 8*60 + 39,  2*3600 + 12*60 + 22],  # 2:08:39
}


class Radio:

    last_station_name = ""
    will_start_next_station_at = None

    @on_signal(type='on update', order=14)
    def on_update(message):
        room = Room.get_current_room()
        if room.domain.name == 'unknown':

            distance_vector = []

            for point in list(Radio.get_station_points()):
                distance = point.distance_to(Hero.hero.scene_position)
                if distance <= 6:
                    distance = 1 - (distance / 6)
                    distance_vector.append((distance, point))

                continue

            if distance_vector:
                distance_vector = max(distance_vector)
                pygame.mixer.music.set_volume(distance_vector[0])
                domain_name = Board.get_board_by_scene_position(
                    distance_vector[1]).get_room().domain.name
                Radio.set_station(domain_name)

            else:
                pygame.mixer.music.set_volume(0)

    def get_station_points():
        room = Room.get_current_room()
        for word, tps in room.get_edge_tile_positions().items():
            for tp in tps:
                if Tile.get_tile_type_by_tile_position(tp) != 'floor':
                    continue
                yield Tile.get_scene_position_by_tile_position(tp) + word_delta[word]

    @on_signal(type='on setup', order=13)
    def on_setup(message):
        if not MUSIC:
            return
        pygame.mixer.music.play()

    @on_signal(type='on hero reach room', order=14)
    def on_setup(message):
        if not MUSIC:
            return
        room = message
        pygame.mixer.music.set_volume(1)
        domain_name = room.domain.name
        if domain_name != 'unknown':
            Radio.set_station(domain_name)

    def set_station(station_name):

        if not MUSIC:
            return

        if Radio.last_station_name == station_name:
            return

        global_time = pygame.time.get_ticks()/1000

        # Since all stations share the same music file we need to refresh the cursor back to start of the station when it leaves the station
        # (this checks needs to be done regulary, maybe every second?)
        if station_name == "":
            if global_time > Radio.will_start_next_station_at:
                # will select the same station as before to refresh cursor
                station_name = Radio.last_station_name
            else:
                # still on the same track, nothing to do yet...
                return

        station = stations[station_name]

        station_play_length = station[1] - station[0]

        # --
        # Docs: The meaning of "pos", a float (or a number that can be converted to a float),
        # depends on the music format.
        # --
        # I happen to know set pos is based on seconds in my case
        pygame.mixer.music.set_pos(global_time %
                                   station_play_length + station[0])

        # store these values to be able to detect if next station and what station to restart to
        Radio.will_start_next_station_at = global_time + \
            station_play_length - (global_time % station_play_length)
        Radio.last_station_name = station_name
