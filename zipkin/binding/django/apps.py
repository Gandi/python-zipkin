"""
Django App to trace call with zipkin.


Usage:

You need to add this in your django settings.

::

    ZIPKIN_SERVICE_NAME = "my-service-name"
    ZIPKIN_COLLECTOR = "zipkin.localdomain"  # hostname of the zipkin server
    ZIPKIN_ENV = "dev"  # Environment
    ZIPKIN_BINDINGS = ["requests"]  # List of library to patch/attach

    INSTALLED_APPS = [
        ...,
        "zipkin.binding.django",
        ...
    ]


"""

from django.conf import settings
from django.apps import AppConfig
from zipkin.config import configure


def get_settings():
    zk_settings = {
        "zipkin.transport": getattr(settings, "ZIPKIN_TRANSPORT", "scribe"),
        "zipkin.collector": settings.ZIPKIN_COLLECTOR,
        "zipkin.service_name": settings.ZIPKIN_SERVICE_NAME,
        "zipkin.env": settings.ZIPKIN_ENV,
    }
    if hasattr(settings, "ZIPKIN_COLLECTOR_PORT"):
        zk_settings["zipkin.collector.port"] = settings.ZIPKIN_COLLECTOR_PORT
    if hasattr(settings, "ZIPKIN_COLLECTOR_SCHEME"):
        zk_settings["zipkin.collector.scheme"] = settings.ZIPKIN_COLLECTOR_SCHEME
    if hasattr(settings, "ZIPKIN_TRANSPORT_ASYNC"):
        zk_settings["zipkin.transport.async"] = settings.ZIPKIN_TRANSPORT_ASYNC

    return zk_settings


class ZipkinConfig(AppConfig):
    """
    Configure zipkin from django settings.
    """

    name = "zipkin"
    service_name = ""

    def ready(self):

        bindings = []  # settings.ZIPKIN_BINDINGS
        appsettings = get_settings()
        ZipkinConfig.service_name = "%s-%s" % (
            settings.ZIPKIN_SERVICE_NAME,
            settings.ZIPKIN_ENV,
        )
        configure(
            appsettings["zipkin.service_name"],
            appsettings,
            use_celery="celery" in bindings,
            use_requests="request" in bindings,
            use_xmlrpclib="xmlrpclib" in bindings,
        )
