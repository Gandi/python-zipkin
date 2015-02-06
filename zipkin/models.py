import math
import time
import socket

from .util import uniq_id
from ._thrift.zipkinCore import constants


class Endpoint(object):
    """
    :param ip: C{str} ip address
    :param port: C{int} port number
    :param service_name: C{str} service_name
    """

    def __init__(self, service_name, ip=None, port=0):
        if not ip:
            ip = socket.gethostbyname_ex(socket.gethostname())[2][0]
        self.ip = ip
        self.port = port
        self.service_name = service_name

#TODO
#__eq__, __ne__, __repr__


class TraceStack(object):
    def __init__(self):
        self.stack = []
        self.cur = None

    def child(self, name, endpoint=None):
        trace = self.cur.child(name, endpoint)
        self.stack.append(trace)
        self.cur = trace
        return trace

    def append(self, trace):
        self.stack.append(trace)
        self.cur = trace

    def pop(self):
        trace = self.stack.pop()
        try:
            cur = self.stack.pop()
            self.stack.append(cur)
            self.cur = cur
        except:
            self.cur = None
        return trace

    @property
    def current(self):
        return self.cur


class Trace(object):
    def __init__(self, name, trace_id=None, span_id=None,
                 parent_span_id=None, endpoint=None):
        self.name = name
        self.trace_id = trace_id or uniq_id()
        self.span_id = span_id or uniq_id()

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
        trace = self.__class__(name, trace_id=self.trace_id,
                               parent_span_id=self.span_id, endpoint=e)
        return trace

    def child(self, name, endpoint=None):
        trace = self.child_noref(name, endpoint)
        self._children.append(trace)
        return trace

    def children(self):
        return [y for x in self._children for y in x.children()] + [self]


class Annotation(object):
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

        return cls(name, timestamp, 'timestamp')

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
        return cls(name, value, 'string')

    @classmethod
    def bytes(cls, name, value):
        return cls(name, value, 'bytes')
