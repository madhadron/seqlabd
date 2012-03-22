import sqlite3
import time

import common
from seqlab.place import *


def test_seqkey():
    assert seqkey('279.22708_G02_014.ab1') == 22708
    assert seqkey('280.22708_H02_016.ab1') == 22708

def test_place(tmpdir):
    tmpdir.mkdir('source')
    targetdir = tmpdir.mkdir('target')
    sourcefile = tmpdir.join('source/280.22708_H02_016.ab1').ensure(dir=False)
    keyfun = seqkey
    metadatafun = lambda k, ct: {22708: {'to': 'boris/hilda'}, 22709: {'to': 'meep/vroom'}}[k]
    pathgenfun = lambda basepath, metadata, currenttime: basepath.join(metadata['to'])
    postplacefun = lambda p, m: None
    finalpath, metadata = place(sourcefile, keyfun, metadatafun, pathgenfun, targetdir, postplacefun)
    assert finalpath.check(exists=1, file=1)
    assert targetdir.join('boris/hilda/280.22708_H02_016.ab1') == finalpath
    assert targetdir.join('boris/hilda/metadata.json').check(exists=1, file=1)


def test_seqkey_to_workup():
    db = sqlite3.connect(':memory:')
    db.execute("""create table workups (
                      accession text, pat_name text, amp_name text,
                      specimen_description text, specimen_category text,
                      test1_code text, test1_name text,
                      test2_code text, test2_name text,
                      test3_code text, test3_name text,
                      test4_code text, test4_name text,
                      test5_code text, test5_name text,
                      test6_code text, test6_name text,
                      test7_code text, test7_name text,
                      test8_code text, test8_name text,
                      test9_code text, test9_name text,
                      seq_key integer primary key )""")
    db.execute("""insert into workups(accession,pat_name,amp_name,
                      specimen_description, specimen_category, 
                      test1_code, test1_name,
                      test2_code, test2_name, seq_key)
                  values ('H34908', 'JENKINS, JOHN', 'alt_16s',
                          'liver', 'isolate',
                          'BAC1', 'bacterial sequencing',
                          'MUP1', 'muppet test', 123)""")
    print metadata(db, 123)
    assert metadata(db, 123) == \
        {'amp_name': u'alt_16s', 'specimen_description': u'liver', 'seq_key': 123, 'specimen_category': u'isolate', 'pat_name': u'JENKINS, JOHN', 'date': '2012_03_22', 'tests': [(u'BAC1', u'bacterial sequencing'), (u'MUP1', u'muppet test')], 'accession': u'H34908'}
    db.close()

def test_genpath():
    basepath = py.path.local('base')
    metadata = {'accession': 'H34908',
                'pat_name': 'JENKINS, JOHN',
                'amp_name': 'alt_16s'}
    fixed_time = time.strptime('2012-01-06', '%Y-%m-%d')
    assert genpath(basepath, metadata, fixed_time) == \
        basepath.join('2012/2012_January/2012_01_06/H34908_JENKINS_alt_16s')

def test_updatepath():
    db = sqlite3.connect(":memory:")
    db.execute("""create table `seq result` ( `Seq Result ID` integer primary key, path text )""")
    db.execute("""insert into `seq result` ( `Seq Result ID`) values (123)""")
    finalpath = py.path.local('base/2012/junk.ab1')
    metadata = {'seq_key': 123}
    updatepath(db, finalpath, metadata)
    newpath, = db.execute("""select path from `seq result` where `Seq Result ID`=123""").fetchone();
    assert newpath == str(finalpath.dirpath())

