# -----------------------------------------
# source/future_signal.py
# ------------------------------------------

from tick import Tick
from on_signal import on_signal
from on_signal import send_signal


class FutureSignal:

    future_signals = set()

    @classmethod
    def send_signal(cls, future, _type, message=None):
        cls.future_signals.add((Tick.tick+future, _type, message))

    @on_signal(type='on update', order=22)
    def on_update(message):
        for future_signal in FutureSignal.future_signals.copy():
            future, _type, message = future_signal
            if Tick.tick >= future:
                FutureSignal.future_signals.discard(future_signal)
                send_signal(_type, message)
