import sqlite3
import time

import common
from seqlab.place_file import *


def test_seqkey():
    assert seqkey('279.22708_G02_014.ab1') == 22708
    assert seqkey('280.22708_H02_016.ab1') == 22708

def test_seqkey_to_workup():
    conn = sqlite3.connect('data/workups.sqlite3')
    assert seqkey_to_workup(conn, 22708) == {'accession': u'H34908',
                                             'amp_name': u'alt_16s',
                                             'pat_name': u'JENKINS,JOHN',
                                             'seq_key': 22708}



def test_place_file():
    conn = sqlite3.connect('data/workups.sqlite3')
    fixed_time = time.strptime('2012-01-06', '%Y-%m-%d')
    filename = '279.22708_G02_014.ab1'
    source_path = 'data/place_file/source'
    target_path = 'data/place_file/target'
    output_path = 'data/place_file/target/2012/2012_January/2012_01_06/H34908_JENKINS_alt_16s'
    for f in os.listdir(target_path):
        shutil.rmtree(os.path.join(target_path, f))
    assert not(os.path.exists(os.path.join(output_path, filename)))
    place_file(os.path.join(source_path, filename), conn, target_path,
               leave_original=True, current_time=fixed_time)
    assert os.path.exists(os.path.join(output_path, filename))
    assert os.path.exists(os.path.join(output_path, 'workup.json'))
    with open(os.path.join(output_path,'workup.json')) as h:
        j = json.load(h)
        assert j == {'accession': u'H34908',
                     'amp_name': u'alt_16s',
                     'pat_name': u'JENKINS,JOHN',
                     'seq_key': 22708,
                     'path': 'data/place_file/target/2012/2012_January/2012_01_06/H34908_JENKINS_alt_16s'}


test_place_file()
