import time

from pyramid.view import view_config
from pyramid.response import Response

from zipkin_pyramid import trace

import requests


def root(request):
    headers = {}
    subfunc()
    sleep()
    return Response('hello zipkin, %s' % str(headers))

def sleep_for(request):
    t = int(request.matchdict['time'])
    if t >= 1:
        print "sleeping 1"
        sleep(1)
        print "http://localhost:6543/sleep/%d" % (t - 1)
        ret = requests.get("http://localhost:6543/sleep/%d" % (t - 1))
        return Response(ret.text + "<br/>\nwaited 1sec")
    else:
        return Response("returned immediatly")

@trace("subfunc")
def subfunc():
    time.sleep(0.2)

@trace
def sleep(t = 0.4):
    time.sleep(t)
