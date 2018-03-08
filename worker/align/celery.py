from __future__ import absolute_import, unicode_literals
from celery import Celery
from worker.config import BACKEND, BROKER

app = Celery('align',
             broker=BROKER,
             backend=BACKEND,
             include=['worker.align.tasks'])
