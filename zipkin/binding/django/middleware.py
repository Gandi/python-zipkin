"""Middleware for django."""
from django.conf import settings

from zipkin import local
from zipkin.api import get_current_trace, stack_trace
from zipkin.models import Trace, Annotation, Endpoint
from zipkin.util import int_or_none
from zipkin.client import log as zipkin_log

from .apps import ZipkinConfig


def init_trace(request):
    headers = request.headers
    trace_name = request.method + " " + request.path_info
    trace = Trace(
        trace_name,
        int_or_none(headers.get("X-B3-TraceId", None)),
        int_or_none(headers.get("X-B3-SpanId", None)),
        int_or_none(headers.get("X-B3-ParentSpanId", None)),
        endpoint=Endpoint(ZipkinConfig.service_name),
    )
    trace.record(Annotation.string("http.path", request.path_info))
    trace.record(Annotation.string("span.kind", "client"))
    trace.record(Annotation.server_recv())
    stack_trace(trace)
    return trace


def log_response(trace, response):
    trace.record(
        Annotation.string("http.responsecode", "{0}".format(response.status_code))
    )
    trace.record(Annotation.server_send())
    zipkin_log(trace)
    local().reset()


def add_header_response(response):
    response["Trace-Id"] = str(get_current_trace().trace_id)


def zk_middleware(get_response):
    """
    Zipkin Middleware to add in the django settings.


    Usage:

    ::

        MIDDLEWARE = [
            "zipkin.binding.django.middleware.zk_middleware",
            ...
        ]
    """

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        trace = init_trace(request)

        response = get_response(request)

        add_header_response(response)
        log_response(trace, response)

        return response

    return middleware