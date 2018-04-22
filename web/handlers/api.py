import os
import json
import tornado.web
from celery.result import AsyncResult
from worker.celery import app

from lib.database import UserJob, CeleryTask
from web.app import BaseHandler, now
from lib.utils import parse_fasta
from worker import pipeline as task_pipeline
from worker.tree.tasks import tree as task_tree
from worker.align.tasks import align as task_align
from worker.cluster.tasks import create_cvm, destroy_cvm, install


class ResultViewHandler(BaseHandler):
    def get(self, job_id):
        result = self.db.query(CeleryTask).filter(CeleryTask.task_id == job_id).all()
        if not result:
            return self.return_json(error='Not found task id: %s' % job_id)
        else:
            res = AsyncResult(job_id, app=app)
            if res.status == 'SUCCESS':
                return self.return_json(data=res.get())
            elif res.result == 'PENDING':
                return self.return_json(error='Task is still running')
            else:
                return self.return_json(error='Task failed')


class CreateTreeHandler(BaseHandler):
    """Create a tree-building task.

    POST align task_id
    return tree task_id
    """
    @tornado.web.authenticated
    def post(self):
        align_id = self.get_argument('align_task_id')
        job_title = self.get_argument('name', 'Tree Job')
        data = self.query('align', align_id)
        if data:
            seq_data = json.loads(data['result'])
            task = task_tree.delay(seqs=seq_data)

            self.db.merge(UserJob(user_id=self.current_user['id'], job_type='tree',
                                  job_id=str(task), create_time=now(), job_meta=job_title))
            self.db.commit()
            return self.return_json(data=str(task))
        else:
            return self.return_json(error='Not found align id: %s' % align_id)


class CreateAlignHandler(BaseHandler):
    """Create a align task

    POST fasta file uuid (or path?)
    return align task_id
    """
    @tornado.web.authenticated
    def post(self):
        job_title = self.get_argument('name', 'Align Job')
        file_path = self.get_argument('fasta_file', '')
        file_real_path = os.path.join(os.path.dirname(__file__), '../{0}'.format(file_path))
        if '..' in file_path or not file_path.startswith('upload/') or not file_path.endswith('.fasta') or \
                not os.path.exists(file_real_path):
            return self.return_json(error='Invalid file path')

        try:
            ret = parse_fasta(file_real_path)
        except Exception as e:
            return self.return_json(error='Parse fasta file failed ({0})'.format(str(e)))

        task = task_align.delay(seq_dict=ret)
        self.db.merge(UserJob(user_id=self.current_user['id'], job_type='align',
                              job_id=str(task), create_time=now(), job_meta=job_title))
        self.db.commit()

        return self.return_json(data=str(task))


class PipelineHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        files = data.get('files', [])
        settings = data.get('settings', {})

        for file_path in files:
            file_real_path = os.path.join(os.path.dirname(__file__), '../{0}'.format(file_path))
            if '..' in file_path or not file_path.startswith('upload/') or not file_path.endswith('.fasta') or \
                    not os.path.exists(file_real_path):
                continue

            try:
                ret = parse_fasta(file_real_path)
            except Exception as e:
                print(e)
                continue

            task = task_pipeline.delay(seq_dict=ret, seq_type=settings.get('seq', None),
                                       method=settings.get('method', None))
            self.db.merge(UserJob(user_id=self.current_user['id'], job_type='pipeline',
                                  job_id=str(task), create_time=now(), job_meta='A&T Job'))
            self.db.commit()

        return self.return_json(data=str(task))


class ClusterHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        count = self.get_argument('count')
        create_cvm.delay(count)
        return self.return_json(data={})

    @tornado.web.authenticated
    def delete(self):
        ids = tornado.escape.json_decode(self.request.body)
        destroy_cvm(ids)
        return self.return_json(data={})


class ClusterInstallHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        ip = self.get_argument('ip')
        install.delay(ip)
        return self.return_json(data={})