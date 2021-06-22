try:
    from .impl import bind, request_adapter
except ImportError as exc:
    import logging

    logging.getLogger(__name__).warn("requests not installed")

    def bind():
        pass

    def request_adapter(adapter):
        return adapter
