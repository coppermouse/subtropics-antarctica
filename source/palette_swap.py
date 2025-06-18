# -----------------------------------------
# source/palette_swap.py
# ------------------------------------------

from common import range2d


def palette_swap(surface, palette_map):
    final = surface.copy()

    for xy in range2d(*final.get_size()):
        final.set_at(xy, palette_map.get(
            tuple(final.get_at(xy)), final.get_at(xy)))
    return final
