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

    return record_factory


def install_logger_factory():
    logging.setLogRecordFactory(record_factory_factory())
