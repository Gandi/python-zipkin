from pyramid.view import view_config
from pyramid.response import Response
#from pyramid_zipkin._requests import requests


def root(request):
    #headers = requests(request, 'delay', endpoint='httpbin').get('http://httpbin.org/delay/1').json()
    headers = {}
    return Response('hello zipkin, %s' % str(headers))
