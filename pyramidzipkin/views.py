from pyramid.view import view_config
from pyramid.response import Response

from zipkin_pyramid import trace

import time


def root(request):
    headers = {}
    subfunc()
    sleep()
    return Response('hello zipkin, %s' % str(headers))

@trace("subfunc")
def subfunc():
    time.sleep(0.2)

@trace
def sleep():
    time.sleep(0.4)
