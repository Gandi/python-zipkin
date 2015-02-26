import unittest
from mock import patch

from flask import Flask
from flask.views import View

import zipkin
from zipkin.binding.flask import bind as bind_zipkin

from ..utils import DummyClient, dummy_log


class Home(View):
    def dispatch_request(self):
        return "Guten Morgen!"


class Forbidden(View):
    def dispatch_request(self):
        return "Verboten!", 403


class FlaskApp(Flask):
    def __init__(self):
        super(FlaskApp, self).__init__(__name__)
        self.setup_url()
        self.setup_zipkin()

    def setup_zipkin(self):
        endpoint = zipkin.configure('My test flask application',
                                    {'zipkin.collector': 'www.remote.url',
                                     'zipkin.service_name': 'my app'})
        bind_zipkin(self, endpoint)

    def setup_url(self):
        self.add_url_rule('/', methods=['GET'],
                          view_func=Home.as_view(b'home'))
        self.add_url_rule('/interdit', methods=['GET'],
                          view_func=Forbidden.as_view(b'proibito'))


class FlaskAppTestCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super(FlaskAppTestCase, self).__init__(methodName)
        self.logger = patch('zipkin.binding.flask.events.log', dummy_log)

    def setUp(self):
        self.logger.start()
        DummyClient.reset()

        self.app = FlaskApp()
        self.client = self.app.test_client()

    def tearDown(self):
        self.logger.stop()

    def test_home(self):
        ret = self.client.get('/')
        self.assertEquals(ret.data, "Guten Morgen!")

        traces = DummyClient._client.messages
        self.assertEquals(len(traces), 1,
                          "There should be one trace for "
                          "the request just processed")
