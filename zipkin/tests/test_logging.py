import logging
import unittest
from unittest.mock import patch

from zipkin.api import Trace, get_current_trace, stack_trace
from zipkin.logging import install_logger_factory
from zipkin.models import Trace as TraceModel


def log_message():
    logger = logging.getLogger()
    logger.info("I am a dummy")


class TestLogging(unittest.TestCase):
    def setUp(self):
        self.revert = install_logger_factory()

    def tearDown(self):
        self.revert()

    @patch("logging.Logger.handle")
    def test_no_trace_in_stack(self, mock_handle):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        log_message()

        self.assertTrue(mock_handle.called)

        log_record = mock_handle.call_args[0][0]

        self.assertIn("trace_id", log_record.__dict__)
        self.assertIsNone(log_record.trace_id)
        self.assertIn("span_id", log_record.__dict__)
        self.assertIsNone(log_record.span_id)

        formatter = logging.Formatter("[%(trace_id)s] [%(span_id)s] %(message)s")
        formatted_message = formatter.format(log_record)
        self.assertEqual(formatted_message, "[None] [None] I am a dummy")

    @patch("logging.Logger.handle")
    def test_trace_in_stack_log_with_trace(self, mock_handle):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        stack_trace(TraceModel("root"))  # insane call
        with Trace("my"):
            assert get_current_trace()
            log_message()

        self.assertTrue(mock_handle.called)

        log_record = mock_handle.call_args[0][0]

        self.assertIn("trace_id", log_record.__dict__)
        self.assertIsNotNone(log_record.trace_id)

        formatter = logging.Formatter("[%(trace_id)s] [%(span_id)s] %(message)s")
        formatted_message = formatter.format(log_record)
        self.assertEqual(
            formatted_message,
            "[%s] [%s] I am a dummy" % (log_record.trace_id, log_record.span_id),
        )
