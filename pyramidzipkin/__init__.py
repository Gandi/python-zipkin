from pyramid.config import Configurator

#from sqlalchemy import engine_from_config

from .views import root

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('zipkin_pyramid')

    config.add_route('root', '/')
    config.add_view(root, route_name='root')

    return config.make_wsgi_app()
