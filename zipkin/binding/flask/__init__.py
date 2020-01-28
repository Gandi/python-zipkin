try:
    from .impl import bind
except ImportError as exc:
    import logging
    logging.getLogger(__name__).warning('Flask not installed')

    def bind(*args, **kwargs):
        pass

    raise
