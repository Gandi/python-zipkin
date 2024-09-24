from __future__ import unicode_literals, absolute_import

import os
import unittest
from unittest.mock import patch

from flask import Flask
from flask.views import View
import requests

import zipkin
from ...binding.flask import bind as bind_zipkin
from ...binding.requests import bind as bind_requests
from ...models import Endpoint, Trace
from ...thread import local

from ..utils import DummyClient, dummy_log, Server


class Home(View):
    def dispatch_request(self):
        return "Guten Morgen!"


class Forbidden(View):
    def dispatch_request(self):
        return "Verboten!", 403


class FlaskApp(Flask):
    def __init__(self, *args, **kwargs):
        super(FlaskApp, self).__init__(__name__)
        self.setup_url()
        self.setup_zipkin()

    def setup_zipkin(self):
        endpoint = zipkin.configure(
            "My test flask application",
            {"zipkin.collector": "localhost", "zipkin.service_name": "my app"},
        )
        bind_zipkin(self, endpoint)

    def setup_url(self):
        self.add_url_rule("/", methods=["GET"], view_func=Home.as_view(str("home")))
        self.add_url_rule(
            "/interdit", methods=["GET"], view_func=Forbidden.as_view(str("proibito"))
        )


class FlaskAppTestCase(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        super(FlaskAppTestCase, self).__init__(methodName)
        self.logger = patch("zipkin.binding.flask.events.log", dummy_log)

    def setUp(self):
        self.logger.start()
        DummyClient.reset()

        self.app = FlaskApp()
        self.client = self.app.test_client()

    def tearDown(self):
        self.logger.stop()

    def test_home(self):
        ret = self.client.get("/")
        self.assertEqual(ret.data, b"Guten Morgen!")

        traces = DummyClient._client.messages
        self.assertEqual(
            len(traces),
            1,
            "There should be one trace for " "the request just processed",
        )


class FlaskAppRealServerTestCase(unittest.TestCase):
    def __init__(self, methodName="runTest"):
        super(FlaskAppRealServerTestCase, self).__init__(methodName)
        self.logger = patch("zipkin.binding.flask.events.log", dummy_log)
        bind_requests()

    def setUp(self):
        self.http_proxy = os.environ.pop("http_proxy", None)
        self.https_proxy = os.environ.pop("https_proxy", None)

        self.logger.start()
        DummyClient.reset()

        self.app = Server(FlaskApp())
        self.app.start()

    def tearDown(self):
        self.logger.stop()
        self.app.stop()

        if self.http_proxy:
            os.environ["http_proxy"] = self.http_proxy
        if self.https_proxy:
            os.environ["https_proxy"] = self.https_proxy

    def test_home_no_headers(self):
        ret = requests.get(self.app.url)
        self.assertEqual(ret.text, "Guten Morgen!")

        traces = DummyClient._client.messages
        self.assertEqual(
            len(traces),
            1,
            "There should be one trace for " "the request just processed",
        )

    def test_home_headers(self):
        endpoint = Endpoint("127.0.0.1", 0, "RequestsWithContextTestCase")
        trace = Trace("flask", None, None, None, endpoint=endpoint)
        local().replace(trace)

        ret = requests.get(self.app.url)
        self.assertEqual(ret.text, "Guten Morgen!")

        traces = DummyClient._client.messages
        self.assertEqual(
            len(traces),
            1,
            "There should be one trace for " "the request just processed",
        )
        self.assertEqual(
            traces[0].trace_id,
            trace.trace_id,
            "TraceId should be read from client if present",
        )
