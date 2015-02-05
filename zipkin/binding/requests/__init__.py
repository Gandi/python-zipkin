try:
    from .impl import bind
except ImportError as exc:
    import logging
    logging.getLogger(__name__).warn('requests not installed')

    def bind():
        pass
