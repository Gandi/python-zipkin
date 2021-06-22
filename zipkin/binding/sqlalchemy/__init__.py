try:
    from .impl import bind
except ImportError as exc:
    import logging

    logging.getLogger(__name__).warn("SQLAlchemy not installed")

    def bind(*args, **kwargs):
        pass

    raise
