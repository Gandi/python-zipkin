import logging

from zipkin import local
from zipkin.models import Trace, Annotation
from zipkin.util import int_or_none
from zipkin.client import log


logger = logging.getLogger(__name__)


def wrap_request(endpoint):
    def wrap(event):
        request = event.request
        headers = request.headers
        trace = Trace(request.method + ' ' + request.matched_route.pattern,
                      int_or_none(headers.get('X-B3-TraceId', None)),
                      int_or_none(headers.get('X-B3-SpanId', None)),
                      int_or_none(headers.get('X-B3-ParentSpanId', None)),
                      endpoint=endpoint)
        if 'X-B3-TraceId' not in headers:
            logger.warn('no trace info from request')

        trace.record(Annotation.string('http.path', request.path_qs))
        logger.info('new trace %r' % trace.trace_id)

        setattr(request, 'trace', trace)
        local().append(trace)
        trace.record(Annotation.server_recv())
        request.add_response_callback(add_header_response)
        request.add_finished_callback(log_response(endpoint))

    return wrap


def add_header_response(request, response):
    if hasattr(request, 'trace'):
        trace = request.trace
        response.headers['Trace-Id'] = str(request.trace.trace_id)


def log_response(endpoint):
    def wrap(request):
        trace = request.trace
        trace.record(Annotation.server_send())

        log(trace)
        local().pop()

        request.response.headers['Trace-Id'] = request.trace.trace_id

    return wrap
