from pyramid.events import NewRequest

from zipkin.config import configure
from .pyramidhook import wrap_request


def includeme(config):
    """Include the zipkin definitions"""

    settings = config.registry.settings
    if 'zipkin.collector' not in settings:
        return
    name = config.registry.__name__
    endpoint = configure(name, settings)

    config.add_subscriber(wrap_request(endpoint), NewRequest)
