import sys
from functools import wraps

from psycopg2.extensions import connection as _connection
from psycopg2.extensions import cursor as _cursor

from zipkin.api import get_current_trace
from zipkin.models import Annotation


class TraceConnection(_connection):
    """A connection that logs all queries to a zipkin."""

    def cursor(self, *args, **kwargs):
        kwargs.setdefault("cursor_factory", self.cursor_factory or TraceCursor)
        return super(TraceConnection, self).cursor(*args, **kwargs)


def trace_req(trace_name):
    def wrapper(fn):
        @wraps(fn)
        def wrapped(cursor, statement, vars=None):
            trace = None
            parent_trace = get_current_trace()
            if parent_trace:
                trace = parent_trace.child(trace_name)
                trace.record(Annotation.string("db.statement", statement))

                if vars:
                    if isinstance(vars, dict):
                        params = dict(
                            [
                                (key, getattr(param, "logged_value", param))
                                for key, param in vars.items()
                            ]
                        )
                    else:
                        params = [
                            getattr(param, "logged_value", param) for param in vars
                        ]

                    trace.record(Annotation.string("db.parameters", repr(params)))
                    trace.record(Annotation.string("span.kind", "client"))
                    trace.record(Annotation.server_send())

            try:
                fn(cursor, statement, vars)
            finally:
                if trace:
                    status = "OK" if sys.exc_info()[0] is None else "KO"
                    trace.record(Annotation.string("status", status))
                    trace.record(Annotation.server_recv())

        return wrapped

    return wrapper


class TraceCursor(_cursor):
    """A cursor that logs queries using its connection logging facilities."""

    @trace_req("SQL")
    def execute(self, query, vars=None):
        return super(TraceCursor, self).execute(query, vars)

    @trace_req("STORED PROCEDURE")
    def callproc(self, procname, vars=None):
        return super(TraceCursor, self).callproc(procname, vars)
