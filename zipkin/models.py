import math
import time
import socket
from threading import Lock

from .util import uniq_id
from .client import Local
from .zipkin import zipkincore_thrift as constants


class Id(int):
    def __repr__(self):
        return "<Id %x>" % self

    def __str__(self):
        return "%x" % self


class Endpoint:
    """
    :param ip: C{str} ip address
    :param port: C{int} port number
    :param service_name: C{str} service_name
    """

    def __init__(self, service_name, ip=None, port=0):
        try:
            if not ip:
                if Local.local_ip:
                    ip = Local.local_ip
                else:
                    ip = socket.gethostbyname_ex(socket.gethostname())[2][0]
        except socket.gaierror:
            ip = "127.0.0.1"
        self.ip = ip
        self.port = port
        self.service_name = service_name


# TODO
# __eq__, __ne__, __repr__


class TraceStack:
    def __init__(self):
        self.stack = []
        self.cur = None

        # Locking is required, as stack and cur should mutate at the same time
        self.lock = Lock()

    @property
    def current(self):
        """Get the current trace"""
        return self.cur

    def child(self, name, endpoint=None):
        assert isinstance(name, (bytes, str)), "name parameter should be a string"
        assert (
            isinstance(endpoint, Endpoint) or endpoint is None
        ), "endpoint parameter should be an Endpoint"

        try:
            trace = self.cur.child(name, endpoint)
            self.lock.acquire()
            self.stack.append(trace)
            self.cur = trace
            return trace
        finally:
            self.lock.release()

    def reset(self):
        try:
            self.lock.acquire()
            self.stack = []
            self.cur = None
        finally:
            self.lock.release()

    def replace(self, trace):
        assert isinstance(trace, Trace), "trace parameter should be of type Trace"

        try:
            self.lock.acquire()
            self.stack = [trace]
            self.cur = trace
        finally:
            self.lock.release()

    def append(self, trace):
        assert isinstance(trace, Trace), "trace parameter should be of type Trace"

        try:
            self.lock.acquire()
            self.stack.append(trace)
            self.cur = trace
        finally:
            self.lock.release()

    def pop(self):
        try:
            self.lock.acquire()

            if self.cur is None:
                raise IndexError("pop from an empty stack")

            # pop is safe here, cur is not none, current stack can't be empty
            trace = self.stack.pop()
            try:
                cur = self.stack.pop()
                self.stack.append(cur)
                self.cur = cur
            except:
                self.cur = None
            return trace
        finally:
            self.lock.release()


class Trace:
    def __init__(
        self, name, trace_id=None, span_id=None, parent_span_id=None, endpoint=None
    ):
        assert isinstance(name, (bytes, str)), "name parameter should be a string"
        self.name = name
        self.trace_id = Id(trace_id or uniq_id())
        self.span_id = Id(span_id or uniq_id())

        self.parent_span_id = parent_span_id

        self.annotations = []
        self._children = []

        self._endpoint = endpoint

    def record(self, *annotations):
        for a in annotations:
            if a.endpoint is None:
                a.endpoint = self._endpoint
        self.annotations.extend(annotations)

    def child_noref(self, name, endpoint=None):
        if endpoint is not None:
            e = endpoint
        else:
            e = self._endpoint
        trace = self.__class__(
            name, trace_id=self.trace_id, parent_span_id=self.span_id, endpoint=e
        )
        return trace

    def child(self, name, endpoint=None):
        trace = self.child_noref(name, endpoint)
        self._children.append(trace)
        return trace

    def children(self):
        return [y for x in self._children for y in x.children()] + [self]

    def __repr__(self):
        return "<Trace %s>" % self.trace_id


class Annotation:
    """
    :param name: C{str} name of this annotation.

    :param value: A value of the appropriate type based on
        C{annotation_type}.

    :param annotation_type: C{str} the expected type of our C{value}.

    :param endpoint: An optional L{IEndpoint} provider to associate with
        this annotation or C{None}
    """

    def __init__(self, name, value, annotation_type, endpoint=None):
        self.name = name
        self.value = value
        self.annotation_type = annotation_type
        self.endpoint = endpoint

    @classmethod
    def timestamp(cls, name, timestamp=None):
        if timestamp is None:
            timestamp = math.trunc(time.time() * 1000 * 1000)

        return cls(name, timestamp, "timestamp")

    @classmethod
    def server_send(cls, timestamp=None):
        return cls.timestamp(constants.SERVER_SEND, timestamp)

    @classmethod
    def server_recv(cls, timestamp=None):
        return cls.timestamp(constants.SERVER_RECV, timestamp)

    @classmethod
    def client_send(cls, timestamp=None):
        return cls.timestamp(constants.CLIENT_SEND, timestamp)

    @classmethod
    def client_recv(cls, timestamp=None):
        return cls.timestamp(constants.CLIENT_RECV, timestamp)

    @classmethod
    def string(cls, name, value):
        return cls(name, value, "string")

    @classmethod
    def bytes(cls, name, value):
        return cls(name, value, "bytes")
