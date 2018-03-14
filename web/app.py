import json
import time
import tornado.web
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import and_

from lib.database import Result, engine


def now():
    return int(time.time())


def ctime(s):
    return datetime.fromtimestamp(int(s)).strftime('%Y-%m-%d %H:%M:%S')


class JinjaEnvironment(object):
    _flag = None
    _jinja_env = None

    def __new__(cls, *args, **kwargs):
        if not 'path' in kwargs:
            raise Exception('Path of FileSystemLoader required')

        if not cls._jinja_env:
            cls._jinja_env = Environment(loader=FileSystemLoader(kwargs['path']),)
            cls._jinja_env.filters['ctime'] = ctime

        return cls._jinja_env


class JinjaTemplateMixin(object):
    """A simple mixin of jinja2
    From: http://bibhas.in/blog/using-jinja2-as-the-template-engine-for-tornado-web-framework/
    """
    def _render(self, template_name, **kwargs):
        env = JinjaEnvironment(path=self.settings['template_path'])

        try:
            template = env.get_template(template_name)
        except TemplateNotFound:
            raise TemplateNotFound(template_name)
        return template.render(settings=self.settings, **kwargs)


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data)
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            return fields
        return json.JSONEncoder.default(self, obj)


class BaseHandler(tornado.web.RequestHandler, JinjaTemplateMixin):
    def __init__(self, application, request, **kwargs):
        self.db = scoped_session(sessionmaker(bind=engine))
        super(BaseHandler, self).__init__(application, request, **kwargs)

    def query(self, type_, uuid):
        result = self.db.query(Result).filter(and_(Result.job_type == type_, Result.job_id == uuid)).all()
        if not result:
            return None
        else:
            return json.loads(json.dumps(result[0], cls=AlchemyEncoder))

    def data_received(self, chunk):
        pass

    def render(self, template_name, **kwargs):
        self.write(self._render(template_name, user=self.current_user['username'], **kwargs))

    def return_json(self, status=200, **kwargs):
        self.set_status(status)
        self.write(json.dumps(kwargs))
        self.finish()

    def get_current_user(self):
        if self.get_secure_cookie('user'):
            return {'username': self.get_secure_cookie('user'), 'id': self.get_secure_cookie('id')}
        else:
            return None
