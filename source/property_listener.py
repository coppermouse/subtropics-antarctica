# -----------------------------------------
# source/property_listener.py
# ------------------------------------------

from on_signal import on_signal


def property_listener(prop):
    def inner(func):
        PropertyListener.property_listener_prop_function.add((prop, func))

        def wrapper():
            func()
        return wrapper
    return inner


class PropertyListener:

    property_listener_instances = set()
    property_listener_prop_function = set()
    property_listener_last_data = dict()

    def __init__(self):
        PropertyListener.property_listener_instances.add(self)

    @on_signal(type='on update', order=29)
    def on_update(message):
        cls = PropertyListener
        for instance in cls.property_listener_instances.copy():
            for prop, func in cls.property_listener_prop_function:
                if instance.__class__.__qualname__ == func.__qualname__.split(".")[0]:
                    value = getattr(instance, prop)
                    if (instance, prop) in cls.property_listener_last_data:
                        last_value = cls.property_listener_last_data[(
                            instance, prop)]
                        if value != last_value:
                            func(instance, last_value, value)

                    cls.property_listener_last_data[(instance, prop)] = value
