from __future__ import absolute_import

import unittest
import os

import requests

from ..utils import Server
from ...binding.requests import bind as bind_requests
from ...models import Endpoint, Trace
from ...thread import local
from ...util import hex_str


def request_json(response):
    """Signature for response.json varies between
    requests versions, this wrapper finds out which api
    to use
    """
    if hasattr(response.json, "__call__"):
        return response.json()
    else:
        return response.json


class RequestsTestCase(unittest.TestCase):
    """
    This test class starts up a HttpBin instance locally for test-purpose
    """

    def __init__(self, methodName="runTest"):
        super(RequestsTestCase, self).__init__(methodName)
        bind_requests()

    def setUp(self):
        self.http_proxy = os.environ.pop("http_proxy", None)
        self.https_proxy = os.environ.pop("https_proxy", None)

        self.httpbin = Server()
        self.httpbin.start()

    def tearDown(self):
        self.httpbin.stop()
        if self.http_proxy:
            os.environ["http_proxy"] = self.http_proxy
        if self.https_proxy:
            os.environ["https_proxy"] = self.https_proxy


class RequestsNoContextTestCase(RequestsTestCase):
    def test_http_headers_no_context(self):
        resp = requests.get(self.httpbin.url + "/headers")
        headers = request_json(resp)

        self.assertEqual(
            headers.get("X-B3-TraceId", None),
            None,
            "There should be no B3 headers if context " "is not present",
        )


class RequestsWithContextTestCase(RequestsTestCase):
    def setUp(self):
        super(RequestsWithContextTestCase, self).setUp()

        endpoint = Endpoint("127.0.0.1", 0, "RequestsWithContextTestCase")
        self.trace = Trace("requests", None, None, None, endpoint=endpoint)
        local().replace(self.trace)

    def tearDown(self):
        super(RequestsWithContextTestCase, self).tearDown()
        local().reset()

    def test_http_headers_context(self):
        resp = requests.get(self.httpbin.url + "/headers")
        headers = request_json(resp)["headers"]

        self.assertEqual(
            headers.get("X-B3-Traceid", None),
            hex_str(self.trace.trace_id),
            "There should be B3 headers if context is present",
        )
