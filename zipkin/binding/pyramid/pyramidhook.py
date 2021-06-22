import logging

from zipkin import local
from zipkin.models import Trace, Annotation
from zipkin.util import int_or_none
from zipkin.client import log as zipkin_log
from zipkin.config import configure


log = logging.getLogger(__name__)


def wrap_request(registry):
    settings = registry.settings
    if "zipkin.collector" not in settings:
        logging.getLogger(__name__).info(
            "The plugin zipkin.binding.pyramid "
            "is active but not configured. "
            "Check the doc."
        )
        return
    default_name = registry.__name__
    name = settings.get("zipkin.service_name", default_name)
    endpoint = configure(name, settings)

    def wrap(event):
        request = event.request
        headers = request.headers
        had_trace = False
        if getattr(request, "trace", None):
            had_trace = True

        trace_name = request.path_qs
        if request.matched_route:
            # we only get a matched route if we've gone through the router.
            trace_name = request.matched_route.pattern

        if had_trace:
            request.trace.name = request.method + " " + trace_name
            trace = request.trace
        else:
            trace = Trace(
                request.method + " " + trace_name,
                int_or_none(headers.get("X-B3-TraceId", None)),
                int_or_none(headers.get("X-B3-SpanId", None)),
                int_or_none(headers.get("X-B3-ParentSpanId", None)),
                endpoint=endpoint,
            )

        if "X-B3-TraceId" not in headers:
            log.info("no trace info from request: %s", request.path_qs)

        if request.matchdict:  # matchdict maybe none if no route is registered
            for k, v in request.matchdict.items():
                trace.record(Annotation.string("route.param.%s" % k, v))

        trace.record(Annotation.string("http.path", request.path_qs))
        log.info("new trace %r", trace.trace_id)

        setattr(request, "trace", trace)
        if had_trace:
            # We already had a trace registered for this request, but we got
            # called again
            # We should be called twice:
            #  - For every request (tween view)
            #  - For every request *after* the router (ContextFound)
            # Just reset the TraceStack, drop the previous trace, and register
            # this one instead (which got more information)
            local().reset()
        else:
            request.add_response_callback(add_header_response)
            request.add_finished_callback(log_response(endpoint))

        local().append(trace)
        trace.record(Annotation.server_recv())

    return wrap


def add_header_response(request, response):
    if hasattr(request, "trace"):
        response.headers["Trace-Id"] = str(request.trace.trace_id)


def log_response(endpoint):
    def log_response(request):
        trace = request.trace
        trace.record(Annotation.server_send())
        log.info("reporting trace %s", trace.name)

        zipkin_log(trace)
        local().reset()

    return log_response


class tween_factory(object):
    def __init__(self, handler, registry):
        self.handler = handler
        self.registry = registry

    def __call__(self, request):
        class ZipkinTweenEvent(object):
            def __init__(self, request):
                self.request = request

        zipkin_wrapper = wrap_request(self.registry)
        if zipkin_wrapper:
            zipkin_wrapper(ZipkinTweenEvent(request))

        response = self.handler(request)

        return response
