
from zipkin.models import Annotation

from zipkin import local

def trace(name):
    if hasattr(name, '__call__'):
        return trace(name.__name__)(name)

    def func_decorator(func):
        def wrapper(*args):
            trace = local().child(name)

            try:
                annotation = Annotation.server_recv()

                trace.record(annotation)
                return func(*args)
            finally:
                trace.record(Annotation.server_send())

                local().pop()

        return wrapper
    return func_decorator


