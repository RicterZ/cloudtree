import os
import tornado.web

from uuid import uuid4
from sqlalchemy import and_, desc
from sqlalchemy.orm.exc import NoResultFound

from web.app import BaseHandler, now
from lib.database import User, UserJob


class IndexHandler(BaseHandler):
    def get(self):
        jobs = []
        if self.current_user:
            jobs = self.db.query(UserJob).filter(and_(UserJob.user_id == self.current_user['id'],
                                                      UserJob.job_type != 'upload'))\
                .order_by(desc(UserJob.create_time))

        self.render('index.html', jobs=jobs, title='Dashboard')


class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')

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
        self.render('upload.html')

    @tornado.web.authenticated
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

        self.db.merge(UserJob(user_id=self.current_user['id'], job_type='upload',
                              job_meta='upload/{0}.fasta'.format(upload_filename), create_time=now()))
        self.db.commit()

        return self.return_json(data='upload/{0}.fasta'.format(upload_filename))
