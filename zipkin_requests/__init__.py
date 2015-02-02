from requests.adapters import HTTPAdapter, DEFAULT_POOLSIZE, DEFAULT_POOLBLOCK, DEFAULT_RETRIES
import requests as r

from .models import Annotation
from .util import hex_str

class ZipkinHTTPAdapter(HTTPAdapter):
    def __init__(self, trace, name, pool_connections=DEFAULT_POOLSIZE,
                 pool_maxsize=DEFAULT_POOLSIZE, max_retries=DEFAULT_RETRIES,
                 pool_block=DEFAULT_POOLBLOCK, endpoint=None):
        super(ZipkinHTTPAdapter, self).__init__(pool_connections, pool_maxsize, max_retries, pool_block)
        self.trace = trace
        self.name = name
        self.endpoint = endpoint

    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        trace = self.trace.child(self.name, self.endpoint)
        request.trace = trace

        request.headers['X-B3-TraceId'] = hex_str(trace.trace_id)
        request.headers['X-B3-SpanId'] = hex_str(trace.span_id)
        if trace.parent_span_id is not None:
            request.headers['X-B3-ParentSpanId'] = hex_str(trace.parent_span_id)

        trace.record(Annotation.string('http.uri', request.url))
        trace.record(Annotation.client_send())

        return super(ZipkinHTTPAdapter, self).send(request, stream, timeout, verify, cert, proxies)

    def build_response(self, req, resp):
        trace = req.trace
        trace.record(Annotation.client_recv())
        trace.record(Annotation.string('http.responsecode', '{0}'.format(getattr(resp, 'status', None))))

        return super(ZipkinHTTPAdapter, self).build_response(req, resp)


def requests(request, name, endpoint=None):
    s = r.session()
    if endpoint:
       endpoint = request.trace._endpoint.child(endpoint)

    s.mount('http://', ZipkinHTTPAdapter(request.trace, name, endpoint=endpoint))
    s.mount('https://', ZipkinHTTPAdapter(request.trace, name, endpoint=endpoint))

    return s
