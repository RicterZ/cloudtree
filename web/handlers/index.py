import os
import time
import tornado.web
import hashlib

from sqlalchemy import and_, desc
from sqlalchemy.orm.exc import NoResultFound

from web.app import BaseHandler, now
from lib.database import User, UserJob
from worker.cluster.tasks import CVM_STATUS_CREATING, CVM_STATUS_DESTROYING, CVM_STATUS_NORMAL, list_cvm


class IndexHandler(BaseHandler):
    def get(self):
        status_dict = {
            CVM_STATUS_DESTROYING: 'Destroying',
            CVM_STATUS_NORMAL: 'Working',
            CVM_STATUS_CREATING: 'Creating',
        }
        cluster = list_cvm()
        jobs = []
        if self.current_user:
            jobs = self.db.query(UserJob).filter(and_(UserJob.user_id == self.current_user['id'],
                                                      UserJob.job_type != 'upload'))\
                .order_by(desc(UserJob.create_time)).limit(5).all()

        self.render('index.html', jobs=jobs, title='Dashboard', cluster=cluster, status_dict=status_dict)


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_all_cookies()
        return self.redirect('/')


class LoginHandler(BaseHandler):
    def get(self):
        self.render('base.html')

    def post(self):
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)

        if username and password:
            try:
                user = self.db.query(User).filter(User.username == username).one()
            except NoResultFound:
                return self.redirect('/login')

            if user.check(password):
                self.set_secure_cookie('user', user.username)
                self.set_secure_cookie('id', str(user.id))
                return self.redirect('/')

        return self.redirect('/login')


class UploadFastAHandler(BaseHandler):
    """Upload a FastA file

    POST file
    return file path
    """
    @tornado.web.authenticated
    def get(self):
        uploads = self.db.query(UserJob).filter(and_(UserJob.user_id == self.current_user['id'],
                                                     UserJob.job_type == 'upload'))\
            .order_by(desc(UserJob.create_time)).limit(10).all()
        self.render('upload.html', uploads=uploads, title='Upload')

    @tornado.web.authenticated
    def post(self):
        upload_path = os.path.join(os.path.dirname(__file__), '../upload/')

        file_meta = self.request.files.get('file', None)
        if not file_meta:
            return self.return_json(error='No file uploaded')

        # only get the first file
        file_meta = file_meta[0]
        if not file_meta['filename'].rsplit('.', 1)[1].lower() == 'fasta':
            return self.return_json(error='Only can upload .fasta file')

        upload_filename = '{}-{}'.format(hashlib.md5(str(time.time())).hexdigest()[:6],
                                         os.path.basename(file_meta['filename']))
        file_path = os.path.join(upload_path, upload_filename)
        with open(file_path, 'wb') as f:
            f.write(file_meta['body'])

        self.db.merge(UserJob(user_id=self.current_user['id'], job_type='upload',
                              job_meta='upload/{0}'.format(upload_filename), create_time=now()))
        self.db.commit()

        return self.return_json(data='upload/{0}'.format(upload_filename))


class CreateTaskHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        uploads = self.db.query(UserJob).filter(and_(UserJob.user_id == self.current_user['id'],
                                                     UserJob.job_type == 'upload')) \
            .order_by(desc(UserJob.create_time)).limit(5).all()
        jobs = self.db.query(UserJob).filter(and_(UserJob.user_id == self.current_user['id'],
                                                  UserJob.job_type != 'upload')) \
            .order_by(desc(UserJob.create_time)).limit(10).all()
        self.render('tasks.html', uploads=uploads, jobs=jobs, title='Tasks')


class ClusterHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        status_dict = {
            CVM_STATUS_DESTROYING: 'Destroying',
            CVM_STATUS_NORMAL: 'Working',
            CVM_STATUS_CREATING: 'Creating',
        }
        cluster = list_cvm()
        self.render('cluster.html', title='Cluster', cluster=cluster, status_dict=status_dict)
