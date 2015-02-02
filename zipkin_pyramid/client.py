import logging

from scribe import scribe
from thrift.transport import TTransport, TSocket
from thrift.protocol import TBinaryProtocol

from zipkin.util import base64_thrift_formatter


logger = logging.getLogger('gandi.whateber')

class Client(object):

    host = 'localhost'
    port = 9410
    _client = None

    @classmethod
    def configure(cls, settings):
        cls.host = settings['zipkin.collector']
        if 'zipkin.collector.port' in settings:
            cls.port = int(settings['zipkin.collector.port'])

    @classmethod
    def ensure_connection(cls):
        if cls._client:
            return cls._client
        try:
            socket = TSocket.TSocket(host=cls.host, port=cls.port)
            transport = TTransport.TFramedTransport(socket)
            protocol = TBinaryProtocol.TBinaryProtocol(trans=transport, strictRead=False, strictWrite=False)
            cls._client = scribe.Client(protocol)
            transport.open()
        except TTransport.TTransportException:
            cls._client = None
            logger.exception("Can't connect to zipkin collector")
        return cls._client

    @classmethod
    def log(cls, trace):
        if cls.ensure_connection():
            messages = [base64_thrift_formatter(t, t.annotations) for t in trace.children()]
            log_entries = [scribe.LogEntry('zipkin', message) for message in messages]

            try:
                cls._client.Log(messages=log_entries)
            except TTransport.TTransportException:
                cls._client = None


def log(trace):
    Client.log(trace)
