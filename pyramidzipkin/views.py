import time

from pyramid.view import view_config
from pyramid.response import Response

from zipkin_pyramid import trace

import requests

from tasks import add

def root(request):
    headers = {}
    subfunc()
    sleep()
    ret = add.delay(4, 4).get()
    return Response('hello zipkin, %s %d' % (str(headers), ret))

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
