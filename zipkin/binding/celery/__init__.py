try:
    from .impl import bind
except ImportError as exc:
    import logging
    logging.getLogger(__name__).warning('Celery not installed')

    def bind(*arg, **kwarg):
        pass
