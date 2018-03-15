from __future__ import absolute_import, unicode_literals
import time
import json

from sqlalchemy.orm import scoped_session, sessionmaker

try:
    from clustalo import clustalo
except ImportError:
    def clustalo(arg):
        raise Exception('patch')

from worker.celery import app


@app.task
def ping():
    return 'pong'


@app.task
def sleep(**kwargs):
    time.sleep(50)
    return 'ok'


@app.task
def align(seq_dict):
    result = clustalo(seq_dict)
    return result
