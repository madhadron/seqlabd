import py.test
import json
import time
import shutil
import os
import csv
import common

try:
    import oursql
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
    
except:
    pass


from seqlab.subcommands import renderab1

def test_renderab1():
    class Args:
        ab1 = 'data/no_assembly-1.ab1'
        output = 'data/renderedab1.html'
    assert renderab1.action(Args()) == 0



from seqlab.subcommands import sequencereport

def test_workup_files(tmpdir):
    f = tmpdir.join('a')
    f.ensure('workup.json')
    f.ensure('asdf.ab1')
    f.ensure('pqrs.ab1')
    result = sequencereport.workup_files(str(f))
    assert result[0] == str(f.join('workup.json'))
    assert set(result[1:]) == set([str(f.join('asdf.ab1')),
                                   str(f.join('pqrs.ab1'))])
    f = tmpdir.join('b')
    with py.test.raises(ValueError):
        sequencereport.workup_files(str(f))
    f = tmpdir.join('c')
    f.ensure('workup.json')
    with py.test.raises(ValueError):
        sequencereport.workup_files(str(f))
    
def test_sequencereport():
    class Args:
        path_or_json='data/workup.json'
        read1='data/tmpzRpKiy-1.ab1'
        read2='data/tmpzRpKiy-2.ab1'
        verbose=False
        omit_blast=True
        output='data/sequencereport_command_output.html'
    assert sequencereport.action(Args()) == 0
    
import seqlab.subcommands.dailysummary

def test_dailysummary():
    class Args:
        path='data/target'
        nop = False
    assert seqlab.subcommands.dailysummary.action(Args()) == 0
    assert os.path.exists('data/target/summary.html')

import seqlab.subcommands.assemble
def test_assemble():
    class Args:
        output = 'data/assembly.json.bz2'
        first_ab1 = 'data/10h9BE-1.ab1'
        second_ab1 = 'data/10h9BE-2.ab1'
        metadata = 'data/workup.json'
        additional_sequences = []
    assert seqlab.subcommands.assemble.action(Args()) == 0
    assert os.path.exists('data/assembly.json.bz2')

import seqlab.subcommands.addsequence
import seqlab.assembly as asm
def test_addsequences(tmpdir):
    a = asm.Assembly([('a', asm.aflist(0, 'ATGATGGA', '-'))])
    a.serialize(str(tmpdir.join('asm.json.bz2')))
    with open(str(tmpdir.join('a.fasta')), 'w') as h:
        print >>h, '>alpha omega\nTGATGGA\n'
    class Args:
        assembly=str(tmpdir.join('asm.json.bz2'))
        output=str(tmpdir.join('output.json.bz2'))
        align_to='a'
        fastas=[str(tmpdir.join('a.fasta'))]
        no_alignment=False
    assert seqlab.subcommands.addsequence.action(Args()) == 0
    assert os.path.exists(str(tmpdir.join('output.json.bz2')))
    asm2 = asm.deserialize(str(tmpdir.join('output.json.bz2')))
    assert asm2 == asm.Assembly([('a', asm.aflist(0, 'ATGATGGA', '-')),
                                 ('alpha omega', asm.aflist(1, 'TGATGGA', '-'))])

import seqlab.subcommands.statistics

def test_statistics(tmpdir):
    a = asm.Assembly([('a', asm.aflist(0, 'ATGGNTGG-TC', '-')),
                      ('b', asm.aflist(2,   'GGATCCATC', '-')),
                      ('c', asm.aflist(0, 'AAA', '-'))])
    a.serialize(str(tmpdir.join('asm.json.bz2')))
    class Args:
        assembly = str(tmpdir.join('asm.json.bz2'))
        label1 = 'a'
        label2 = 'b'
        fields = ','.join(['identities','mismatches','fracoverlap'])
        output = str(tmpdir.join('test.csv'))
    assert seqlab.subcommands.statistics.action(Args()) == 0
    with open(str(tmpdir.join('test.csv'))) as h:
        cr = csv.reader(h)
        assert cr.next() == ['5','3','0.9']

