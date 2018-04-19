from __future__ import absolute_import, unicode_literals
import os
import tempfile
import subprocess
import glob

from worker.celery import app


@app.task
def tree(seqs, seq_type='dna'):
    mega = os.path.join(os.path.dirname(__file__), 'vendor/megacc')
    tree_mao = os.path.join(os.path.dirname(__file__), 'templates/tree.mao')
    with open(os.path.join(os.path.dirname(__file__), 'templates/meg.template')) as f:
        meg_file_content = f.read()

    for k, v in seqs.items():
        meg_file_content += '#%s\n%s\n' % (k, v)

    temp_dir = tempfile.mktemp(prefix='cloudtree_')
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

    meg_file_path = os.path.join(temp_dir, 'run.meg')
    with open(meg_file_path, 'w') as f:
        f.write(meg_file_content)

    print('{} -d {} -a {} -o {}'.format(mega, meg_file_path, tree_mao, temp_dir))
    subprocess.call('{} -d {} -a {} -o {}'.format(mega, meg_file_path, tree_mao, temp_dir), shell=True)

    nwk_file = glob.glob(os.path.join(temp_dir, '*.nwk'))
    if not nwk_file:
        raise Exception('nwk file not found')

    # save result
    with open(nwk_file[0], 'r') as f:
        result = f.read()

    return result
