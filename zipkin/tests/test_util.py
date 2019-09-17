from __future__ import absolute_import

import unittest
import base64
import binascii

from ..models import Trace
from ..util import base64_thrift_formatter, int_or_none


class TestClient(unittest.TestCase):
    def test_format_64bit_traceid(self):
        _64bit_trace_id = 'b1119a5629b4cb7f'
        trace = Trace('foobar', trace_id=int_or_none(_64bit_trace_id))
        annotations = []
        data = base64_thrift_formatter(trace, annotations)
        data = base64.b64decode(data)

        self.assertIn(binascii.unhexlify(_64bit_trace_id), data)
