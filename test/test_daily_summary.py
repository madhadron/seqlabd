import os
import common
from seqlab.daily_summary import *
import seqlab.ab1
import seqlab.contig

def test_subdirs(tmpdir):
    tmpdir.join('a').ensure(dir=True)
    tmpdir.join('b').ensure(dir=True)
    tmpdir.join('b/workup.json').write('{}')
    tmpdir.join('c').ensure(dir=True)
    tmpdir.join('c/workup.json').write('{}')
    tmpdir.join('c/assembly_report.html').ensure()
    tmpdir.join('d').ensure(dir=False)
    assert subdirs(str(tmpdir)) == [os.path.join(str(tmpdir),p) for p in ['a','b','c']]
    assert usable_workup(str(tmpdir.join('a'))) == (str(tmpdir.join('a')), False, 'No workup.json in path.')
    assert usable_workup(str(tmpdir.join('b'))) == (str(tmpdir.join('b')), False, 'No report found.')
    assert usable_workup(str(tmpdir.join('c'))) == \
        (str(tmpdir.join('c')), True, 'assembled',
         os.stat(str(tmpdir.join('c/assembly_report.html'))).st_ctime, {})

    assert isinstance(summarize_workups(map(usable_workup, subdirs(str(tmpdir)))), str)


def test_subdirs_for_summary():
    assert subdirs_for_summary('data/workups/2011-06-11') == \
        [({u'amp_name': u'rpoB', u'seq_key': 22708, u'accession': u'F2521',
           u'workup': None, u'pat_name': u'MOZART, WOLFGANG A.'},
          'F2521_MOZART_rpoB',False),
         ({u'amp_name': u'alt_16S', u'seq_key': 22708, u'accession': u'W01325', 
           u'workup': None, u'pat_name': u'JENKINS, JOHN H.'},
          'W01325_JENKINS_alt_16S',True)]


def test_generate_daily_summary():
    if os.path.exists('daily/workups/2011-06-11/summary.html'):
        os.unlink('data/workups/2011-06-11/summary.html')
    daily_summary('data/workups/2011-06-11')
    s = os.path.exists('data/workups/2011-06-11/summary.html')
    assert s

