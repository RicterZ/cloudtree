from __future__ import absolute_import, unicode_literals
from clustalo import clustalo
from .celery import app


@app.task
def align(seq_dict):
    return clustalo(seq_dict)


@app.task
def ping():
    return 'ok'
