#!/usr/bin/env python3


def singleton(class_):
    _instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in _instances:
            _instances[class_] = class_(*args, **kwargs)
        return _instances[class_]
    return getinstance
