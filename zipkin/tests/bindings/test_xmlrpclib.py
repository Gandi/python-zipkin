from __future__ import absolute_import

import unittest
import multiprocessing as mp

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy

from time import time, sleep

import zipkin
from zipkin.thread import local
from zipkin.binding.xmlrpclib import bind as bind_zipkin

from ..utils import DummyClient, dummy_log

SERVERPORT = 18747


class XMLRPClibAppTestCase(unittest.TestCase):
    server = None

    def setUp(self):
        endpoint = zipkin.configure(
            "My test xmlrpclib application",
            {"zipkin.collector": "localhost", "zipkin.service_name": "my app"},
        )

        bind_zipkin(endpoint)

        server = SimpleXMLRPCServer(("localhost", SERVERPORT), allow_none=True)
        server.register_function(sleep)

        self.server = mp.Process(target=server.serve_forever)
        self.server.start()

        DummyClient.reset()

    def tearDown(self):
        if self.server and self.server.is_alive():
            self.server.terminate()

    def test_sleep(self):
        client = ServerProxy("http://localhost:%d/RPC2" % SERVERPORT, allow_none=True)

        start = time()
        client.sleep(0.1)
        end = time()
        delta = end - start

        dummy_log(local().current)

        self.assertGreater(delta, 0.101)

        traces = DummyClient._client.messages
        self.assertEqual(
            len(traces),
            1,
            "There should be one trace for " "the request just processed",
        )
