import socket
import logging

from zipkin.models import Endpoint
from zipkin.client import Client

log = logging.getLogger(__name__)


def configure(name, settings, use_requests=True, use_celery=True):
    """Include the zipkin definitions"""

    ip = socket.gethostbyname_ex(socket.gethostname())[2][0]
    endpoint = Endpoint(ip, 0, name)
    Client.configure(settings)

    if use_requests:
        try:
            from zipkin_requests import init as request_init
            request_init()
        except ImportError:
            log.warn('package requests not installed')

    if use_celery:
        from zipkin_celery import zipkin_init as celery_init
        celery_init(endpoint)

    return endpoint
