from __future__ import absolute_import

import re
import logging
from xmlrpc import client as xmlrpclib

from zipkin import local
from zipkin.models import Annotation, Endpoint
from zipkin.util import hex_str


log = logging.getLogger(__name__)

_parse_method_name = re.compile(r"<methodName>([^<]*)</methodName>", re.I)


class MonkeyTransport(xmlrpclib.Transport):
    """Monkey patched version of xmlrpclib.Transport to plug zipkin in"""

    __origin = xmlrpclib.Transport

    def request(self, host, handler, request_body, verbose=0):
        try:
            https = isinstance(self, xmlrpclib.SafeTransport)
            protocol = "https://" if https else "http://"
            target = "%s%s%s" % (protocol, host, handler)

            match = _parse_method_name.search(request_body)
            method = match.group(1) if match else None

            parent_trace = local().current
            self._trace = parent_trace.child("xmlrpclib")

            self._trace.record(Annotation.string("uri", target))
            if method:
                self._trace.record(Annotation.string("method", method))
            self._trace.record(Annotation.server_recv())
        except Exception as exc:
            log.error(repr(exc))

        try:
            return self.__origin.request(self, host, handler, request_body, verbose)
        finally:
            try:
                self._trace.record(Annotation.server_send())
            except:
                pass

    def send_host(self, connection, host):
        ret = self.__origin.send_host(self, connection, host)
        try:
            forward = self.trace.child_noref("subservice")
            connection.putheader("X-B3-TraceId", hex_str(forward.trace_id))
            connection.putheader("X-B3-SpanId", hex_str(forward.span_id))
            if forward.parent_span_id is not None:
                connection.putheader(
                    "X-B3-ParentSpanId", hex_str(forward.parent_span_id)
                )
        finally:
            return ret


def bind(endpoint=None):
    log.info("Binding zipkin to xmlrpclib")
    if not endpoint:
        endpoint = Endpoint("xmlrpc")

    xmlrpclib.Transport = MonkeyTransport

    log.info("zipkin bound to xmlrpclib")


def unbind():
    xmlrpclib.Transport = MonkeyTransport.__origin
