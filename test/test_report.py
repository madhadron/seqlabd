import os
import common
import seqlablib.report
import seqlablib.ab1
import seqlablib.contig

import test_mdx

def test_subdirs_for_summary():
    m = test_mdx.MockMDX()
    assert seqlablib.report.subdirs_for_summary('data/workups/2011-06-11', m) == \
        [(test_mdx.ws[0],'W01_JENKINS',False),
         (test_mdx.ws[2],'TH3_MOZART',True)]

def test_generate_daily_summary():
    m = test_mdx.MockMDX()
    seqlablib.report.generate_daily_summary('data/workups/2011-06-11', m)
    s = os.path.exists('data/workups/2011-06-11/summary.html')
    os.unlink('data/workups/2011-06-11/summary.html')
    assert s

    
def test_ab1_to_alignment():
    path = 'data/ab1_alignment.html'
    d = seqlablib.ab1.read('data/tmpzRpKiy-1.ab1')
    with open(path, 'w') as h:
        print >>h, "<html><head><style>" + seqlablib.report.alignment_css() + "</style></head><body>"
        print >>h, seqlablib.report.render_ab1(d)
        print >>h, "</body></html>"


def test_pprint_seq():
    s = "TAGGATCAACATGCGTTTCAGCAAACAACCCATCAATCCCCACCGCCGCCGCAGCTCTCGCTAAAATAGGGGCAAAAGAGCTGTCTCCTGAACTTTTCCCGTTCGCTCCCCCTGGCATTTGCACGCTATGGGTAGCGTCAAAAATCACAGGGGCAAATTCTCGCATGATTTTT"
    path = 'data/pprint_seq.html'
    with open(path, 'w') as h:
        print >>h, "<html><head><style>" + seqlablib.report.pprint_seq_css() + "</style></head><body>"
        print >>h, seqlablib.report.pprint_seq(s)
        print >>h, "</body></html>"

def test_render_alignment():
    path = "data/assembly_alignment.html"
    read1 = seqlablib.ab1.read('data/tmpzRpKiy-1.ab1')
    read2 = seqlablib.ab1.read('data/tmpzRpKiy-2.ab1')
    assembly = seqlablib.contig.contig(
        read1['sequence'], read1['confidences'],
        seqlablib.tracks.revcomp(read2['sequence']), seqlablib.tracks.revcomp(read2['confidences']))
    with open(path, 'w') as h:
        print >>h, "<html><head><style>" + seqlablib.report.alignment_css() + "</style></head><body>"
        print >>h, seqlablib.report.render_alignment(assembly, read1, read2)
        print >>h, "</body></html>"

def test_pprint_nums():
    assert seqlablib.report.pprint_int(35221) == "35,221"
    assert seqlablib.report.pprint_sci(0.035521) == "3.6&times;10<sup>-2</sup>"


def test_render_blast():
    import cPickle
    with open('data/blast.pickle') as input, open('data/blast_render.html', 'w') as output:
        b = cPickle.load(input)
        print >>output, "<html><head><style>" + seqlablib.report.blast_css() + seqlablib.report.pprint_seq_css() + "</style>"
        print >>output, """<script type="text/javascript">\n""" + seqlablib.report.blast_javascript() + "</script>"
        print >>output, "</head><body>"
        print >>output, seqlablib.report.render_blast(b)
        print >>output, "</body></html>"
