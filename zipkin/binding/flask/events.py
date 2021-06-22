from zipkin import local
from zipkin.client import log
from zipkin.models import Annotation, Trace
from zipkin.util import int_or_none

from flask import request

endpoint = None


def pre_request(app, **extra):
    headers = request.headers
    trace = Trace(
        request.method + " " + request.url,
        int_or_none(headers.get("X-B3-TraceId", None)),
        int_or_none(headers.get("X-B3-SpanId", None)),
        int_or_none(headers.get("X-B3-ParentSpanId", None)),
        endpoint=endpoint,
    )

    setattr(request, "trace", trace)
    local().append(trace)
    trace.record(Annotation.string("http.uri", request.url))
    trace.record(Annotation.server_recv())


def pre_response(app, response, **extra):
    request.trace.record(
        Annotation.string("http.responsecode", "{0}".format(response.status_code))
    )
    request.trace.record(Annotation.server_send())
    log(request.trace)
    local().pop()
