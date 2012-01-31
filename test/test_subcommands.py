import json
import time
import shutil
import os

import common

from seqlab.subcommands import placefile
from seqlab.subcommands import seqreport


def test_placefile():
    class Args:
        file='data/place_file/source/279.22708_G02_014.ab1'
        sqlite='data/workups.sqlite3'
        target='data/place_file/target'
    args = Args()

    # Clear anything already there
    for f in os.listdir(args.target):
        shutil.rmtree(os.path.join(args.target, f))
    
    ret = placefile.action(args)
    t = time.localtime()
    path = os.path.join(args.target, time.strftime('%Y', t),
                        time.strftime('%Y_%B', t), time.strftime('%Y_%m_%d', t),
                        'H34908_JENKINS_alt_16s')

    worked = os.path.exists(os.path.join(path, '279.22708_G02_014.ab1'))

    if worked:
        shutil.move(os.path.join(path, '279.22708_G02_014.ab1'),
                    args.file)
    assert ret == 0
    assert worked
    assert os.path.exists(os.path.join(path, 'workup.json'))
    with open(os.path.join(path,'workup.json')) as h:
        j = json.load(h)
        assert j == {'accession': u'H34908',
                     'amp_name': u'alt_16s',
                     'pat_name': u'JENKINS,JOHN',
                     'seq_key': 22708,
                     'path': path}


def test_seqreport():
    for s in ['assembly','strandwise']:
        class Args:
            reportpath=os.path.join('data/seqreport_scratch',s)
        args = Args()

        # Clear possibly existing reports.
        for f in [x for x in os.listdir(args.reportpath) if x.endswidth('.html')]:
            shutil.rmtree(os.path.join(args.reportpath, x))

        ret = seqreport.action(args)
        assert ret == 0
        assert os.path.exists(os.path.join(args.reportpath, '%s_report.html' % s))
        os.unlink(os.path.join(args.reportpath, '%s_report.html' %s))
