import json
import time
import shutil
import os

import common

from seqlab.subcommands import place, metadata


def test_placefile(tmpdir):
    tmpdir.mkdir('source')
    filepath = tmpdir.join('source/279.22708_G02_014.ab1')
    filepath.ensure(dir=False)
    targetpath = tmpdir.join('target')
    targetpath.ensure(dir=True)
    class Args:
        file=str(filepath)
        target=str(targetpath)
        config='data/seqlab.conf'
        port = None
        host=None
        user=None
        password=None
        database=None
    args = Args()

    assert place.action(args) == 0
    t = time.localtime()
    path = targetpath.join(time.strftime('%Y', t),
                           time.strftime('%Y_%B', t), time.strftime('%Y_%m_%d', t),
                           'H34908_MORRALL_alt_16s')

    assert path.join('279.22708_G02_014.ab1').check(exists=1)
    assert path.join('metadata.json').check(exists=1)
    with open(str(path.join('metadata.json'))) as h:
        j = json.load(h)
        expected = {'amp_name': 'alt_16s',
                    'specimen_description': 'BNE-FLAP',
                    'seq_key': 22708,
                    'accession': 'H34908',
                    'specimen_category': None,
                    'pat_name': 'MORRALL,MARK R',
                    'tests': [['TSEXAM-BACTERIAL',
                               'Tissue extract and amplify bacterial primers'],
                              ['TSEXAM-AFB',
                               'Tissue extract and amplify AFB primers'],
                              ['TSEXAM-FUNGAL',
                               'Tissue extract and amplify fungal primers']]}
        assert j == expected


def test_metadata(tmpdir):
    tmpdir.mkdir('source')
    filepath = tmpdir.join('source/279.22708_G02_014.ab1')
    filepath.ensure(dir=False)
    class Args:
        file=str(filepath)
        output=str(tmpdir.join('metadata.json'))
        config='data/seqlab.conf'
        port = None
        host=None
        user=None
        password=None
        database=None
    args = Args()

    assert metadata.action(args) == 0
    with open(args.output) as h:
        j = json.load(h)
        expected = {'amp_name': 'alt_16s',
                    'specimen_description': 'BNE-FLAP',
                    'seq_key': 22708,
                    'accession': 'H34908',
                    'specimen_category': None,
                    'pat_name': 'MORRALL,MARK R',
                    'tests': [['TSEXAM-BACTERIAL',
                               'Tissue extract and amplify bacterial primers'],
                              ['TSEXAM-AFB',
                               'Tissue extract and amplify AFB primers'],
                              ['TSEXAM-FUNGAL',
                               'Tissue extract and amplify fungal primers']]}
        assert j == expected
