import json
import os
import common
from seqlab.sequence_report import *
import seqlab.assembly

def test_pprint_seq():
    s = seqlab.assembly.ProperList(5, ''.join(["TAGGATCAACATGCGTTTCAGCAAACAACCCATCAATCCCCACCGCCGCCGCAGCTCTCGCT",
                                        "AAAATAGGGGCAAAAGAGCTGTCTCCTGAACTTTTCCCGTTCGCTCCCCCTGGCATTTGCAC",
                                        "GCTATGGGTAGCGTCAAAAATCACAGGGGCAAATTCTCGCATGATTTTT"]))
    path = 'data/pprint_seq.html'
    with open(path, 'w') as h:
        print >>h, "<html><head><style>" + pprint_seq_css() + "</style></head><body>"
        print >>h, pprint_seq(s)
        print >>h, "</body></html>"


def test_pprint_nums():
    assert pprint_int(35221) == "35,221"
    assert pprint_sci(0.035521) == "3.6&times;10<sup>-2</sup>"


def test_render_blast():
    with open('data/pylori_blast.json') as input, open('data/blast_render.html', 'w') as output:
        b = json.load(input)
        print >>output, "<html><head><style>" + blast_css() + pprint_seq_css() + "</style>"
        print >>output, """<script type="text/javascript">\n""" + blast_javascript() + "</script>"
        print >>output, "</head><body>"
        print >>output, render_blast(b, 'none')
        print >>output, "</body></html>"

def test_generate_report():
    assembled_fun = lambda w, a, searchres, omit_blast=False: searchres
    strandwise_fun = lambda w, a, searchres1, searchres2, omit_blast=False: searchres1+searchres2
    f = generate_report(lambda x, *args, **kwargs: 'alpha', assembled_fun, strandwise_fun)
    assert f(({'accession':'W01', 'workup':'F22501', 'pat_name':'Jenkins, John H.',
               'amp_name':'rpoB', 'path':'data/workups/2011-06-11/W01_JENKINS'},
              'data/no_assembly-1.ab1', 'data/no_assembly-2.ab1')) == ('assembled', "alpha")
    f = generate_report(lambda x, *args, **kwargs: 'beta', assembled_fun, strandwise_fun)
    assert f(({'accession':'TH3', 'workup': None,
               'pat_name': 'Mozart, Wolfgang', 'amp_name': 'alt_16s',
               'path': 'data/workups/2011-06-11/TH3_MOZART'},
              'data/tmpzRpKiy-1.ab1', 'data/tmpzRpKiy-2.ab1')) == ('assembled', "beta")

def test_render_assembled():
    w = {'accession':'W01325', 'workup':'F22501', 'pat_name':'JENKINS, JOHN H.', 'amp_name':'rpoB', 'path':'data/workups/2011-06-11/W01_JENKINS',
         'date': '2011-06-23', 'tests': [['BACTSEQ','Bacterial sequencing']],
         'specimen_description': 'Gooey stuff', 'specimen_category': 'Sputum'}
    with open('data/pylori_blast.json') as h:
        blast_res = json.load(h)
    with open('data/render_assembled.html', 'w') as h:
        print >>h, generate_report(lambda s, *args, **kwargs: blast_res, render_assembled, lambda *args: None )((w, 'data/tmpzRpKiy-1.ab1', 'data/tmpzRpKiy-2.ab1'))[1]

def test_render_strandwise():
    w = {'accession':'F2521', 'workup':'F22501', 'pat_name':'MOZART, WOLFGANG A.', 'amp_name':'rpoB', 'path':'data/workups/2011-06-11/W01_JENKINS',
         'date': '2011-06-23', 'tests': [['BACTSEQ','Bacterial sequencing']],
         'specimen_description': 'Gooey stuff', 'specimen_category': 'Sputum'}
    with open('data/pylori_blast.json') as h, open('data/pylori_blast.json') as h2:
        blast_res1 = json.load(h)
        blast_res2 = json.load(h2)
    def pseudoblast(seq, *args, **kwargs):
        if seq[0] == 'G': 
            return blast_res1
        else:
            return blast_res2
    body = generate_report(pseudoblast, lambda *args: None, render_strandwise)((w, 'data/10h9BE-1.ab1', 'data/10h9BE-2.ab1'))[1]
    assert body is not None
    with open('data/render_strandwise.html', 'w') as h:
        print >>h, body


def test_render_noblast():
    w = {'accession':'F2521', 'workup':'F22501', 'pat_name':'MOZART, WOLFGANG A.', 'amp_name':'rpoB', 'path':'data/workups/2011-06-11/W01_JENKINS',
         'date': '2011-06-23', 'tests': [['BACTSEQ','Bacterial sequencing']],
         'specimen_description': 'Gooey stuff', 'specimen_category': 'Sputum'}
    def pseudoblast(seq, *args, **kwargs):
        raise Exception("Should not call lookup!")
    body = generate_report(pseudoblast, lambda *args: None, render_strandwise)((w, 'data/10h9BE-1.ab1', 'data/10h9BE-2.ab1'), omit_blast=True)
    assert body[0] == 'strandwise'
    assert body[1] is not None
    with open('data/render_strandwise_noblast.html', 'w') as h:
        print >>h, body[1]

    w = {'accession':'W01325', 'workup':'F22501', 'pat_name':'JENKINS, JOHN H.', 'amp_name':'rpoB', 'path':'data/workups/2011-06-11/W01_JENKINS',
         'date': '2011-06-23', 'tests': [['BACTSEQ','Bacterial sequencing']],
         'specimen_description': 'Gooey stuff', 'specimen_category': 'Sputum'}
    with open('data/render_assembled_noblast.html', 'w') as h:
        print >>h, generate_report(pseudoblast, render_assembled, lambda *args: None )((w, 'data/tmpzRpKiy-1.ab1', 'data/tmpzRpKiy-2.ab1'), omit_blast=True)[1]

@common.slow
def test_blast_seq():
    # H. pylori 16S fragment
    s = "TAGGATCAACATGCGTTTCAGCAAACAACCCATCAATCCCCACCGCCGCCGCAGCTCTCGCTAAAATAGGGGCAAAAGAGCTGTCTCCTGAACTTTTCCCGTTCGCTCCCCCTGGCATTTGCACGCTATGGGTAGCGTCAAAAATCACAGGGGCAAATTCTCGCATGATTTTT"
    path = 'data/pylori_blast.xml'
    results = blast_seq(s, path, json_path='data/pylori_blast.json', json_limit=None)
    r = results.alignments[0]
    assert r.title.find('pylori') != -1
    assert os.path.exists('data/pylori_blast.xml')
    assert os.path.exists('data/pylori_blast.json')




