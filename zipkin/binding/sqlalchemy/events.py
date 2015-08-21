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

        if not parent_trace:
            log.error('No parent found while tracing SQL')
            return

        cursor.trace = parent_trace.child('SQL', endpoint=endpoint)
        cursor.trace.record(Annotation.string('query', statement))

        if parameters:
            if isinstance(parameters, dict):
                parameters = dict([(key, getattr(param, 'logged_value', param))
                                   for key, param in parameters.items()])
            else:
                parameters = [getattr(param, 'logged_value', param)
                              for param in parameters]

        cursor.trace.record(Annotation.string('parameters', repr(parameters)))
        cursor.trace.record(Annotation.server_recv())
    except Exception:
        log.exception('Unexpected exception while tracing SQL')


def after_cursor_execute(conn, cursor, statement, parameters, context,
                         executemany):
    if not hasattr(cursor, 'trace'):
        return
    try:
        context.trace.record(Annotation.string('status', 'OK'))
        context.trace.record(Annotation.server_send())
    except Exception:
        log.exception('Unexpected exception while tracing SQL')


def dbapi_error(conn, cursor, statement, parameters, context, exception):
    if not hasattr(cursor, 'trace'):
        return
    try:
        cursor.trace.record(Annotation.string('status', 'KO'))
        cursor.trace.record(Annotation.server_send())
    except Exception:
        log.exception('Unexpected exception while tracing SQL')
