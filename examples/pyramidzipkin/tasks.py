import time

from celery import Celery

from zipkin.binding.celery import zipkin_init
from zipkin.client import Client

from zipkin.api import trace

#if __name__ == 'main':
#    Client.configure({'zipkin.collector': '127.0.0.1'})
zipkin_init()

app = Celery('tasks', broker='redis://localhost', backend='redis://localhost')

@app.task
def add(x, y):
    sleep(0.2)
    return x + y

@trace
def sleep(t):
    time.sleep(t)
    
