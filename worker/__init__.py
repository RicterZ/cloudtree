from worker.align.tasks import align as task_align
from worker.tree.tasks import tree as task_tree
from worker.celery import app


@app.task
def pipeline(seq_dict, seq_type=None, method=None, bootstrap=500):
    ret = task_tree(task_align(seq_dict), seq_type=seq_type, method=method, bootstrap=bootstrap)
    return ret
