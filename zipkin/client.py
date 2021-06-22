import importlib


class Local(object):
    local_ip = None


Client = None


def configure(settings, prefix):
    global Client
    transport = settings.get(prefix + "transport", "scribe")
    assert transport in ("http", "scribe")
    driver = importlib.import_module(
        "zipkin.transport.{}client".format(transport),
    )
    Client = driver.Client  # noqa
    Client.configure(settings, prefix)


def log(trace):
    Client.log(trace)
