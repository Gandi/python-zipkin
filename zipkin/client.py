import importlib


class Local:
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
    try:
        Client.log(trace)
    except Exception as err:
        log.error("Unexpected Exception while sending trace: %s", err)
