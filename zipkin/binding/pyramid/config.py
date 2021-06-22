from pyramid.events import ContextFound
from pyramid.tweens import INGRESS

from .pyramidhook import wrap_request


def includeme(config):
    """Include the zipkin definitions"""

    # Attach the subscriber a couple of times, this allow to start logging as
    # early as possible. Later calls on the same request will enhance the more
    # we proceed through the stack (after authentication, after router, ...)
    config.add_tween("zipkin.binding.pyramid.pyramidhook.tween_factory", under=INGRESS)
    zipkin_wrapper = wrap_request(config.registry)
    if zipkin_wrapper:
        config.add_subscriber(zipkin_wrapper, ContextFound)
