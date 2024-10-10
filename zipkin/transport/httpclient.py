import logging

import requests
from requests.exceptions import Timeout, ConnectionError, ConnectTimeout

from ..util import base64_thrift_formatter_many


logger = logging.getLogger(__name__)


class Client:

    host = None
    port = 9411
    scheme = "http"
    _url = None
    _socket_timeout = 1000

    @classmethod
    def configure(cls, settings, prefix):
        cls.host = settings.get(prefix + "collector")
        if prefix + "collector.port" in settings:
            cls.port = int(settings[prefix + "collector.port"])
        if prefix + "collector.scheme" in settings:
            cls.scheme = settings[prefix + "collector.scheme"]
        if prefix + "transport.socket_timeout" in settings:
            cls._socket_timeout = int(settings[prefix + "transport.socket_timeout"])

        cls._url = "%s://%s:%s/api/v1/spans" % (cls.scheme, cls.host, cls.port)

    @classmethod
    def log(cls, trace):
        if cls._url is None:
            raise ValueError("Unconfigured client")
        payload = base64_thrift_formatter_many(trace)
        try:
            requests.post(
                cls._url,
                headers={"Content-Type": "application/x-thrift"},
                data=payload,
                timeout=cls._socket_timeout,
            )
        except ConnectTimeout:
            logger.error("Connect timeout while connecting to zipkin collector")
        except ConnectionError:
            logger.error("Cannot connect to zipkin collector")
        except Timeout:
            logger.error("Timeout while posting trace")
