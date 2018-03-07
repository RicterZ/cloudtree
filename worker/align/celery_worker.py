from celery import Celery

app = Celery('align',
             broker='',
             include=[''])
