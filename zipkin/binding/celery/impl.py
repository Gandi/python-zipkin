import socket
import logging

from celery.signals import before_task_publish, task_prerun, task_postrun

from zipkin.models import Endpoint
from . import config

log = logging.getLogger(__name__)


def bind(endpoint=None):
    if not endpoint:
        ip = socket.gethostbyname_ex(socket.gethostname())[2][0]
        endpoint = Endpoint(ip, 0, "Celery")

    config._endpoint = endpoint

    log.info('Attaching zipkin to celery signals')
    before_task_publish.connect(config.task_send_handler)
    task_prerun.connect(config.task_prerun_handler)
    task_postrun.connect(config.task_postrun_handler)
    log.info('zipkin signals attached')
