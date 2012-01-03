import threading
import Queue
import os
import pytest
import sets

import common
import seqlablib.process
import seqlablib.refs
import seqlablib.tracks
import seqlablib.ab1

def test_pair_up():
    pairs, singles = seqlablib.process.pair_up(['alpha.1','beta.1','gamma.1','alpha.2','gamma.2'],
                                               lambda s: s.split('.')[0])
    assert pairs == {'alpha':('alpha.1','alpha.2'), 'gamma':('gamma.1','gamma.2')}
    assert singles == {'beta':'beta.1'}

def test_ensure_isdir():
    assert seqlablib.process.ensure_isdir('data') == None
    assert seqlablib.process.ensure_isdir('data/dir_to_create') == None
    with pytest.raises(ValueError):
        assert seqlablib.process.ensure_isdir('data/to_process/alpha.1')

def test_ensure_paths_exist():
    assert seqlablib.process.ensure_paths_exist(['data/to_process/alpha.1',
                                                 'data/to_process/alpha.2',
                                                 'data/to_process/horace',
                                                 'data/to_process/beta.1',
                                                 'data/to_process/beta.2']) == \
                                                 ['data/to_process/alpha.1',
                                                  'data/to_process/alpha.2',
                                                  'data/to_process/beta.1']

# def test_process():
#     seqlablib.process.ensure_isdir('data/unmatched')
#     seqlablib.process.ensure_isdir('data/processed') 
#     unmatched_queue = Queue.Queue()
#     pair_queue = Queue.Queue()
#     n_retries = seqlablib.refs.Ref(3)
#     m = lambda x: shutil.move(x, 'data/unmatched')
#     p = seqlablib.process.process(pair_by=lambda x: x.split('.')[0],
#                                   unmatched_fun=seqlablib.process.requeue_n_times(unmatched_queue,
#                                                                                   n_retries, m),
#                                   pair_fun=lambda a,b: pair_queue.put((a,b)) and \
#                                       shutil.move(a, 'data/processed') and \
#                                       shutil.move(b, 'data/processed'))
#     p(sets.ImmutableSet([os.path.join('data/to_process',p)
#                          for p in ['horace', 'alpha.1','alpha.2','beta.1',
#                                    'gamma.1','gamma.2']]))
#     assert os.path.split(unmatched_queue.get_nowait())[1] == 'beta.1'
#     assert [os.path.split(x)[1] for x in pair_queue.get_nowait()] == ['gamma.1','gamma.2']
#     assert [os.path.split(x)[1] for x in pair_queue.get_nowait()] == ['alpha.1','alpha.2']

@common.slow
def test_blast_seq():
    # H. pylori 16S fragment
    s = "TAGGATCAACATGCGTTTCAGCAAACAACCCATCAATCCCCACCGCCGCCGCAGCTCTCGCTAAAATAGGGGCAAAAGAGCTGTCTCCTGAACTTTTCCCGTTCGCTCCCCCTGGCATTTGCACGCTATGGGTAGCGTCAAAAATCACAGGGGCAAATTCTCGCATGATTTTT"
    path = 'data/pylori_blast.xml'
    results = seqlablib.process.blast_seq(s, path)
    r = results.alignments[0]
    assert r.title.find('pylori') != -1
    

