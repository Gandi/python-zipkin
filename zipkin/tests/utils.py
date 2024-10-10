from __future__ import unicode_literals

import threading

import json
from wsgiref.simple_server import make_server, WSGIRequestHandler
from wsgiref.handlers import SimpleHandler
from urllib.parse import urljoin
from flask import Flask, request
from flask.views import View


class Headers(View):
    def dispatch_request(self):
        return json.dumps({"headers": dict(request.headers)})


class FlaskApp(Flask):
    def __init__(self, *args, **kwargs):
        super(FlaskApp, self).__init__(__name__)
        self.setup_url()

    def setup_url(self):
        self.add_url_rule(
            "/headers", methods=["GET"], view_func=Headers.as_view(str("headers"))
        )


httpbin_app = FlaskApp()


class ScribeClient:
    def __init__(self):
        self.messages = []

    def Log(self, messages):
        self.messages.append(messages)


class DummyClient:
    _client = ScribeClient()

    @classmethod
    def configure(cls, settings, prefix):
        pass

    @classmethod
    def get_connection(cls):
        return cls._client

    @classmethod
    def log(cls, trace):
        return cls._client.Log(trace)

    @classmethod
    def reset(cls):
        cls._client = ScribeClient()


def dummy_log(trace):
    DummyClient.log(trace)


class ServerHandler(SimpleHandler):

    server_software = "HTTPBIN/0.1.0"
    http_version = "1.1"

    def cleanup_headers(self):
        SimpleHandler.cleanup_headers(self)
        self.headers["Connection"] = "Close"

    def close(self):
        try:
            self.request_handler.log_request(
                self.status.split(" ", 1)[0], self.bytes_sent
            )
        finally:
            SimpleHandler.close(self)


class Handler(WSGIRequestHandler):
    def handle(self):
        """Handle a single HTTP request"""

        self.raw_requestline = self.rfile.readline()
        if not self.parse_request():  # An error code has been sent, just exit
            return

        handler = ServerHandler(
            self.rfile, self.wfile, self.get_stderr(), self.get_environ()
        )
        handler.request_handler = self  # backpointer for logging
        handler.run(self.server.get_app())

    def get_environ(self):
        """
        wsgiref simple server adds content-type text/plain to everything, this
        removes it if it's not actually in the headers.
        """
        # Note: Can't use super since this is an oldstyle class in python 2.x
        environ = WSGIRequestHandler.get_environ(self).copy()
        if self.headers.get("content-type") is None:
            del environ["CONTENT_TYPE"]
        return environ


class Server(threading.Thread):
    """
    HTTP server running a WSGI application in its own thread.
    """

    def __init__(self, application=httpbin_app, host="127.0.0.1", port=0, **kwargs):
        self.app = application
        self._server = make_server(
            host, port, self.app, handler_class=Handler, **kwargs
        )
        self.host = self._server.server_address[0]

        self.port = self._server.server_address[1]
        self.protocol = "http"

        super(Server, self).__init__(
            name=self.__class__,
            target=self._server.serve_forever,
        )

    def __del__(self):
        self.stop()

    def __add__(self, other):
        return self.url + other

    def stop(self):
        self._server.shutdown()

    @property
    def url(self):
        return "{0}://{1}:{2}".format(self.protocol, self.host, self.port)

    def join(self, url, allow_fragments=True):
        return urljoin(self.url, url, allow_fragments=allow_fragments)
