import json
import tornado.web
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import and_

from lib.database import Result, engine


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


class BaseHandler(tornado.web.RequestHandler):
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

    def return_json(self, status=200, **kwargs):
        self.set_status(status)
        self.write(json.dumps(kwargs))
        self.finish()
