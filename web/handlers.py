import os
import json
from uuid import uuid4
from web.app import BaseHandler
from lib.utils import parse_fasta
from worker.tree.tasks import tree as task_tree
from worker.align.tasks import align as task_align


class IndexHandler(BaseHandler):
    def get(self):
        self.redirect('index.html')


class AlignHandler(BaseHandler):
    def get(self, job_id):
        result = self.query('align', job_id)
        if not result:
            self.return_json(error='Not found align id: %s' % job_id)
        else:
            self.return_json(data=result)


class TreeHandler(BaseHandler):
    def get(self, job_id):
        result = self.query('tree', job_id)
        if not result:
            return self.return_json(error='Not found tree id: %s' % job_id)
        else:
            return self.return_json(data=result)


class CreateTreeHandler(BaseHandler):
    """Create a tree-building task.

    POST align task_id
    return tree task_id
    """
    def post(self):
        align_id = self.get_argument('align_task_id')
        data = self.query('align', align_id)
        if data:
            seq_data = json.loads(data['result'])
            task_id = str(uuid4())
            task_tree.delay(job_id=task_id, seqs=seq_data)
            return self.return_json(data=task_id)
        else:
            return self.return_json(error='Not found align id: %s' % align_id)


class CreateAlignHandler(BaseHandler):
    """Create a align task

    POST fasta file uuid (or path?)
    return align task_id
    """
    def post(self):
        file_path = self.get_argument('fasta_file', '')
        file_real_path = os.path.join(os.path.dirname(__file__), '../{0}'.format(file_path))
        if '..' in file_path or not file_path.startswith('upload/') or not file_path.endswith('.fasta') or \
                not os.path.exists(file_real_path):
            return self.return_json(error='Invalid file path')

        try:
            ret = parse_fasta(file_real_path)
        except Exception as e:
            return self.return_json(error='Parse fasta file failed ({0})'.format(str(e)))

        task_id = str(uuid4())
        task_align.delay(job_id=task_id, seq_dict=ret)
        return self.return_json(data=task_id)


class UploadFastAHandler(BaseHandler):
    """Upload a FastA file

    POST file
    return file path
    """
    def post(self):
        upload_path = os.path.join(os.path.dirname(__file__), '../upload/')
        upload_filename = str(uuid4())

        file_meta = self.request.files.get('file', None)
        if not file_meta:
            return self.return_json(error='No file uploaded')

        # only get the first file
        file_meta = file_meta[0]
        if not file_meta['filename'].rsplit('.', 1)[1].lower() == 'fasta':
            return self.return_json(error='Only can upload .fasta file')

        file_path = os.path.join(upload_path, '{0}.fasta'.format(upload_filename))
        with open(file_path, 'wb') as f:
            f.write(file_meta['body'])

        return self.return_json(data='upload/{0}.fasta'.format(upload_filename))
