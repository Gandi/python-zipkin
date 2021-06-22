import logging

from celery.signals import before_task_publish, task_prerun, task_postrun

from zipkin.models import Endpoint
from . import events

log = logging.getLogger(__name__)


def bind(endpoint=None):
    if not endpoint:
        endpoint = Endpoint("Celery")

    events.endpoint = endpoint

    log.info("Attaching zipkin to celery signals")
    before_task_publish.connect(events.task_send_handler)
    task_prerun.connect(events.task_prerun_handler)
    task_postrun.connect(events.task_postrun_handler)
    log.info("zipkin signals attached")
