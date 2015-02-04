import socket

from pyramid.events import NewRequest

from zipkin.config import configure
from zipkin.models import Endpoint
from zipkin.client import Client
from zipkin_requests import init as request_init
from .pyramidhook import wrap_request


def includeme(config):
    """Include the zipkin definitions"""

    settings = config.registry.settings
    if 'zipkin.collector' not in settings:
        return
    name = config.registry.__name__
    endpoint = configure(name, settings)

    config.add_subscriber(wrap_request(endpoint), NewRequest)
