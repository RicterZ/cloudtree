from __future__ import absolute_import, unicode_literals
from celery import Celery
from worker.config import BACKEND, BROKER

app = Celery('cloud_tree',
             include=['worker.tree.tasks', 'worker.align.tasks', 'worker'])
app.config_from_object('worker.celeryconfig')
