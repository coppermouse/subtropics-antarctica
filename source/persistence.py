# -----------------------------------------
# source/persistence.py
# ------------------------------------------

from on_signal import on_signal


class Persistence:

    current = None

    def __init__(self):
        self.triggers = set()

    @on_signal(type='on setup', order=3)
    def on_setup(message):
        Persistence.current = Persistence()
