from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine

from worker.config import BACKEND


connect_str = BACKEND.replace('db+mysql://', 'mysql://')
engine = create_engine(connect_str, echo=True, pool_recycle=3600)
Base = declarative_base()
metadata = Base.metadata


class Result(Base):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True)
    job_id = Column(String(64), unique=True)
    job_type = Column(String(10))
    result = Column(Text)
    start_time = Column(Integer)
    end_time = Column(Integer)


class Sequence(Base):
    __tablename__ = 'sequences'
    id = Column(Integer, primary_key=True)
    seq_name = Column(Text)
    seq = Column(Text)


db = scoped_session(sessionmaker(bind=engine))

if __name__ == "__main__":
    metadata.create_all(engine)
