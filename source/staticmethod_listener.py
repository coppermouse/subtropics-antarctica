# -----------------------------------------
# source/staticmethod_listener.py
# ------------------------------------------

from collections import defaultdict
from on_signal import on_signal
from functools import lru_cache


def staticmethod_listener(staticmethod):
    def inner(func):
        StaticmethodListener.staticmethod_listeners[staticmethod].append(func)

        def wrapper():
            func()
        return wrapper
    return inner


class StaticmethodListener:

    staticmethod_listeners = defaultdict(list)
    staticmethod_listener_last_value = dict()

    @lru_cache(maxsize=2**7)
    def get_method_by_name(name):
        _class, method = name.split(".")
        m = __import__(_class.lower())
        c = getattr(m, _class)
        return getattr(c, method)

    @on_signal(type='on update', order=30)
    def on_update(message):
        from room import Room
        cls = StaticmethodListener
        for name, funcs in sorted(cls.staticmethod_listeners.items()):
            method = StaticmethodListener.get_method_by_name(name)
            value = method()
            if name in cls.staticmethod_listener_last_value:
                last_value = cls.staticmethod_listener_last_value[name]
                if value != last_value:
                    for func in funcs:
                        func(last_value, value)
            cls.staticmethod_listener_last_value[name] = value
