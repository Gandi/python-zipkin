from __future__ import print_function
import sys

try:
    print('>'*80, file=sys.stderr)
    from .impl import bind
except ImportError as exc:
    import logging
    print(exc, file=sys.stderr)
    import traceback
    traceback.print_stack()
    logging.getLogger(__name__).warn('SQLAlchemy not installed')

    def bind(*args, **kwargs):
        pass

    raise
