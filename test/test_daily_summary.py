import os
import common
import seqlab.daily_summary
import seqlab.ab1
import seqlab.contig

def test_subdirs_for_summary():
    assert seqlab.daily_summary.subdirs_for_summary('data/workups/2011-06-11') == \
        [({u'amp_name': u'rpoB', u'seq_key': 22708, u'accession': u'F2521',
           u'workup': None, u'pat_name': u'MOZART, WOLFGANG A.'},
          'F2521_MOZART_rpoB',False),
         ({u'amp_name': u'alt_16S', u'seq_key': 22708, u'accession': u'W01325', 
           u'workup': None, u'pat_name': u'JENKINS, JOHN H.'},
          'W01325_JENKINS_alt_16S',True)]


def test_generate_daily_summary():
    if os.path.exists('daily/workups/2011-06-11/summary.html'):
        os.unlink('data/workups/2011-06-11/summary.html')
    seqlab.daily_summary.daily_summary('data/workups/2011-06-11')
    s = os.path.exists('data/workups/2011-06-11/summary.html')
    assert s

