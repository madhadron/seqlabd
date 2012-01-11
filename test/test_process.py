import threading
import Queue
import os
import pytest
import shutil
import sets
import time

import common
import test_mdx
import seqlab.process
import seqlab.refs
import seqlab.tracks
import seqlab.ab1
import seqlab.mdx

def test_pair_up():
    pairs, singles = seqlab.process.pair_up(['alpha.1','beta.1','gamma.1','alpha.2','gamma.2'],
                                               lambda s: s.split('.')[0])
    assert pairs == {'alpha':('alpha.1','alpha.2'), 'gamma':('gamma.1','gamma.2')}
    assert singles == {'beta':'beta.1'}

def test_ensure_isdir():
    assert seqlab.process.ensure_isdir('data') == None
    assert seqlab.process.ensure_isdir('data/dir_to_create') == None
    with pytest.raises(ValueError):
        assert seqlab.process.ensure_isdir('data/to_process/alpha.1')

def test_ensure_paths_exist():
    assert seqlab.process.ensure_paths_exist(['data/to_process/alpha.1',
                                                 'data/to_process/alpha.2',
                                                 'data/to_process/horace',
                                                 'data/to_process/beta.1',
                                                 'data/to_process/beta.2']) == \
                                                 ['data/to_process/alpha.1',
                                                  'data/to_process/alpha.2',
                                                  'data/to_process/beta.1']



def test_process_pair():
    seqlab.process.ensure_isdir('data/process_share/workups') 
    share_path_ref = seqlab.refs.Ref('data/process_share')
    workup_path_ref = seqlab.refs.Ref('workups')
    analysis_queue = Queue.Queue()
    mdx = test_mdx.MockMDX()
    seqlab.process.process_pair(share_path_ref, workup_path_ref, analysis_queue, mdx, leave_original=True)(
        seqlab.mdx.Workup(accession='A01', workup='W01', pat_name='Jenkins, John',
                             amp_name='rpoB',path=None),
        'data/tmpzRpKiy-1.ab1', 'data/tmpzRpKiy-2.ab1')
    workup, r1, r2 = analysis_queue.get()
    expected_path = os.path.join(
        time.strftime('data/process_share/workups/%Y/%Y_%B/%Y_%m_%d/', time.localtime()),
        'W01_JENKINS_rpoB')
    assert workup==seqlab.mdx.Workup(accession='A01', workup='W01', pat_name='Jenkins, John', amp_name='rpoB',
                               path=expected_path)
    assert r1==os.path.join(expected_path, 'tmpzRpKiy-1.ab1')
    assert r2==os.path.join(expected_path, 'tmpzRpKiy-2.ab1')
    shutil.rmtree('data/process_share/workups/%Y', time.localtime())


def test_process():
    seqlab.process.ensure_isdir('data/unmatched')
    seqlab.process.ensure_isdir('data/process_share/workups') 
    unmatched_queue = Queue.Queue()
    pair_queue = Queue.Queue()
    seqlab.process.process(pair_by=lambda x: x.split('.')[0],
                              unmatched_fun=lambda k,p: unmatched_queue.put(p),
                              pair_fun=lambda k,a,b: pair_queue.put((a,b)))(sets.ImmutableSet([os.path.join('data/to_process',p)
                                                                                               for p in ['horace', 'alpha.1','alpha.2','beta.1',
                                                                                                         'gamma.1','gamma.2']]))
    assert os.path.split(unmatched_queue.get_nowait())[1] == 'beta.1'
    assert [os.path.split(x)[1] for x in pair_queue.get_nowait()] == ['alpha.1','alpha.2']
    assert [os.path.split(x)[1] for x in pair_queue.get_nowait()] == ['gamma.1','gamma.2']

@common.slow
def test_blast_seq():
    # H. pylori 16S fragment
    s = "TAGGATCAACATGCGTTTCAGCAAACAACCCATCAATCCCCACCGCCGCCGCAGCTCTCGCTAAAATAGGGGCAAAAGAGCTGTCTCCTGAACTTTTCCCGTTCGCTCCCCCTGGCATTTGCACGCTATGGGTAGCGTCAAAAATCACAGGGGCAAATTCTCGCATGATTTTT"
    path = 'data/pylori_blast.xml'
    results = seqlab.process.blast_seq(s, path)
    r = results.alignments[0]
    assert r.title.find('pylori') != -1
    

def test_find_workup():
    path = '/some/path/to/a/file/229.alpha.ab1'
    w = seqlab.process.find_workup(test_mdx.MockMDX())(path)
    assert w.accession == 'A01'
    assert w.workup == 'W01'
    assert w.pat_name == 'Jenkins, John'
    assert w.amp_name == 'rpoB'
