import logging

from zipkin.models import Endpoint
from zipkin.client import Client

log = logging.getLogger(__name__)


def configure(name, settings, use_requests=True, use_celery=True):
    """Include the zipkin definitions"""

    endpoint = Endpoint(name)
    Client.configure(settings)

    if use_requests:
        try:
            from zipkin.binding.requests import bind as bind_requests
            bind_requests()
        except ImportError:
            log.warn('package requests not installed')

    if use_celery:
        from zipkin.binding.celery import bind as bind_celery
        bind_celery(endpoint)

    return endpoint
