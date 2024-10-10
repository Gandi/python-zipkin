import logging
from urllib.parse import urlparse


from zipkin import local
from zipkin.models import Annotation
from zipkin.util import hex_str


log = logging.getLogger(__name__)


def filter_url_path(url):
    url = urlparse(url)._replace(path="", query=None, fragment="")
    url = url._replace(netloc=url.netloc.split("@")[-1])
    return url.geturl()


def pre_request(request):
    parent_trace = local().current
    if not parent_trace:
        return request

    url = filter_url_path(request.url)
    request.trace = parent_trace.child("requests:%s %s" % (request.method, url))
    forwarded_trace = request.trace.child_noref("subservice")

    request.headers["X-B3-TraceId"] = hex_str(forwarded_trace.trace_id)
    request.headers["X-B3-SpanId"] = hex_str(forwarded_trace.span_id)
    if forwarded_trace.parent_span_id is not None:
        request.headers["X-B3-ParentSpanId"] = hex_str(forwarded_trace.parent_span_id)

    request.trace.record(Annotation.string("http.method", request.method))
    request.trace.record(Annotation.string("http.url", request.url))
    request.trace.record(Annotation.string("span.kind", "client"))
    request.trace.record(Annotation.server_recv())

    return request


def pre_response(resp, req=None):
    if not req:
        req = resp.request

    if not hasattr(req, "trace"):
        return resp

    req.trace.record(
        Annotation.string(
            "http.status_code", "{0}".format(getattr(resp, "status", None))
        )
    )
    req.trace.record(Annotation.server_send())

    return resp


class Proxy:
    __slots__ = ["_obj", "__weakref__"]

    def __init__(self, obj):
        object.__setattr__(self, "_obj", obj)

    #
    # proxying (special cases)
    #
    def __getattr__(self, name):
        return getattr(object.__getattribute__(self, "_obj"), name)

    def __delattr__(self, name):
        delattr(object.__getattribute__(self, "_obj"), name)

    def __setattr__(self, name, value):
        setattr(object.__getattribute__(self, "_obj"), name, value)

    def __nonzero__(self):
        return bool(object.__getattribute__(self, "_obj"))

    def __str__(self):
        return str(object.__getattribute__(self, "_obj"))

    def __repr__(self):
        return repr(object.__getattribute__(self, "_obj"))

    #
    # factories
    #
    _special_names = [
        "__abs__",
        "__add__",
        "__and__",
        "__call__",
        "__cmp__",
        "__coerce__",
        "__contains__",
        "__delitem__",
        "__delslice__",
        "__div__",
        "__divmod__",
        "__eq__",
        "__float__",
        "__floordiv__",
        "__ge__",
        "__getitem__",
        "__getslice__",
        "__gt__",
        "__hash__",
        "__hex__",
        "__iadd__",
        "__iand__",
        "__idiv__",
        "__idivmod__",
        "__ifloordiv__",
        "__ilshift__",
        "__imod__",
        "__imul__",
        "__int__",
        "__invert__",
        "__ior__",
        "__ipow__",
        "__irshift__",
        "__isub__",
        "__iter__",
        "__itruediv__",
        "__ixor__",
        "__le__",
        "__len__",
        "__long__",
        "__lshift__",
        "__lt__",
        "__mod__",
        "__mul__",
        "__ne__",
        "__neg__",
        "__oct__",
        "__or__",
        "__pos__",
        "__pow__",
        "__radd__",
        "__rand__",
        "__rdiv__",
        "__rdivmod__",
        "__reduce__",
        "__reduce_ex__",
        "__repr__",
        "__reversed__",
        "__rfloorfiv__",
        "__rlshift__",
        "__rmod__",
        "__rmul__",
        "__ror__",
        "__rpow__",
        "__rrshift__",
        "__rshift__",
        "__rsub__",
        "__rtruediv__",
        "__rxor__",
        "__setitem__",
        "__setslice__",
        "__sub__",
        "__truediv__",
        "__xor__",
        "next",
    ]

    @classmethod
    def _create_class_proxy(cls, theclass):
        """creates a proxy for the given class"""

        def make_method(name):
            def method(self, *args, **kw):
                return getattr(object.__getattribute__(self, "_obj"), name)(*args, **kw)

            return method

        namespace = {}
        for name in cls._special_names:
            if hasattr(theclass, name):
                namespace[name] = make_method(name)
        return type("%s(%s)" % (cls.__name__, theclass.__name__), (cls,), namespace)

    def __new__(cls, obj, *args, **kwargs):
        """
        creates an proxy instance referencing `obj`. (obj, *args, **kwargs) are
        passed to this class' __init__, so deriving classes can define an
        __init__ method of their own.
        note: _class_proxy_cache is unique per deriving class (each deriving
        class must hold its own cache)
        """
        try:
            cache = cls.__dict__["_class_proxy_cache"]
        except KeyError:
            cls._class_proxy_cache = cache = {}
        try:
            theclass = cache[obj.__class__]
        except KeyError:
            cache[obj.__class__] = theclass = cls._create_class_proxy(obj.__class__)
        ins = object.__new__(theclass)
        theclass.__init__(ins, obj, *args, **kwargs)
        return ins


try:
    from requests.adapters import HTTPAdapter

    class ZipkinAdapterProxy(Proxy, HTTPAdapter):
        """This class will proxy all methods or attributes to underlying
        HTTPAdapter, it also override the send and build_response to hook
        zipkin headers and tracing.
        The proxy allows to hook into an existing HTTPAdapter
        """

        def send(self, request, *args, **kwargs):
            pre_request(request)
            return super(ZipkinAdapterProxy, self).send(request, *args, **kwargs)

        def build_response(self, req, resp, *args, **kwargs):
            pre_response(resp, req)

            return super(ZipkinAdapterProxy, self).build_response(
                req, resp, *args, **kwargs
            )

    def request_adapter(adapter):
        return ZipkinAdapterProxy(adapter)

except ImportError:
    # requests < 1.0.0
    def request_adapter(adapter):
        return adapter


def session_init(init):
    def func(self, *args, **kwargs):
        init(self, *args, **kwargs)
        if hasattr(self, "mount"):
            adapter = ZipkinAdapterProxy(HTTPAdapter())
            self.mount("http://", adapter)
            self.mount("https://", adapter)
        else:
            self.hooks["pre_request"] = pre_request
            self.hooks["response"] = pre_response

    return func
