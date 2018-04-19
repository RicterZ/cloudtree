from __future__ import absolute_import, unicode_literals


try:
    from clustalo import clustalo
except ImportError:
    def clustalo(arg):
        raise Exception('patch')

from worker.celery import app


@app.task
def align(seq_dict):
    result = clustalo(seq_dict)
    return result
