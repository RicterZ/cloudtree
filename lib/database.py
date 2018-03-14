from hashlib import sha1
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from sqlalchemy import create_engine
from sqlalchemy.orm.exc import NoResultFound

from worker.config import BACKEND


connect_str = BACKEND.replace('db+mysql://', 'mysql://')
engine = create_engine(connect_str, echo=True, pool_recycle=3600)
Base = declarative_base()
metadata = Base.metadata


class CeleryTask(Base):
    __tablename__ = 'celery_taskmeta'
    id = Column(Integer, primary_key=True)
    task_id = Column(String(64))
    status = Column(String(20))


class Result(Base):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(64), unique=True)
    job_type = Column(String(10))
    result = Column(Text)
    start_time = Column(Integer)
    end_time = Column(Integer)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(20))
    password = Column(String(40))

    def check(cls, password):
        return cls.password == sha1(password).hexdigest()


class UserJob(Base):
    __tablename__ = 'users_jobs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(64))
    user_id = Column(Integer)
    create_time = Column(Integer)
    job_type = Column(String(10))
    job_meta = Column(Text)

    @property
    def status(cls):
        if cls.job_type == 'upload':
            return 'SUCCESS'

        session = Session.object_session(cls)
        try:
            obj = session.query(CeleryTask).filter(CeleryTask.task_id == cls.job_id).one()
        except NoResultFound:
            return 'RUNNING'

        return obj.status


db = scoped_session(sessionmaker(bind=engine))

if __name__ == "__main__":
    metadata.create_all(engine)
