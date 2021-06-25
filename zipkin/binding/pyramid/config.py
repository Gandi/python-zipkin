def includeme(config):
    """Include the zipkin definitions"""

    # Attach the subscriber a couple of times, this allow to start logging as
    # early as possible. Later calls on the same request will enhance the more
    # we proceed through the stack (after authentication, after router, ...)
    config.include(".pyramidhook")
