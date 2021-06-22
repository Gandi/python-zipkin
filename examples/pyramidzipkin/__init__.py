from pyramid.config import Configurator

# from sqlalchemy import engine_from_config

from .views import root, sleep_for


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""
    config = Configurator(settings=settings)
    config.include("zipkin.binding.pyramid")

    config.add_route("root", "/")
    config.add_route("sleep", "/sleep/{time}")
    config.add_view(root, route_name="root")
    config.add_view(sleep_for, route_name="sleep")

    return config.make_wsgi_app()
