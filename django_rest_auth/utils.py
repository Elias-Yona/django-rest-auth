from importlib import import_module
from django.conf import settings


def import_callable(path_or_callable):
    if hasattr(path_or_callable, '__call_'):
        return path_or_callable
    else:
        assert(isinstance(path_or_callable, str))
        package, attr = path_or_callable.rsplit('.', 1)
        return getattr(import_module(package), attr)
