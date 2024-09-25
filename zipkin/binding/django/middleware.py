"""Middleware for django."""

import time
import logging

from django.conf import settings

from zipkin import local
from zipkin.api import get_current_trace, stack_trace
from zipkin.models import Trace, Annotation, Endpoint
from zipkin.util import int_or_none
from zipkin.client import log as zipkin_log

from .apps import ZipkinConfig


log = logging.getLogger(__name__)


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
    try:
        zipkin_log(trace)
    except Exception as err:
        log.error("Error while sending trace: %s", trace)


def add_header_response(response):
    trace = get_current_trace()
    if trace:
        response["Trace-Id"] = str(trace.trace_id)


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
        local().reset()
        return response

    return middleware


def zk_slow_trace_middleware(get_response):
    """
    Zipkin Middleware to trace slow query only added in the django settings.

    Usage:

    ::
        # Only send trace of query that take more than 1.5 seconds
        ZIPKIN_SLOW_LOG_DURATION_EXCEED = 1.5

        MIDDLEWARE = [
            "zipkin.binding.django.middleware.zk_slow_trace_middleware",
            ...
        ]
    """

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        start = time.time()
        trace = init_trace(request)

        response = get_response(request)
        duration = time.time() - start
        add_header_response(response)
        if duration >= settings.ZIPKIN_SLOW_LOG_DURATION_EXCEED:
            log_response(trace, response)
        local().reset()
        return response

    return middleware
