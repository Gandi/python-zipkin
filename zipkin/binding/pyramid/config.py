from pyramid.events import NewRequest
from pyramid.settings import aslist

from zipkin.config import configure
from .pyramidhook import wrap_request


def includeme(config):
    """Include the zipkin definitions"""

    settings = config.registry.settings
    if 'zipkin.collector' not in settings:
        import logging
        logging.getLogger(__name__).warn('The plugin zipkin.binding.pyramid'
                                         'is active but not configured. '
                                         'Check the doc.')
        return
    name = settings.get('zipkin.service_name', config.registry.__name__)
    to_ignore = aslist(settings.get('zipkin.to_ignore', []))
    endpoint = configure(name, settings)
    config.add_subscriber(wrap_request(endpoint, to_ignore), NewRequest)
