# -----------------------------------------
# source/frame.py
# ------------------------------------------

from on_signal import on_signal


class Frame():

    frame = 0

    @on_signal(type='on update', order=-118)
    def on_update(message):
        Frame.frame += 1
