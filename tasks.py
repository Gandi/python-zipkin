from celery import Celery
from celery.signals import before_task_publish, task_prerun, task_postrun

from zipkin_celery import zipkin_init
from zipkin_pyramid.client import Client

if __name__ == 'main':
    Client.configure({'zipkin.collector': '127.0.0.1'})
    zipkin_init()

app = Celery('tasks', broker='redis://localhost', backend='redis://localhost')

@app.task
def add(x, y):
    return x + y


