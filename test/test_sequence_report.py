import os
import common
import seqlab.sequence_report
import seqlab.ab1
import seqlab.contig

def test_ab1_to_alignment():
    path = 'data/ab1_alignment.html'
    d = seqlab.ab1.read('data/tmpzRpKiy-1.ab1')
    with open(path, 'w') as h:
        print >>h, "<html><head><style>" + seqlab.sequence_report.alignment_css() + "</style></head><body>"
        print >>h, seqlab.sequence_report.render_ab1(d)
        print >>h, "</body></html>"


def test_pprint_seq():
    s = "TAGGATCAACATGCGTTTCAGCAAACAACCCATCAATCCCCACCGCCGCCGCAGCTCTCGCTAAAATAGGGGCAAAAGAGCTGTCTCCTGAACTTTTCCCGTTCGCTCCCCCTGGCATTTGCACGCTATGGGTAGCGTCAAAAATCACAGGGGCAAATTCTCGCATGATTTTT"
    path = 'data/pprint_seq.html'
    with open(path, 'w') as h:
        print >>h, "<html><head><style>" + seqlab.sequence_report.pprint_seq_css() + "</style></head><body>"
        print >>h, seqlab.sequence_report.pprint_seq(s)
        print >>h, "</body></html>"

def test_render_alignment():
    path = "data/assembly_alignment.html"
    read1 = seqlab.ab1.read('data/tmpzRpKiy-1.ab1')
    read2 = seqlab.ab1.read('data/tmpzRpKiy-2.ab1')
    assembly = seqlab.contig.contig(
        read1['sequence'], read1['confidences'],
        seqlab.tracks.revcomp(read2['sequence']), seqlab.tracks.revcomp(read2['confidences']))
    with open(path, 'w') as h:
        print >>h, "<html><head><style>" + seqlab.sequence_report.alignment_css() + "</style></head><body>"
        print >>h, seqlab.sequence_report.render_alignment(assembly, read1, read2)
        print >>h, "</body></html>"

def test_pprint_nums():
    assert seqlab.sequence_report.pprint_int(35221) == "35,221"
    assert seqlab.sequence_report.pprint_sci(0.035521) == "3.6&times;10<sup>-2</sup>"


def test_render_blast():
    import cPickle
    with open('data/blast.pickle') as input, open('data/blast_render.html', 'w') as output:
        b = cPickle.load(input)
        print >>output, "<html><head><style>" + seqlab.sequence_report.blast_css() + seqlab.sequence_report.pprint_seq_css() + "</style>"
        print >>output, """<script type="text/javascript">\n""" + seqlab.sequence_report.blast_javascript() + "</script>"
        print >>output, "</head><body>"
        print >>output, seqlab.sequence_report.render_blast(b, 'none')
        print >>output, "</body></html>"

def test_generate_report():
    assembled_fun = lambda w, r1, r2, a, searchres: searchres
    strandwise_fun = lambda w, r1, r2, searchres1, searchres2: searchres1+searchres2
    f = seqlab.sequence_report.generate_report(lambda x, save_path: 'alpha', assembled_fun, strandwise_fun)
    assert f(({'accession':'W01', 'workup':'F22501', 'pat_name':'Jenkins, John H.',
               'amp_name':'rpoB', 'path':'data/workups/2011-06-11/W01_JENKINS'},
              'data/no_assembly-1.ab1', 'data/no_assembly-2.ab1')) == ('strandwise', "alphaalpha")
    f = seqlab.sequence_report.generate_report(lambda x, save_path: 'beta', assembled_fun, strandwise_fun)
    assert f(({'accession':'TH3', 'workup': None,
               'pat_name': 'Mozart, Wolfgang', 'amp_name': 'alt_16s',
               'path': 'data/workups/2011-06-11/TH3_MOZART'},
              'data/tmpzRpKiy-1.ab1', 'data/tmpzRpKiy-2.ab1')) == ('assembled', "beta")

def test_render_assembled():
    import cPickle
    w = {'accession':'W01325', 'workup':'F22501', 'pat_name':'JENKINS, JOHN H.', 'amp_name':'rpoB', 'path':'data/workups/2011-06-11/W01_JENKINS'}
    with open('data/assembly_blast.pickle') as h:
        blast_res = cPickle.load(h)
    with open('data/render_assembled.html', 'w') as h:
        print >>h, seqlab.sequence_report.generate_report(lambda s, save_path: blast_res, seqlab.sequence_report.render_assembled, lambda *args: None )((w, 'data/tmpzRpKiy-1.ab1', 'data/tmpzRpKiy-2.ab1'))[1]

def test_render_strandwise():
    import cPickle
    w = {'accession':'F2521', 'workup':'F22501', 'pat_name':'MOZART, WOLFGANG A.', 'amp_name':'rpoB', 'path':'data/workups/2011-06-11/W01_JENKINS'}
    with open('data/strand1_blast.pickle') as h, open('data/strand2_blast.pickle') as h2:
        blast_res1 = cPickle.load(h)
        blast_res2 = cPickle.load(h2)
    def pseudoblast(seq, save_path):
        if seq[0] == 'G': 
            return blast_res1
        else:
            return blast_res2
    with open('data/render_strandwise.html', 'w') as h:
        print >>h, seqlab.sequence_report.generate_report(pseudoblast, lambda *args: None, seqlab.sequence_report.render_strandwise)((w, 'data/no_assembly-1.ab1', 'data/no_assembly-2.ab1'))[1]
    
