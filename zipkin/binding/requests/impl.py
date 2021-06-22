import requests.sessions

from . import events
from .events import request_adapter


def bind():
    if not getattr(requests.sessions.Session, "_zipkin_patched", False):
        old_init = requests.sessions.Session.__init__
        requests.sessions.Session.__init__ = events.session_init(old_init)
        requests.sessions.Session._zipkin_patched = True
