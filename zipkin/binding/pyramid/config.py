import logging

from pyramid.events import ContextFound, NewRequest
from pyramid.config import aslist

from zipkin.config import configure
from .pyramidhook import wrap_request


def includeme(config):
    """Include the zipkin definitions"""

    settings = config.registry.settings
    if 'zipkin.collector' not in settings:
        logging.getLogger(__name__).info('The plugin zipkin.binding.pyramid '
                                         'is active but not configured. '
                                         'Check the doc.')
        return
    default_name = config.registry.__name__
    name = settings.get('zipkin.service_name', default_name)
    endpoint = configure(name, settings)

    # Attach the subscriber twice, ensure we can log request that do not
    # get through the router
    config.add_subscriber(wrap_request(endpoint), NewRequest)
    config.add_subscriber(wrap_request(endpoint), ContextFound)

