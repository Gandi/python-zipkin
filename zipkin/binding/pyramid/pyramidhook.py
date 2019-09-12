import logging

from zipkin import local
from zipkin.models import Trace, Annotation
from zipkin.util import int_or_none
from zipkin.client import log as zipkin_log


log = logging.getLogger(__name__)


def wrap_request(endpoint):
    def wrap(event):
        request = event.request
        headers = request.headers
        had_trace = False
        if getattr(request, 'trace', None):
            had_trace = True

        trace = Trace(request.method + ' ' + request.matched_route.pattern,
                      int_or_none(headers.get('X-B3-TraceId', None)),
                      int_or_none(headers.get('X-B3-SpanId', None)),
                      int_or_none(headers.get('X-B3-ParentSpanId', None)),
                      endpoint=endpoint)
        if 'X-B3-TraceId' not in headers:
            log.info('no trace info from request: %s', request.path_qs)

        trace.record(Annotation.string('http.path', request.path_qs))
        log.info('new trace %r', trace.trace_id)

        setattr(request, 'trace', trace)
        if had_trace:
            # We already had a trace registered for this request, but we got called again
            # We should be called twice:
            #  - For every request (NewRequest subscriber)
            #  - For every request *after* the router (ContextFound)
            # Just reset the TraceStack, drop the previous trace, and register this one
            # instead (which got more information)
            local().reset()
        else:
            request.add_response_callback(add_header_response)
            request.add_finished_callback(log_response(endpoint))

        local().append(trace)
        trace.record(Annotation.server_recv())

    return wrap


def add_header_response(request, response):
    if hasattr(request, 'trace'):
        trace = request.trace
        response.headers['Trace-Id'] = str(request.trace.trace_id)


def log_response(endpoint):
    def log_response(request):
        trace = request.trace
        trace.record(Annotation.server_send())
        log.info('reporting trace %s', trace.name)

        zipkin_log(trace)
        local().reset()

    return log_response
