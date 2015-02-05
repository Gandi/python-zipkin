import socket
import logging

from zipkin.models import Endpoint

log = logging.getLogger(__name__)


try:
    from celery.signals import before_task_publish, task_prerun, task_postrun
    from .config import task_send_handler, task_prerun_handler, task_postrun_handler, _endpoint

    def zipkin_init(endpoint = None):
        global _endpoint
        if not endpoint:
            ip = socket.gethostbyname_ex(socket.gethostname())[2][0]
            _endpoint = Endpoint(ip, 0, "Celery")
        else:
            _endpoint = endpoint

        before_task_publish.connect(task_send_handler)
        task_prerun.connect(task_prerun_handler)
        task_postrun.connect(task_postrun_handler)

except ImportError:
    # most likely, celery is not available
    log.warn('package celery not installed')

    def zipkin_init(*args, **kwargs):
        pass
