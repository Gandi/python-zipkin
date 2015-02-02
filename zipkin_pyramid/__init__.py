from pyramid.events import NewRequest
from zipkin.models import Endpoint

from .pyramidhook import wrap_request

from .client import init

def includeme(config):
    """Include the zipkin definitions"""

    print config.registry.__dict__
    name = config.registry.__name__

    endpoint = Endpoint("127.0.0.1", 0, name)
    init("127.0.0.1", 9410)

    config.add_subscriber(wrap_request(endpoint), NewRequest)


