from .models import Annotation, Trace
from .thread import local

__ALL__ = ['trace', 'get_current_trace']


def trace(name):
    """ A decorator that trace the decorated function """

    if hasattr(name, '__call__'):
        return trace(name.__name__)(name)

    def func_decorator(func):
        def wrapper(*args, **kwargs):
            try:
                tracing = True
                append_trace(name)
            except Exception:
                tracing = False

            try:
                return func(*args, **kwargs)
            finally:
                if tracing:
                    try:
                        end_current_trace()
                    except Exception:
                        tracing = False

        return wrapper
    return func_decorator


def get_current_trace():
    return local().current


def append_trace(name, endpoint=None):
    current = local().current
    if current:
        trace = current.child(name, endpoint)
    else:
        trace = Trace('unknown', None, None, None, endpoint=endpoint)
        local().append(trace)

    annotation = Annotation.server_recv()
    trace.record(annotation)


def end_current_trace():
    current = local().current
    current.record(Annotation.server_send())
    local().pop()
