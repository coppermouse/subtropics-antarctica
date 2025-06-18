# -----------------------------------------
# source/on_signal.py
# ------------------------------------------

from collections import defaultdict


def on_signal(type, order):
    def inner(func):
        OnSignal.add_listener(type, order, func)

        def wrapper():
            func()
        return wrapper
    return inner


def send_signal(_type, message=None):
    order_function = OnSignal.types_order_function.get(_type)
    for order in sorted(order_function):
        if order_function[order](message) == 'break':
            break


class OnSignal:

    types_order_function = defaultdict(dict)

    @classmethod
    def add_listener(cls, type, order, func):

        if order in cls.types_order_function[type]:
            raise Exception("order on this type already taken")

        cls.types_order_function[type][order] = func
