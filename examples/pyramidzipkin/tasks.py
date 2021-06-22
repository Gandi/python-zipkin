import time

from celery import Celery

from zipkin.client import Client

from zipkin.api import trace

app = Celery("tasks", broker="redis://localhost", backend="redis://localhost")


@app.task
def add(x, y):
    sleep(0.2)
    return x + y


@trace
def sleep(t):
    time.sleep(t)
