from __future__ import print_function
import logging
import sys

from zipkin import append_trace, end_current_trace


log = logging.getLogger(__name__)
endpoints = {}


def before_cursor_execute(conn, cursor, statement, parameters, context,
                                                executemany):
    try:
        print('!'*80, file=sys.stderr)
        print(statement, file=sys.stderr)
        endpoint = endpoints.get(conn.engine)
        append_trace('SQL', endpoint=endpoint)
    except Exception as exc:
        print('?'*80, file=sys.stderr)
        print(exc, file=sys.stderr)
        log.exception('Unexpected exception while tracing SQL')


def after_cursor_execute(conn, cursor, statement, parameters, context,
                         executemany):
    try:
        end_current_trace()
    except Exception:
        log.exception('Unexpected exception while tracing SQL')


def dbapi_error(conn, cursor, statement, parameters, context, exception):
    try:
        end_current_trace()
    except Exception:
        log.exception('Unexpected exception while tracing SQL')
