
from zipkin import local
from zipkin.models import Annotation, Trace
from zipkin.util import hex_str, int_or_none

from zipkin.client import log


endpoint = None


def task_send_handler(body, exchange, routing_key, headers, **kwargs):
    trace = local().current
    forwarded_trace = trace.child_noref("subservice")

    headers['X-B3-TraceId'] = hex_str(forwarded_trace.trace_id)
    headers['X-B3-SpanId'] = hex_str(forwarded_trace.span_id)
    if forwarded_trace.parent_span_id is not None:
        headers['X-B3-ParentSpanId'] = hex_str(forwarded_trace.parent_span_id)


def task_prerun_handler(task_id, task, **kwargs):
    request = task.request

    trace = Trace('Task %r' % task.name,
                  int_or_none(request.headers.get('X-B3-TraceId', None)),
                  int_or_none(request.headers.get('X-B3-SpanId', None)),
                  int_or_none(request.headers.get('X-B3-ParentSpanId', None)),
                  endpoint=endpoint)

    setattr(request, 'trace', trace)
    local().append(trace)
    trace.record(Annotation.server_recv())


def task_postrun_handler(task_id, task, **kwargs):
    trace = local().current
    trace.record(Annotation.server_send())

    log(trace)
