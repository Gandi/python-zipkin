import logging

from scribe import scribe
from thrift.transport import TTransport, TSocket
from thrift.protocol import TBinaryProtocol

from zipkin.util import base64_thrift_formatter


logger = logging.getLogger(__name__)


class Client(object):

    host = 'localhost'
    port = 9410
    _client = None

    @classmethod
    def configure(cls, settings, prefix):
        cls.host = settings[prefix + 'collector']
        if prefix + 'collector.port' in settings:
            cls.port = int(settings[prefix + 'collector.port'])

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
            logger.error("Can't connect to zipkin collector %s:%d"
                         % (cls.host, cls.port))
        except Exception:
            cls._client = None
            logger.exception("Can't connect to zipkin collector %s:%d"
                             % (cls.host, cls.port))
        return cls._client

    @classmethod
    def log(cls, trace):
        if cls.ensure_connection():
            messages = [base64_thrift_formatter(t, t.annotations) for t in trace.children()]
            log_entries = [scribe.LogEntry('zipkin', message)for message in messages]

            try:
                cls._client.Log(messages=log_entries)
            except EOFError:
                cls._client = None
                logger.error("EOFError while logging a trace on zipkin collector %s:%d"
                             % (cls.host, cls.port))
            except Exception:
                cls._client = None
                logger.exception("Unknown Exception while logging a trace on zipkin collector %s:%d"
                                 % (cls.host, cls.port))


def log(trace):
    Client.log(trace)
