# flake8: noqa
try:
    from requests.packages.urllib3.packages.six.moves import range

except ImportError:
    """Remove embedded version of six from request.packages v0.14...
    Missing six.moves.range
    """

    import sys
    import os.path
    import inspect

    try:
        import requests.packages

        if "six.moves" in sys.modules:
            del sys.modules["six.moves"]
            dirname = os.path.dirname(inspect.getfile(requests.packages))
            if dirname in sys.path:
                sys.path.remove(dirname)
    except ImportError:
        pass

    import six.moves
