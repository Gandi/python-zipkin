import socket
import logging
from pyramid.events import NewRequest

from zipkin.models import Endpoint
from zipkin.client import Client
from zipkin_requests import init as request_init
from zipkin_celery import zipkin_init as celery_init

log = logging.getLogger(__name__)


def configure(name, settings, requests=True, celery=True):
    """Include the zipkin definitions"""


    ip = socket.gethostbyname_ex(socket.gethostname())[2][0]
    endpoint = Endpoint(ip, 0, name)
    Client.configure(settings)

    if requests:
        try:
            request_init()
        except ImportError:
            log.warn('package requests not installed')

    if celery:
        try:
            celery_init(endpoint)
        except ImportError:
            log.warn('package celery not installed')

    return endpoint
