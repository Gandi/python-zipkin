"""
Update python login to have trace_id and span_id available in formater.


.. important::

    To ensure the logger will properly log, the function
    :func:`zipkin.logging.install_logger_factory` must be call before logging


Example of python formatter:

::

    [formatter_generic]
    format = %(asctime)s %(levelname)-5.5s [%(trace_id)s][%(span_id)s] %(message)s

"""

import logging

from zipkin.api import get_current_trace


def record_factory_factory():
    old_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        trace = get_current_trace()
        record.trace_id = trace.trace_id if trace else None
        record.span_id = trace.span_id if trace else None
        return record

    def revert():
        logging.setLogRecordFactory(old_factory)
        return

    return record_factory, revert


def install_logger_factory():
    """
    Replace the logger factory to have the trace_id and span_id available

    in the logging metadata.
    """
    logger, revert = record_factory_factory()
    logging.setLogRecordFactory(logger)
    return revert
