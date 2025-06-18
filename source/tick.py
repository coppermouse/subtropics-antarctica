# -----------------------------------------
# source/tick.py
# ------------------------------------------

from on_signal import on_signal
from on_signal import send_signal


class Tick():

    tick = 0

    speed_buffer = None

    @on_signal(type='on update', order=1)
    def on_update(message):
        delta = Tick.speed_buffer.pop(0) if Tick.speed_buffer else 1
        Tick.tick += delta
        send_signal('on tick', delta)
