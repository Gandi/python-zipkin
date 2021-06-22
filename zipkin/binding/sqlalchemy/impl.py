import logging


from sqlalchemy import event

from . import events
from zipkin.models import Endpoint

log = logging.getLogger(__name__)


def bind(engine, endpoint=None):

    log.info("Binding zipkin to SQLALchemy")
    if not endpoint:
        endpoint = Endpoint("SQL")

    events.endpoints[engine] = endpoint
    event.listen(engine, "before_cursor_execute", events.before_cursor_execute)
    event.listen(engine, "after_cursor_execute", events.after_cursor_execute)
    # event.listen(engine, 'dbapi_error', events.dbapi_error)
    log.info("zipkin bound to SQLALchemy")
