from __future__ import absolute_import, unicode_literals
import time
import json

from sqlalchemy.orm import scoped_session, sessionmaker

try:
    from clustalo import clustalo
except ImportError:
    def clustalo(arg):
        raise Exception('patch')

from lib.database import Result, engine
from worker.celery import app


@app.task
def ping():
    return 'ok'


@app.task
def align(job_id, seq_dict):
    start_at = int(time.time())
    result = clustalo(seq_dict)
    save_result(job_id, result, start_at)
    return result


def save_result(job_id, result, start_at):
    db = scoped_session(sessionmaker(bind=engine))
    result = Result(job_id=job_id, job_type='align', result=json.dumps(result), start_time=start_at, end_time=int(time.time()))
    db.add(result)
    db.commit()
