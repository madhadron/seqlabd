import common
from seqlab.contig import *
import py.test

def test_highqualityinterval():
    with py.test.raises(ValueError):
        highqualityinterval([])
    assert highqualityinterval([5,5,5,5], 2, 2) == HalfOpenInterval(0,4)
    assert highqualityinterval([1,1,5,5,1,1], 2, 2) == HalfOpenInterval(2,4)
    assert highqualityinterval([1,1,5,5,3,5,1,5,5,1,1], 2, 2) == HalfOpenInterval(2,9)
    assert highqualityinterval([1,1,1,1,1], 2, 2) == hoi(0,0)

def test_extend():
    assert extend(AffineList(3, [1,2,3]), HalfOpenInterval(0,3), AffineList(3, [1,2,3])) == \
        AffineList(3, [1,2,3,1,2,3])
    assert extend(AffineList(3, [1,2,3]), HalfOpenInterval(3,6), AffineList(3, [1,2,3])) == \
        AffineList(3, [1,2,3])
    assert extend(AffineList(3, [1,2,3]), HalfOpenInterval(0,1), AffineList(3, [1,2,3])) == \
        AffineList(3, [1,2,3,None,None,1,2,3])
    assert extend(AffineList(3, [1,2,3]), HalfOpenInterval(6,12), AffineList(3, [1,2,3])) == \
        AffineList(0, [1,2,3,1,2,3])

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
    assert combine() == AffineList(0, '')
    assert combine((AffineList(3, 'ATA'), AffineList(3, [10,20,20]))) == AffineList(3, 'NTA')
    assert combine((AffineList(3, 'ATA'), AffineList(3, [20,20,20])), 
                   (AffineList(3, 'ATA'), AffineList(3, [20,20,20]))) == \
        AffineList(3, 'ATA')
    assert combine((AffineList(3, 'ATA'), AffineList(3, [20,20,20])),
                   (AffineList(0,[]), AffineList(0,[]))) == \
                   AffineList(3, 'ATA')
    assert combine((AffineList(1, 'TTATA'), AffineList(1, [20,20,20,20,20])),
                   (AffineList(3, 'ATACC'), AffineList(3, [20,20,20,20,20]))) == \
                   AffineList(1, 'TTATACC')

def test_assemble():
    s = 'TTAATTCCTTGGTTAATTCCTTGG'
    a = assemble(s, [50]*24, s, [50]*24)
    assert a == Assembly([('confidences 1', AffineList(0, [50]*24)),
                          ('bases 1', AffineList(0, s)),
                          ('confidences 2', AffineList(0, [50]*24)),
                          ('bases 2', AffineList(0, s)),
                          ('contig', AffineList(0, s))])
    assert assemble("CC"+s, [50]*26, s, [50]*24) == \
        Assembly([('confidences 1', AffineList(0, [50]*26)),
                  ('bases 1', AffineList(0, "CC"+s)),
                  ('confidences 2', AffineList(2, [50]*24)),
                  ('bases 2', AffineList(2, s)),
                  ('contig', AffineList(0, "CC"+s))])
    a = assemble('CCATG'+s, [5,5]+([50]*27), s+"TTTTT", [50]*25 + [5]*4).narrowto()
    expecteda = \
        Assembly([('confidences 1', AffineList(0, [5,5]+[50]*27)),
                  ('bases 1', AffineList(0, 'CCATG'+s)),
                  ('confidences 2', AffineList(5, [50]*25 + [5]*4)),
                  ('bases 2', AffineList(5, s+'T'*5)),
                  ('contig', AffineList(2, 'ATG'+s+'T'))])
    assert a == expecteda
    a = assemble('CCATG'+s, [5,5]+[50]*27, s, [5]*24).narrowto()
    expecteda = \
        Assembly([('confidences 1', AffineList(0, [5,5]+[50]*27)),
                  ('bases 1', AffineList(0, 'CCATG'+s)),
                  ('contig', AffineList(2, 'ATG'+s)),
                  ('confidences 2', AffineList(0, [5]*24)),
                  ('bases 2', AffineList(0, s))])
    with open('tmp.html','w') as o:
        print >>o, "<html><head><style>"
        print >>o, css
        print >>o, "</style></head><body>"
        print >>o, renderassembly(a)
        print >>o, "</body></html>"
    assert a == expecteda
    a = assemble(s, [5]*24, s, [5]*24).narrowto()
    assert a == Assembly([('confidences 1', AffineList(0,[5]*24)),
                          ('bases 1', AffineList(0,s)),
                          ('confidences 2', AffineList(0,[5]*24)),
                          ('bases 2', AffineList(0,s))])

if __name__=='__main__':
    test_assemble()
