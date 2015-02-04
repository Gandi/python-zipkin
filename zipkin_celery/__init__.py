import socket

from celery.signals import before_task_publish, task_prerun, task_postrun

from zipkin import local
from zipkin.models import Annotation, Endpoint, Trace
from zipkin.util import hex_str, int_or_none

from zipkin_pyramid.client import log


_endpoint = None

def task_send_handler(body, exchange, routing_key, headers, **kwargs):
    trace = local().current
    forwarded_trace = trace.child_noref("subservice")

    headers['X-B3-TraceId'] = hex_str(forwarded_trace.trace_id)
    headers['X-B3-SpanId'] = hex_str(forwarded_trace.span_id)
    if forwarded_trace.parent_span_id is not None:
        headers['X-B3-ParentSpanId'] = hex_str(forwarded_trace.parent_span_id)

def task_prerun_handler(task_id, task, **kwargs):
    global _endpoint
    request = task.request

    trace = Trace("celery",
                  int_or_none(request.headers.get('X-B3-TraceId', None)),
                  int_or_none(request.headers.get('X-B3-SpanId', None)),
                  int_or_none(request.headers.get('X-B3-ParentSpanId', None)),
                  endpoint=_endpoint)

    setattr(request, 'trace', trace)
    local().append(trace)
    trace.record(Annotation.server_recv())


def task_postrun_handler(task_id, task, **kwargs):
    trace = local().current
    trace.record(Annotation.server_send())

    log(trace)


def zipkin_init(endpoint = None):
    global _endpoint
    if not endpoint:
        ip = socket.gethostbyname_ex(socket.gethostname())[2][0]
        _endpoint = Endpoint(ip, 0, "pyramidzipkin")
    else:
        _endpoint = endpoint

    before_task_publish.connect(task_send_handler)
    task_prerun.connect(task_prerun_handler)
    task_postrun.connect(task_postrun_handler)


