from .models import Annotation
from .thread import local

__all__ = ['trace', 'get_current_trace']


def trace(name):
    """ A decorator that trace the decorated function """

    if hasattr(name, '__call__'):
        return trace(name.__name__)(name)

    def func_decorator(func):
        def wrapper(*args, **kwargs):

            try:
                try:
                    recording = True
                    trace = local().child(name)
                    annotation = Annotation.server_recv()
                    trace.record(annotation)
                except Exception:
                    recording = False
                return func(*args, **kwargs)
            finally:
                if recording:
                    trace.record(Annotation.server_send())
                    local().pop()

        return wrapper
    return func_decorator


def get_current_trace():
    return local().current


def stack_trace(trace):
    return local().append(trace)
