import errno
import logging
import socket
import struct
from io import BytesIO

from thriftpy2.protocol import TBinaryProtocolFactory
from thriftpy2.protocol.binary import write_message_begin, write_val
from thriftpy2.thrift import TClient, TMessageType, TType
from thriftpy2.transport import TFramedTransportFactory, TSocket, TTransportException

from ..client import Local
from ..util import base64_thrift_formatter
from .scribe import scribe_thrift

logger = logging.getLogger(__name__)

CONNECTION_RETRIES = [1, 10, 20, 50, 100, 200, 400, 1000]

try:
    MSG_NOSIGNAL = socket.MSG_NOSIGNAL
except:
    MSG_NOSIGNAL = 16384  # python2


class TNonBlockingSocket(TSocket):
    def _init_sock(self):
        super(TNonBlockingSocket, self)._init_sock()

        # 1M sendq buffer
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024)

        self.sock.setblocking(False)

    def open(self):
        self._init_sock()

        addr = self.unix_socket or (self.host, self.port)
        status = self.sock.connect_ex(addr)
        try:
            Local.local_ip = self.sock.getsockname()[0]
        except Exception:
            pass

        if status not in [errno.EINPROGRESS, errno.EALREADY]:
            raise IOError(
                "connection attempt on a non-clean socket", errno.errorcode[status]
            )

    def write(self, buff):
        # First ensure our incoming end is always empty
        self.read_all()

        # Then actually try to write to socket
        try:
            # We are a library, we can't just set sighandlers. But we don't
            # want SIGPIPE if peer has gone away either. We better set
            # MSG_NOSIGNAL to avoid that.
            # If peer has disconnected, then a errno.EPIPE will raise, and
            # will be catched on the uppper layer

            self.sock.sendall(buff, MSG_NOSIGNAL)
        except socket.error as e:
            if e.errno not in [
                errno.EINPROGRESS,  # Not connected yet
                errno.EWOULDBLOCK,
            ]:  # write buffer full
                # In all other cases, raise.
                raise

            # If not yet connected or write buffer is full, silently drop.

    def read_all(self):
        """
        Flush incoming buffer
        """
        try:
            receiving = " "
            while len(receiving) > 0:  # socket.error.errno.EAGAIN will exit this
                receiving = self.sock.recv(1024)
        except socket.error as e:
            # if EAGAIN or EWOULDBLOCK, then there is nothing to read
            if e.errno not in [errno.EAGAIN, errno.EWOULDBLOCK]:
                # Otherwise that's an error.
                raise

            return  # No more data to read, or connection is not ready

    def read(self, _):
        """
        Mock response, we don't care about results. We never actually read
        them. But we don't want client to wait for server to reply.
        """
        buffer = BytesIO()
        seq_id = 0  # Sequence id is never compared to message.
        write_message_begin(buffer, "Log_result", TMessageType.REPLY, seq_id)

        response = scribe_thrift.Scribe.Log_result(success=scribe_thrift.ResultCode.OK)
        write_val(buffer, TType.STRUCT, response)

        out = buffer.getvalue()

        # Framed message, starts with length of message.
        return struct.pack("!i", len(out)) + out


def make_client(
    service,
    host,
    port,
    proto_factory=TBinaryProtocolFactory(),
    trans_factory=TFramedTransportFactory(),
    socket_factory=TNonBlockingSocket,
    socket_timeout=1000,
):

    socket = socket_factory(host, port, socket_timeout=socket_timeout)
    transport = trans_factory.get_transport(socket)
    protocol = proto_factory.get_protocol(transport)
    transport.open()
    return TClient(service, protocol)


class Client:

    host = None
    port = 9410
    _client = None
    _connection_attempts = 0
    _socket_factory = TNonBlockingSocket
    _socket_timeout = 1000

    @classmethod
    def configure(cls, settings, prefix):
        cls.host = settings.get(prefix + "collector")
        if prefix + "collector.port" in settings:
            cls.port = int(settings[prefix + "collector.port"])
        if prefix + "transport.async" in settings:
            if settings[prefix + "transport.async"].lower() == "false":
                cls._socket_factory = TSocket

        if prefix + "transport.socket_timeout" in settings:
            cls._socket_timeout = int(settings[prefix + "transport.socket_timeout"])

    @classmethod
    def get_connection(cls):
        if not cls._client:
            cls._connection_attempts += 1

            max_retries = CONNECTION_RETRIES[-1]
            if (cls._connection_attempts > max_retries) and not (
                (cls._connection_attempts % max_retries) == 0
            ):
                return
            if (cls._connection_attempts < max_retries) and (
                cls._connection_attempts not in CONNECTION_RETRIES
            ):
                return

            try:
                cls._client = make_client(
                    scribe_thrift.Scribe,
                    host=cls.host,
                    port=cls.port,
                    socket_factory=cls._socket_factory,
                    socket_timeout=cls._socket_timeout,
                )

                cls._connection_attempts = 0
            except TTransportException:
                cls._client = None
                logger.error(
                    "Can't connect to zipkin collector %s:%d" % (cls.host, cls.port)
                )
            except Exception:
                cls._client = None
                logger.exception(
                    "Can't connect to zipkin collector %s:%d" % (cls.host, cls.port)
                )
        return cls._client

    @classmethod
    def log(cls, trace):
        if not cls.host:
            logger.debug("Zipkin tracing is disabled")
            return

        logger.info("logging trace %s", trace.trace_id)

        unknown = (
            "Unknown Exception while logging a trace on "
            "zipkin collector %s:%d" % (cls.host, cls.port)
        )

        client = cls.get_connection()
        if client:
            try:
                messages = [
                    base64_thrift_formatter(t, t.annotations) for t in trace.children()
                ]
                log_entries = [
                    scribe_thrift.LogEntry("zipkin", message) for message in messages
                ]
            except ValueError:
                logger.exception("Error while serializing trace")
                return

            try:
                client.Log(messages=log_entries)
            except EOFError:
                cls._client = None
                logger.error(
                    "EOFError while logging a trace on zipkin "
                    "collector %s:%d" % (cls.host, cls.port)
                )
            except socket.error as err:
                cls._client = None
                if err.errno == errno.EPIPE:
                    logger.error(
                        "Broken pipe while logging a trace "
                        "on zipkin collector %s:%d",
                        cls.host,
                        cls.port,
                    )
                else:
                    logger.exception(unknown)
            except Exception:
                cls._client = None
                logger.exception(unknown)
        else:
            logger.warning("Can't log zipkin trace, not connected")

    @classmethod
    def disconnect(cls):
        if cls._client:
            cls._client.close()
