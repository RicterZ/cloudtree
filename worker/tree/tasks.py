from __future__ import absolute_import, unicode_literals
import os
import tempfile
import subprocess

from worker.celery import app


@app.task
def ping():
    return 'ok'


@app.task
def tree(seqs, seq_type='dna'):
    with open(os.path.join(os.path.dirname(__file__), 'templates/run.nex.template')) as f:
        run_file_content = f.read()

    with open(os.path.join(os.path.dirname(__file__), 'templates/data.nex.template')) as f:
        data_file_content = f.read()

    opts = {'seq_lines': '', 'seq_type': seq_type}
    for k, v in seqs.items():
        opts['seq_lines'] += '{0}\t{1}\n'.format(k, v)
        opts['seq_length'] = len(v)

    opts['seq_count'] = len(seqs)

    data_file_content = data_file_content.format(**opts)

    temp_dir = tempfile.mktemp(prefix='cloudtree_')
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

    run_file_path = os.path.join(temp_dir, 'run.nex')
    data_file_path = os.path.join(temp_dir, 'data.nex')

    with open(run_file_path, 'w') as f:
        f.write(run_file_content)

    with open(data_file_path, 'w') as f:
        f.write(data_file_content)

    with open('{0}.stdout'.format(run_file_path), 'w') as out:
        ret = subprocess.call('mpirun --allow-run-as-root -np {0} mb {1}'.format(2, run_file_path),
                              shell=True, stdout=out, cwd=temp_dir)

    # save result
    with open('{0}.con.tre'.format(run_file_path), 'r') as f:
        result = f.read()

    return result
