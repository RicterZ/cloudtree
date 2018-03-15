from worker.align.tasks import align as task_align
from worker.tree.tasks import tree as task_tree
from worker.celery import app


@app.task
def pipeline(seq_dict):
    ret = task_tree(task_align(seq_dict))
    return ret
