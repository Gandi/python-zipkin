import logging

from .models import Endpoint
from . import client

log = logging.getLogger(__name__)


def configure(
    name,
    settings,
    prefix="zipkin.",
    use_requests=True,
    use_celery=True,
    use_xmlrpclib=True,
):
    """Include the zipkin definitions"""

    endpoint = Endpoint(name)
    client.configure(settings, prefix=prefix)

    # Install in libs here
    if use_requests:
        from .binding.requests import bind as bind_requests

        bind_requests()

    if use_celery:
        from .binding.celery import bind as bind_celery

        bind_celery(endpoint)

    if use_xmlrpclib:
        from .binding.xmlrpclib import bind as bind_xmlrpclib

        bind_xmlrpclib()

    return endpoint
