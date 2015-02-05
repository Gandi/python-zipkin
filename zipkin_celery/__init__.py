from __future__ import print_function
import sys
import socket
import logging

try:
    _use_celery = True
    from celery.signals import before_task_publish, task_prerun, task_postrun
except ImportError:
    _use_celery = False

from zipkin.models import Endpoint
from . import config

log = logging.getLogger(__name__)

if _use_celery:

    def zipkin_init(endpoint=None):
        if not endpoint:
            ip = socket.gethostbyname_ex(socket.gethostname())[2][0]
            _endpoint = Endpoint(ip, 0, "Celery")
        else:
            _endpoint = endpoint
        config._endpoint =_endpoint

        log.info('Attaching zipkin to celery signals')
        before_task_publish.connect(config.task_send_handler)
        task_prerun.connect(config.task_prerun_handler)
        task_postrun.connect(config.task_postrun_handler)
        log.info('zipkin signals attached')

else:

    # most likely, celery is not available
    log.warn('package celery not installed')
    def zipkin_init(*args, **kwargs):
        pass
