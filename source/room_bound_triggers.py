# -----------------------------------------
# source/room_bound_triggers.py
# ------------------------------------------

from on_signal import on_signal


class RoomBoundTriggers:

    triggers = set()

    @on_signal(type='on hero reach room', order=5)
    def on_hero_reach_room(message):
        from room import Room
        RoomBoundTriggers.triggers.clear()
