import logging

from zipkin import get_current_trace
from zipkin.models import Annotation

log = logging.getLogger(__name__)
endpoints = {}


def before_cursor_execute(conn, cursor, statement, parameters, context,
                          executemany):
    try:
        endpoint = endpoints.get(conn.engine)
        parent_trace = get_current_trace()
        context.trace = parent_trace.child('SQL', endpoint=endpoint)
        context.trace.record(Annotation.string('query', statement))
        context.trace.record(Annotation.string('parameters', repr(parameters)))
        context.trace.record(Annotation.server_recv())
    except Exception:
        log.exception('Unexpected exception while tracing SQL')


def after_cursor_execute(conn, cursor, statement, parameters, context,
                         executemany):
    try:
        context.trace.record(Annotation.string('status', 'OK'))
        context.trace.record(Annotation.server_send())
    except Exception:
        log.exception('Unexpected exception while tracing SQL')


def dbapi_error(conn, cursor, statement, parameters, context, exception):
    try:
        cursor.trace.record(Annotation.string('status', 'KO'))
        cursor.trace.record(Annotation.server_send())
    except Exception:
        log.exception('Unexpected exception while tracing SQL')
