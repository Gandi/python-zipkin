import math
import time

from .util import uniq_id
from ._thrift.zipkinCore import constants

class Endpoint(object):
    def __init__(self, ip, port, service_name):
        """
        @param ip: C{str} ip address
        @param port: C{int} port number
        @param service_name: C{str} service_name
        """
        self.ip = ip
        self.port = port
        self.service_name = service_name
    def child(self, name):
        return self.__class__(self.ip, self.port, name)

#TODO
#__eq__, __ne__, __repr__

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
        trace = self.__class__(
                    name, trace_id=self.trace_id, parent_span_id=self.span_id, endpoint=e)
        return trace

    def child(self, name, endpoint = None):
        trace = self.child_noref(name, endpoint)
        self._children.append(trace)
        return trace

    def children(self):
        return [y for x in self._children for y in x.children()] + [self]


class Annotation(object):
    def __init__(self, name, value, annotation_type, endpoint=None):
        """
        @param name: C{str} name of this annotation.

        @param value: A value of the appropriate type based on
            C{annotation_type}.

        @param annotation_type: C{str} the expected type of our C{value}.

        @param endpoint: An optional L{IEndpoint} provider to associate with
            this annotation or C{None}
        """
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




