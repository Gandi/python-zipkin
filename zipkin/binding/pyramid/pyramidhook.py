from __future__ import absolute_import
import time
import logging

from pyramid.tweens import INGRESS
from pyramid.settings import aslist

from zipkin import local
from zipkin.api import stack_trace
from zipkin.models import Trace, Annotation
from zipkin.util import int_or_none
from zipkin.client import log as zipkin_log
from zipkin.config import configure as configure_zk


log = logging.getLogger(__name__)


class AllTraceTweenView:

    endpoint = None

    @classmethod
    def configure(cls, settings):
        default_name = "Registry"  # Keep compat with `registry.__name__` ?
        name = settings.get("zipkin.service_name", default_name)

        bindings = aslist(settings.get("zipkin.bindings", "requests celery xmlrpclib"))
        cls.endpoint = configure_zk(
            name,
            settings,
            use_requests="requests" in bindings,
            use_celery="celery" in bindings,
            use_xmlrpclib="xmlrpclib" in bindings,
        )

    def __init__(self, handler, registry):
        self.handler = handler
        self.trace = None

    def track_start_request(self, request):
        headers = request.headers

        trace_name = request.path_qs
        if request.matched_route:
            # we only get a matched route if we've gone through the router.
            trace_name = request.matched_route.pattern

        trace = Trace(
            request.method + " " + trace_name,
            int_or_none(headers.get("X-B3-TraceId", None)),
            int_or_none(headers.get("X-B3-SpanId", None)),
            int_or_none(headers.get("X-B3-ParentSpanId", None)),
            endpoint=self.endpoint,
        )

        if "X-B3-TraceId" not in headers:
            log.info("no trace info from request: %s", request.path_qs)

        if request.matchdict:  # matchdict maybe none if no route is registered
            for k, v in request.matchdict.items():
                trace.record(Annotation.string("route.param.%s" % k, v))

        trace.record(Annotation.string("http.path", request.path_qs))
        log.info("new trace %r", trace.trace_id)

        stack_trace(trace)

        trace.record(Annotation.server_recv())
        self.trace = trace

    def track_end_request(self, request, response):
        if self.trace:
            self.trace.record(Annotation.server_send())
            log.info("reporting trace %s", self.trace.name)

            response.headers["Trace-Id"] = str(self.trace.trace_id)
            zipkin_log(self.trace)

    def __call__(self, request):
        self.track_start_request(request)
        response = None
        try:
            response = self.handler(request)
        finally:
            # request.response in case an exception is raised ?
            self.track_end_request(request, response or request.response)
            local().reset()
            self.trace = None
        return response or request.response


class SlowQueryTweenView(AllTraceTweenView):

    max_duration = None

    @classmethod
    def configure(cls, settings):
        super(SlowQueryTweenView, cls).configure(settings)
        setting = settings.get("zipkin.slow_log_duration_exceed")
        if setting is None:
            log.error(
                "Missing setting 'zipkin.slow_log_duration_exceed' %r",
                list(settings.keys()),
            )
            return
        try:
            cls.max_duration = float(setting)
        except ValueError:
            log.error("Invalid setting 'zipkin.slow_log_duration_exceed'")

    def __init__(self, handler, registry):
        super(SlowQueryTweenView, self).__init__(handler, registry)
        self.start = None

    def track_start_request(self, request):
        self.start = time.time()
        super(SlowQueryTweenView, self).track_start_request(request)

    def track_end_request(self, request, response):
        if self.max_duration is None:
            # unconfigure, we don't care
            return
        if self.start:
            duration = time.time() - self.start
            if duration > self.max_duration:
                super(SlowQueryTweenView, self).track_end_request(request, response)
            else:
                response.headers["Trace-Id"] = str(self.trace.trace_id)


def includeme(config):
    """Include the zipkin definitions"""

    # Attach the subscriber a couple of times, this allow to start logging as
    # early as possible. Later calls on the same request will enhance the more
    # we proceed through the stack (after authentication, after router, ...)

    settings = config.registry.settings
    tween_factory = settings.get("zipkin.tween_factory", "all")
    assert tween_factory in ["all", "slow_query"]
    if tween_factory == "all":
        tween_factory = AllTraceTweenView
    elif tween_factory == "slow_query":
        tween_factory = SlowQueryTweenView
    else:
        log.error(
            "Invalid value for settings 'zipkin.tween_factory', should be all or slow_query, not %s",
            tween_factory,
        )
        return

    tween_factory.configure(settings)

    config.add_tween(
        "{}.{}".format(tween_factory.__module__, tween_factory.__name__),
        under=INGRESS,
    )
