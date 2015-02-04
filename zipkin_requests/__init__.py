from requests.adapters import HTTPAdapter
import requests.sessions
from zipkin import local

from zipkin.models import Annotation
from zipkin.util import hex_str

class ZipkinHTTPAdapter(HTTPAdapter):
    def __init__(self, trace, *args, **kwargs):
        super(ZipkinHTTPAdapter, self).__init__(**kwargs)
        self.parent_trace = trace

    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        request.trace = self.parent_trace.child("requests:%s %s" % (request.method, request.url))
        forwarded_trace = request.trace.child_noref("subservice")

        request.headers['X-B3-TraceId'] = hex_str(forwarded_trace.trace_id)
        request.headers['X-B3-SpanId'] = hex_str(forwarded_trace.span_id)
        if forwarded_trace.parent_span_id is not None:
            request.headers['X-B3-ParentSpanId'] = hex_str(forwarded_trace.parent_span_id)

        request.trace.record(Annotation.string('http.uri', request.url))
        request.trace.record(Annotation.server_recv())

        return super(ZipkinHTTPAdapter, self).send(request, stream, timeout, verify, cert, proxies)

    def build_response(self, req, resp):
        req.trace.record(Annotation.string('http.responsecode', '{0}'.format(getattr(resp, 'status', None))))
        req.trace.record(Annotation.server_send())

        return super(ZipkinHTTPAdapter, self).build_response(req, resp)


def _func(init):
    def func(self, *args, **kwargs):
        init(self, *args, **kwargs)
        trace = local().current
        self.mount('http://', ZipkinHTTPAdapter(trace))
        self.mount('https://', ZipkinHTTPAdapter(trace))
    return func

def init():
    old_init = requests.sessions.Session.__init__
    requests.sessions.Session.__init__ = _func(old_init)

