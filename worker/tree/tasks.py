from __future__ import absolute_import, unicode_literals
import os
import tempfile
import subprocess
import glob

from worker.celery import app


methods = {
    'Maximum-Likelihood': 'ML.mao',
    'Neighbor-Joining': 'NJ.mao',
    'Minimum-Evolution': 'ME.mao',
    'Maximum-Parsimony': 'MP.mao',
    'UPGMA': 'UPGMA.mao',
}

seq_map = {
    'Nucleotide alignment (non-coding)': 'nc',
    'Nucleotide alignment (coding)': 'c',
    'Protein alignment (amino acid)': 'aa',
}


@app.task
def tree(seqs, seq_type='Nucleotide alignment (non-coding)', method='Neighbor-Joining', bootstrap=500):
    if method in methods:
        mao_file = methods[method]
    else:
        mao_file = 'NJ.mao'

    if seq_type in seq_map:
        seq = seq_map[seq_type]
    else:
        seq = 'nc'

    if not str(bootstrap).isdigit():
        bootstrap = '500'
    else:
        bootstrap = str(bootstrap)

    print('Use mao file: maos/{}/{}'.format(seq, mao_file))
    mega = os.path.join(os.path.dirname(__file__), 'vendor/megacc')
    tree_mao = os.path.join(os.path.dirname(__file__), 'maos/{}/{}'.format(seq, mao_file))

    with open(tree_mao, 'r') as f:
        data = f.read()
        mao_data = data.format(BOOTSTRAP_NUM=bootstrap)

    with open(os.path.join(os.path.dirname(__file__), 'templates/meg.template')) as f:
        meg_file_content = f.read()

    for k, v in seqs.items():
        meg_file_content += '#%s\n%s\n' % (k, v)

    temp_dir = tempfile.mktemp(prefix='cloudtree_')
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

    tree_mao = os.path.join(temp_dir, 'config.mao')
    with open(tree_mao, 'w') as f:
        f.write(mao_data)

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
