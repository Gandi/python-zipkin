import logging

from flask import request_started, request_finished

from zipkin.models import Endpoint
from . import events

log = logging.getLogger(__name__)


def bind(app, endpoint=None):
    if not endpoint:
        endpoint = Endpoint(app.name)

    events.endpoint = endpoint

    log.info("Attaching zipkin to Flask signals")
    request_started.connect(events.pre_request, app)
    request_finished.connect(events.pre_response, app)
    log.info("zipkin signals attached")
