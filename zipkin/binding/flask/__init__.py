try:
    from .impl import bind
except ImportError as exc:
    import logging

    logging.getLogger(__name__).warn("Flask not installed")

    def bind(*args, **kwargs):
        pass

    raise
