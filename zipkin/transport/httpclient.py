import requests

from ..util import base64_thrift_formatter_many


class Client(object):

    host = None
    port = 9411
    scheme = "http"
    _url = None

    @classmethod
    def configure(cls, settings, prefix):
        cls.host = settings.get(prefix + "collector")
        if prefix + "collector.port" in settings:
            cls.port = int(settings[prefix + "collector.port"])
        if prefix + "collector.scheme" in settings:
            cls.scheme = settings[prefix + "collector.scheme"]

        cls._url = "%s://%s:%s/api/v1/spans" % (cls.scheme, cls.host, cls.port)

    @classmethod
    def log(cls, trace):
        if cls._url is None:
            raise ValueError("Unconfigured client")
        payload = base64_thrift_formatter_many(trace)

        requests.post(
            cls._url,
            headers={"Content-Type": "application/x-thrift"},
            data=payload,
        )
