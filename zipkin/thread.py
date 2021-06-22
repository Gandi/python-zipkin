import threading
from .models import TraceStack

data = None


def local():
    global data
    if not data:
        data = threading.local()

    if not getattr(data, "trace", None):
        data.trace = TraceStack()
    return data.trace
