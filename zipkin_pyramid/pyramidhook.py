from scribe import scribe
from thrift.transport import TTransport, TSocket
from thrift.protocol import TBinaryProtocol

from zipkin.models import Trace, Annotation
from zipkin.util import base64_thrift_formatter


from .client import log


def int_or_none(val):
    if val is None:
        return None

    return int(val, 16)


def wrap_request(endpoint):
    def wrap(event):
        request = event.request

        trace = Trace(request.method,
                      int_or_none(request.headers.get('X-B3-TraceId', None)),
                      int_or_none(request.headers.get('X-B3-SpanId', None)),
                      int_or_none(request.headers.get('X-B3-ParentSpanId', None)),
                      endpoint=endpoint)

        setattr(request, 'trace', trace)
        trace.record(Annotation.server_recv())
        request.add_finished_callback(log_response(endpoint))

    return wrap


def log_response(endpoint):
    def wrap(request):
        trace = request.trace
        trace.record(Annotation.server_send())

        log(trace)

    return wrap
