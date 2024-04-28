# from __future__ import absolute_import, unicode_literals
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cfabib.settings')

app = Celery('cfabib')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# from celery import Celery
# AMQP_URL = 'amqp://guest:guest@localhost:5672//'

# app = Celery('tasks', broker=AMQP_URL)