import logging
from socket import timeout

from thriftpy.transport import TTransportException, TFramedTransportFactory
from thriftpy.rpc import make_client

from .util import base64_thrift_formatter
from .scribe import scribe_thrift


logger = logging.getLogger(__name__)

CONNECTION_RETRIES = [1, 10, 20, 50, 100, 200, 400, 1000]


class Client(object):

    host = None
    port = 9410
    _client = None
    _connection_attempts = 0
    # This is used in TSocket which divides by 1000 before passing it to
    # python socket. This is ms, do not trust socket.settimeout documentation.
    timeout = 50

    @classmethod
    def configure(cls, settings, prefix):
        cls.host = settings.get(prefix + 'collector')
        if prefix + 'collector.port' in settings:
            cls.port = int(settings[prefix + 'collector.port'])
        if prefix + 'collector.timeout' in settings:
            cls.timeout = int(settings[prefix + 'collector.timeout'])

    @classmethod
    def get_connection(cls):
        if not cls._client:
            cls._connection_attempts += 1

            max_retries = CONNECTION_RETRIES[-1]
            if ((cls._connection_attempts > max_retries) and
                    not ((cls._connection_attempts % max_retries) == 0)):
                return
            if ((cls._connection_attempts < max_retries) and
                    (cls._connection_attempts not in CONNECTION_RETRIES)):
                return

            try:
                cls._client = make_client(
                    scribe_thrift.Scribe, host=cls.host,
                    port=cls.port, timeout=cls.timeout,
                    trans_factory=TFramedTransportFactory())

                cls._connection_attempts = 0
            except TTransportException:
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
        if not cls.host:
            logger.debug('Zipkin tracing is disabled')
            return
        client = cls.get_connection()
        if client:
            messages = [base64_thrift_formatter(t, t.annotations)
                        for t in trace.children()]
            log_entries = [scribe_thrift.LogEntry('zipkin', message)
                           for message in messages]

            try:
                client.Log(messages=log_entries)
            except EOFError:
                cls._client = None
                logger.error('EOFError while logging a trace on zipkin '
                             'collector %s:%d' % (cls.host, cls.port))
            except timeout:
                cls._client = None
                logger.error('timeout when sending data or connecting to '
                             'collector %s:%d' % (cls.host, cls.port))
            except Exception:
                cls._client = None
                logger.exception('Unknown Exception while logging a trace on '
                                 'zipkin collector %s:%d' % (cls.host,
                                                             cls.port))
        else:
            logger.warn("Can't log zipkin trace, not connected")


def log(trace):
    Client.log(trace)
