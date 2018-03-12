from lib.database import db, Result


class A(object):
    def __repr__(self):
        return 'x user()}, NULL, NULL)#'


if __name__ == '__main__':
    a = A()
    result = Result(job_id='job_id3', job_type='1', result={a: 1})
    db.add(result)
    db.commit()
