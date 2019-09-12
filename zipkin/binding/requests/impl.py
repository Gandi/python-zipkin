
import requests.sessions

from . import events
from .events import request_adapter


def bind():
    old_init = requests.sessions.Session.__init__
    requests.sessions.Session.__init__ = events.session_init(old_init)
