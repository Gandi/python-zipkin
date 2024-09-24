# export the API here
from .api import trace, get_current_trace, stack_trace, Trace

from .config import configure
from .logging import install_logger_factory
from .thread import local  # XXX remove me from here

install_logger_factory()

__version__ = "0.9.2"

__all__ = ["trace", "Trace", "get_current_trace", "stack_trace", "configure", "local"]
