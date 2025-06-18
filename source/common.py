# -----------------------------------------
# source/common.py
# ------------------------------------------

from functools import lru_cache


def offset2d(a, b):
    return a[0] + b[0], a[1] + b[1]


def diff2d(a, b):
    return a[0] - b[0], a[1] - b[1]


@lru_cache(maxsize=32)
def range2d(stops_x, stops_y):
    # TODO: this could need to clean up. it has too many steps
    stops = (stops_x, stops_y)
    r = list()
    for y in range(*((stops[1],) if type(stops[1]) == int else stops[1])):
        for x in range(*((stops[0],) if type(stops[0]) == int else stops[0])):
            r.append((x, y))
    return r


def factor2d(item, factor):
    return item[0] * factor, item[1] * factor


def round2d(a):
    return round(a[0]), round(a[1])
