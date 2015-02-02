import socket

from pyramid.events import NewRequest
from zipkin.models import Endpoint
from pyramid.tweens import MAIN, EXCVIEW

from .pyramidhook import wrap_request

from .client import Client
from .api import *


from zipkin_requests import init as request_init

def includeme(config):
    """Include the zipkin definitions"""

    settings = config.registry.settings
    if 'zipkin.collector' not in settings:
        return
    name = config.registry.__name__

    ip = socket.gethostbyname_ex(socket.gethostname())[2][0]
    endpoint = Endpoint(ip, 0, name)
    Client.configure(settings)

    request_init()

    config.add_subscriber(wrap_request(endpoint), NewRequest)
