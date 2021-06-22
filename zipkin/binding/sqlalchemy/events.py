import logging

from zipkin import get_current_trace
from zipkin.models import Annotation

log = logging.getLogger(__name__)
endpoints = {}


def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    try:
        endpoint = endpoints.get(conn.engine)
        parent_trace = get_current_trace()

        if not parent_trace:
            log.warning("No parent found while tracing SQL")
            return

        try:
            context.trace = parent_trace.child("SQL", endpoint=endpoint)
            abstract = context
        except AttributeError:
            cursor.trace = parent_trace.child("SQL", endpoint=endpoint)
            abstract = cursor

        abstract.trace.record(Annotation.string("db.statement", statement))

        if parameters:
            if isinstance(parameters, dict):
                parameters = dict(
                    [
                        (key, getattr(param, "logged_value", param))
                        for key, param in parameters.items()
                    ]
                )
            else:
                parameters = [
                    getattr(param, "logged_value", param) for param in parameters
                ]

        abstract.trace.record(Annotation.string("db.parameters", repr(parameters)))
        abstract.trace.record(Annotation.string("span.kind", "client"))
        abstract.trace.record(Annotation.server_recv())
    except Exception:
        log.exception("Unexpected exception while tracing SQL")


def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    if not hasattr(context, "trace") and not hasattr(cursor, "trace"):
        return
    abstract = context if hasattr(context, "trace") else cursor

    try:
        abstract.trace.record(Annotation.string("status", "OK"))
        abstract.trace.record(Annotation.server_send())
    except Exception:
        log.exception("Unexpected exception while tracing SQL")


def dbapi_error(conn, cursor, statement, parameters, context, exception):
    if not hasattr(context, "trace") and not hasattr(cursor, "trace"):
        return
    abstract = context if hasattr(context, "trace") else cursor

    try:
        abstract.trace.record(Annotation.string("status", "KO"))
        abstract.trace.record(Annotation.server_send())
    except Exception:
        log.exception("Unexpected exception while tracing SQL")
