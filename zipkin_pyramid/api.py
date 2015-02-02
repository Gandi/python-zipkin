
from zipkin.models import Annotation

from zipkin import local

def trace(name):
    if hasattr(name, '__call__'):
        return trace(name.__name__)(name)

    def func_decorator(func):
        def wrapper(**kwargs):
            trace = local().child(name)

            try:
                annotation = Annotation.client_send()

                trace.record(annotation)
                return func(**kwargs)
            finally:
                annotation = Annotation.client_recv()
                trace.record(annotation)
                local().pop()

        return wrapper
    return func_decorator


