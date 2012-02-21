import numpy
import re
import collections
import align
import tracks
from assembly import *

iupac = {('A','C'): 'M',
         ('A','G'): 'R',
         ('A','T'): 'W',
         ('C','G'): 'S',
         ('C','T'): 'Y',
         ('G','T'): 'K',
         ('A',): 'A',
         ('C',): 'C',
         ('T',): 'T',
         ('G',): 'G',
         ('A','C','G'): 'V',
         ('A','C','T'): 'H',
         ('A','G','T'): 'D',
         ('C','G','T'): 'B',
         ('A','C','G','T'): 'N'}

def as_key(s):
    return tuple(sorted(set(s)))

iupac_table = {}
for k1,v1 in iupac.iteritems():
    for k2,v2 in iupac.iteritems():
        new_key = as_key([v1,v2])
        new_base = iupac[as_key(set(k1).union(k2))]
        iupac_table[new_key] = new_base
for i in iupac.itervalues():
    iupac_table[(i,)] = i
    iupac_table[('-',i)] = i
iupac_table[('-',)] = '-'
iupac_table[tuple()] = 'N'


def highqualityinterval(confs, threshold=40, boundarywidth=10):
    """Find the largest interval in *confs* with high quality.

    High quality is defined as having at least *boundarywidth* values
    over *threshold* at each end. Returns a HalfOpenInterval of such a
    region, or None if there is no such region.
    """
    if len(confs) < boundarywidth:
        raise ValueError("Confidences must be at least boundarywidth wide.")
    left = 0
    while any([c < threshold for c in confs[left:left+boundarywidth]]):
        if left+boundarywidth < len(confs):
            left += 1
        else:
            return hoi(0,0)
    right = len(confs)
    while any([c < threshold for c in confs[right-boundarywidth:right]]):
        if right-boundarywidth > 0:
            right -= 1
        else:
            return hoi(0,0)
    return HalfOpenInterval(left,right)
    

def extend(segment, interval, template):
    """Extend *segment* as a subset *interval* of *template*.

    *segment* and *template* should be AffineLists. *interval*
    specifies a space in *template* where *segment* should replace
    whatever is there. The offset of the resulting AffineList is
    adjusted to be in the same coordinates as *segment*.
    """
    if interval.left < template.offset:
        lefttail = []
    elif interval.left < template.offset + len(template):
        lefttail = template[template.offset:interval.left].vals
    else:
        lefttail = template.vals + [None]*(interval.left - (template.offset+len(template)))
    newoffset = segment.offset - len(lefttail)
    if interval.right < template.offset:
        righttail = [None]*(template.offset-interval.right) + template.vals
    elif interval.right < template.offset + len(template):
        righttail = template[interval.right:].vals
    else:
        righttail = []
    return AffineList(newoffset, lefttail + segment.vals + righttail)


def combine(*tracks):
    if len(tracks) == 0:
        return AffineList(0, '')
    n = alzipsupport(*[alzipsupport(t[0],t[1]) for t in tracks])
    s = closure(*[t[0].support() for t in tracks])
    return AffineList(s.left, [combinebase(*q) for q in n])


def combinebase(*pairs):
    if len(pairs) == 0:
        return 'N'
    threshold = 20
    d = collections.defaultdict(lambda: 0)
    for p in pairs:
        if p == None:
            continue
        else:
            b,c = p
            if b:
                d[b] += c
    key = tuple(sorted(k for k,v in d.iteritems() if v >= threshold))
    return iupac_table[key]


def assemble(seq1, conf1, seq2, conf2):
    """Combine two reads into a contig.

    Returns an Assembly with the reads (with used sections marked),
    and a string specifying fate: 'both', 'strand 1', 'strand 2',
    'none'. If the fate is not 'none', then there will be a key
    'contig' in the Assembly.
    """
    assert len(seq1) == len(conf1)
    assert len(seq2) == len(conf2)
    hqint1, hqint2 = highqualityinterval(conf1), highqualityinterval(conf2)
    segment1, segment2 = seq1[hqint1.left:hqint1.right], seq2[hqint2.left:hqint2.right]
    (offset1, rawalsegment1), (offset2, rawalsegment2) = align.ssearch36(segment1, segment2)
    alsegment1, alsegment2 = AffineList(offset1, rawalsegment1), AffineList(offset2, rawalsegment2)
    alseq1, alseq2 = extend(alsegment1, hqint1, AffineList(0,seq1)), \
        extend(alsegment2, hqint2, AffineList(0,seq2))
    alhqint1 = hoi(offset1, offset1+len(alsegment1))
    alhqint2 = hoi(offset2, offset2+len(alsegment2))
    alseq1.features = [Feature('leftunused', None,alhqint1.left, 0,0,0, 0.5),
                       Feature('rightunused', alhqint1.right,None, 0,0,0, 0.5)]
    alseq2.features = [Feature('leftunused', None,alhqint2.left, 0,0,0, 0.5),
                       Feature('leftunused', alhqint2.right,None, 0,0,0, 0.5)]
    alconf1, alconf2 = tracealong(conf1, alseq1), tracealong(conf2, alseq2)
    alconf1.features = [Feature('leftunused', None,alhqint1.left, 0,0,0, 0.5),
                        Feature('rightunused', alhqint1.right,None, 0,0,0, 0.5)]
    alconf2.features = [Feature('leftunused', None,alhqint2.left, 0,0,0, 0.5),
                        Feature('leftunused', alhqint2.right,None, 0,0,0, 0.5)]

    assert len(alsegment1) == len(alconf1[alhqint1])
    assert len(alsegment2) == len(alconf2[alhqint2])
    contig = combine((alsegment1, alconf1[alhqint1]), (alsegment2, alconf2[alhqint2]))

    alconf1.trackclass='integer'
    alconf2.trackclass='integer'
    alseq1.trackclass='nucleotide'
    alseq2.trackclass='nucleotide'
    contig.trackclass='nucleotide'


    if len(alsegment1) != 0 and len(alsegment2) != 0: # both strands
        a = Assembly([('confidences 1', alconf1),
                      ('bases 1', alseq1),
                      ('confidences 2', alconf2),
                      ('bases 2', alseq2),
                      ('contig', contig)])
        return a.narrowto()
    elif len(alsegment1) != 0: # strand 1 only
        a0 = Assembly([('confidences 1', alconf1),
                       ('bases 1', alseq1),
                       ('contig', contig)])
        a = a0.narrowto()
        a['confidences 2'] = AffineList(0, conf2, features=[Feature('unused',None,None,0,0,0,0.5)],
                                        trackclass='integer')
        a['bases 2'] = AffineList(0, seq2, features=[Feature('unused',None,None,0,0,0,0.5)],
                                  trackclass='nucleotide')
        return a
    elif len(alsegment2) != 0: # strand 2 only
        a0 = Assembly([('confidences 2', alconf2),
                       ('bases 2', alseq2),
                       ('contig', contig)])
        a = a0.narrowto()
        a['confidences 1'] = AffineList(0, conf1, features=[Feature('unused',None,None,0,0,0,0.5)],
                                        trackclass='integer')
        a['bases 1'] = AffineList(0, seq1, features=[Feature('unused',None,None,0,0,0,0.5)],
                                  trackclass='nucleotide')
        return a
    else:
        a = Assembly()
        a['confidences 1'] = AffineList(0, conf1, features=[Feature('unused',None,None,0,0,0,0.5)])
        a['bases 1'] = AffineList(0, seq1, features=[Feature('unused',None,None,0,0,0,0.5)])
        a['confidences 2'] = AffineList(0, conf2, features=[Feature('unused',None,None,0,0,0,0.5)])
        a['bases 2'] = AffineList(0, seq2, features=[Feature('unused',None,None,0,0,0,0.5)])
        return a

    

