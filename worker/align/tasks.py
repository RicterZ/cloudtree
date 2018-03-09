from __future__ import absolute_import, unicode_literals
from clustalo import clustalo

from worker.celery import app


@app.task
def ping():
    return 'ok'


@app.task
def align(seq_dict):
    return clustalo(seq_dict)
