import common
from seqlab.contig import *
import py.test

def test_highqualityinterval():
    with py.test.raises(ValueError):
        highqualityinterval([])
    assert highqualityinterval([5,5,5,5], 2, 2) == ProperInterval(0,4)
    assert highqualityinterval([1,1,5,5,1,1], 2, 2) == ProperInterval(2,4)
    assert highqualityinterval([1,1,5,5,3,5,1,5,5,1,1], 2, 2) == ProperInterval(2,9)
    assert highqualityinterval([1,1,1,1,1], 2, 2) == EmptyInterval()

def test_extend():
    assert extend(ProperList(3, [1,2,3]), ProperInterval(0,3), ProperList(3, [1,2,3])) == \
        ProperList(3, [1,2,3,1,2,3])
    assert extend(ProperList(3, [1,2,3]), ProperInterval(3,6), ProperList(3, [1,2,3])) == \
        ProperList(3, [1,2,3])
    assert extend(ProperList(3, [1,2,3]), ProperInterval(0,1), ProperList(3, [1,2,3])) == \
        ProperList(3, [1,2,3,None,None,1,2,3])
    assert extend(ProperList(3, [1,2,3]), ProperInterval(6,12), ProperList(3, [1,2,3])) == \
        ProperList(0, [1,2,3,1,2,3])
    assert extend(ProperList(3, [1,2,3]), EmptyInterval(), ProperList(5, [1,2])) == \
        ProperList(5, [1,2])

def test_combinebase():
    assert combinebase() == 'N'
    assert combinebase(('A', 25)) == 'A'
    assert combinebase(('A', 10), ('T', 10)) == 'N'
    assert combinebase(('A', 10), ('A', 10)) == 'A'
    assert combinebase(('A', 20), ('T', 10)) == 'A'
    assert combinebase(('A', 20), ('T', 20)) == 'W'
    assert combinebase(('A', 20), (None, None)) == 'A'
    assert combinebase(('A', 20), ('T', 10), ('T', 20)) == 'W'

def test_combine():
    assert combine() == EmptyList()
    assert combine((ProperList(3, 'ATA'), ProperList(3, [10,20,20]))) == ProperList(3, 'NTA')
    assert combine((ProperList(3, 'ATA'), ProperList(3, [20,20,20])), 
                   (ProperList(3, 'ATA'), ProperList(3, [20,20,20]))) == \
        ProperList(3, 'ATA')
    assert combine((ProperList(3, 'ATA'), ProperList(3, [20,20,20])),
                   (EmptyList(), EmptyList())) == \
                   ProperList(3, 'ATA')
    assert combine((ProperList(1, 'TTATA'), ProperList(1, [20,20,20,20,20])),
                   (ProperList(3, 'ATACC'), ProperList(3, [20,20,20,20,20]))) == \
                   ProperList(1, 'TTATACC')

def assertassemblies(a, b):
    assert a.keys() == b.keys()
    for k in a.keys():
        assert (k, a[k]) == (k, b[k])
    assert a.metadata == b.metadata

def test_assemble():
    s = 'TTAATTCCTTGGTTAATTCCTTGG'
    assertassemblies(assemble(s, [50]*24, s, [50]*24),
                     Assembly([('confidences 1', ProperList(0, [50]*24, trackclass='integer')),
                               ('bases 1', ProperList(0, s, trackclass='nucleotide')),
                               ('confidences 2', ProperList(0, [50]*24, trackclass='integer')),
                               ('bases 2', ProperList(0, s, trackclass='nucleotide')),
                               ('contig', ProperList(0, s, trackclass='nucleotide'))]))

    assertassemblies(assemble("CC"+s, [50]*26, s, [50]*24),
                     Assembly([('confidences 1', ProperList(0, [50]*26, trackclass='integer')),
                               ('bases 1', ProperList(0, "CC"+s, trackclass='nucleotide')),
                               ('confidences 2', ProperList(2, [50]*24, trackclass='integer')),
                               ('bases 2', ProperList(2, s, trackclass='nucleotide')),
                               ('contig', ProperList(0, "CC"+s, trackclass='nucleotide'))]))

    assertassemblies(assemble('CCATG'+s, [5,5]+([50]*27), s+"TTTTT", [50]*25 + [5]*4), 
                     Assembly([('confidences 1',
                                ProperList(0, [5,5]+[50]*27, trackclass='integer',
                                           features=[ProperInterval(NegInf(), 2, 
                                                                    blue=0, alpha=0.5, green=0, 
                                                                    name='leftunused', red=0)])),
                               ('bases 1', 
                                ProperList(0, 'CCATG'+s, trackclass='nucleotide',
                                           features=[ProperInterval(NegInf(), 2,
                                                                    blue=0, alpha=0.5, green=0,
                                                                    name='leftunused', red=0)])),
                               ('confidences 2', 
                                ProperList(5, [50]*25 + [5]*4, trackclass='integer',
                                           features=[ProperInterval(30, PosInf(), 
                                                                    blue=0, alpha=0.5, green=0, 
                                                                    name='rightunused', red=0)])),
                               ('bases 2', 
                                ProperList(5, s+'T'*5, trackclass='nucleotide',
                                           features=[ProperInterval(30, PosInf(), 
                                                                    blue=0, alpha=0.5, green=0,
                                                                    name='rightunused', red=0)])),
                               ('contig', ProperList(2, 'ATG'+s+'T', trackclass='nucleotide'))]))
    a = assemble('CCATG'+s, [5,5]+[50]*27, s, [5]*24)
    expecteda = \
        Assembly([('confidences 2', ProperList(0, [5]*24, trackclass='integer',
                                               features=[ProperInterval(neginf,posinf, name='unused',
                                                                        red=0, green=0, blue=0, alpha=0.5)])),
                  ('bases 2', ProperList(0, s, trackclass='nucleotide',
                                         features=[ProperInterval(neginf,posinf, name='unused',
                                                                  red=0, green=0, blue=0, alpha=0.5)])),
                  ('confidences 1', 
                   ProperList(0, [5,5]+[50]*27, trackclass='integer',
                              features=[ProperInterval(NegInf(), 2, blue=0, alpha=0.5,
                                                       green=0, name='leftunused', red=0)])),
                  ('bases 1', 
                   ProperList(0, 'CCATG'+s, trackclass='nucleotide',
                              features=[ProperInterval(NegInf(), 2, blue=0, alpha=0.5,
                                                       green=0, name='leftunused', red=0)])),
                  ('contig', ProperList(2, 'ATG'+s, trackclass='nucleotide')),
])
    with open('tmp.html','w') as o:
        print >>o, "<html><head><style>"
        print >>o, css
        print >>o, "</style></head><body>"
        print >>o, renderassembly(a)
        print >>o, "</body></html>"
    assertassemblies(a, expecteda)
    assertassemblies(assemble(s, [5]*24, s, [5]*24), 
                     Assembly([('confidences 1', 
                                ProperList(0,[5]*24, trackclass='integer',
                                           features=[ProperInterval(NegInf(), PosInf(), 
                                                                    blue=0, alpha=0.5, green=0, name='unused', red=0)])),
                               ('bases 1', ProperList(0,s, trackclass='nucleotide',
                                                      features=[ProperInterval(NegInf(), PosInf(), blue=0, 
                                                                               alpha=0.5, green=0, name='unused', red=0)])),
                               ('confidences 2', ProperList(0,[5]*24, trackclass='integer',
                                                            features=[ProperInterval(NegInf(), PosInf(), blue=0, 
                                                                                     alpha=0.5, green=0,
                                                                                     name='unused', red=0)])),
                               ('bases 2', ProperList(0,s, trackclass='nucleotide',
                                                      features=[ProperInterval(NegInf(), PosInf(), blue=0,
                                                                               alpha=0.5, green=0, name='unused', red=0)]))]))

if __name__=='__main__':
    test_assemble()
