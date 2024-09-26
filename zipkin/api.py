from functools import wraps

from .models import Annotation
from .thread import local

__all__ = ["trace", "get_current_trace"]


class Trace:
    def __init__(self, name):
        self.name = name
        self.recording = None
        self.trace = None

    def __enter__(self):

        try:
            self.trace = local().child(self.name)
            annotation = Annotation.server_recv()
            self.trace.record(annotation)
            self.recording = True
        except Exception:
            self.recording = False

    def __exit__(self, type, value, traceback):
        if self.recording:
            self.trace.record(Annotation.server_send())
            local().pop()

    def __call__(self, func):
        @wraps(func)
        def decorated(*args, **kwds):
            with self:
                return func(*args, **kwds)

        return decorated


def trace(name):
    """A decorator that trace the decorated function"""

    if hasattr(name, "__call__"):
        return trace(name.__name__)(name)

    def func_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with Trace(name):
                return func(*args, **kwargs)

        return wrapper

    return func_decorator


def get_current_trace():
    return local().current


def stack_trace(trace):
    return local().append(trace)
