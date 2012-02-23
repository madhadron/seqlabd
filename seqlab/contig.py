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
            return EmptyInterval()
    right = len(confs)
    while any([c < threshold for c in confs[right-boundarywidth:right]]):
        if right-boundarywidth > 0:
            right -= 1
        else:
            return EmptyInterval()
    return ProperInterval(left,right)
    

def extend(segment, interval, template):
    """Extend *segment* as a subset *interval* of *template*.

    *segment* and *template* should be ProperLists. *interval*
    specifies a space in *template* where *segment* should replace
    whatever is there. The offset of the resulting ProperList is
    adjusted to be in the same coordinates as *segment*.
    """
    if interval.isempty():
        return template
    lefttail = list(template.iter(template.left(), interval.left()))
    righttail = list(template.iter(interval.right(), template.right()))
    offset = segment.left() - len(lefttail)
    body = lefttail + list(segment) + righttail
    if len(body) == 0:
        return EmptyList()
    else:
        return ProperList(offset, body, **dictunion(segment.metadata))


def combine(*tracks):
    if len(tracks) == 0:
        return EmptyList()
    n = alzipsupport(*[alzipsupport(t[0],t[1]) for t in tracks])
    s = closure(*[t[0].support() for t in tracks])
    return aflist(s.left(), [combinebase(*q) for q in n])


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

    # Pull out high quality segments
    hqint1, hqint2 = highqualityinterval(conf1), highqualityinterval(conf2)
    segment1 = seq1[hqint1.left():hqint1.right()] if hqint1.isproper() else ""
    segment2 = seq2[hqint2.left():hqint2.right()] if hqint2.isproper() else ""
    # Align them
    (offset1, rawalsegment1), (offset2, rawalsegment2) = align.ssearch36(segment1, segment2)
    alsegment1, alsegment2 = aflist(offset1, rawalsegment1, trackclass='nucleotide'), \
        aflist(offset2, rawalsegment2, trackclass='nucleotide')
    alhqint1 = ProperInterval(offset1, offset1+alsegment1.width())
    alhqint2 = ProperInterval(offset2, offset2+alsegment2.width())
    alseq1, alseq2 = extend(alsegment1, hqint1, aflist(0,seq1)), \
        extend(alsegment2, hqint2, aflist(0,seq2))
    alconf1, alconf2 = tracealong(conf1, alseq1), tracealong(conf2, alseq2)

    for i,s in (alhqint1, alseq1), (alhqint1, alconf1), (alhqint2, alseq2), (alhqint2, alconf2):
        if i.isempty():
            s.appendfeature(interval(neginf, posinf, name='unused', red=0, green=0, blue=0, alpha=0.5))
        else:
            if i.left() > s.left():
                s.appendfeature(interval(neginf, i.left(), name='leftunused', 
                                         red=0, green=0, blue=0, alpha=0.5))
            if i.right() < s.right():
                s.appendfeature(interval(i.right(), posinf, name='rightunused', 
                                         red=0, green=0, blue=0, alpha=0.5))


    print alconf1
    print alconf2

    assert alsegment1.width() == alconf1[alhqint1].width()
    assert alsegment2.width() == alconf2[alhqint2].width()
    contig = combine((alsegment1, alconf1[alhqint1]), (alsegment2, alconf2[alhqint2]))

    alconf1.setmeta('trackclass', 'integer')
    alconf2.setmeta('trackclass', 'integer')
    alseq1.setmeta('trackclass', 'nucleotide')
    alseq2.setmeta('trackclass', 'nucleotide')
    contig.setmeta('trackclass', 'nucleotide')


    if alsegment1.width() != 0 and alsegment2.width() != 0: # both strands
        a = Assembly([('confidences 1', alconf1),
                      ('bases 1', alseq1),
                      ('confidences 2', alconf2),
                      ('bases 2', alseq2),
                      ('contig', contig)])
        return a.toorigin()
    elif alsegment1.width() != 0: # strand 1 only
        a0 = Assembly([('confidences 2', ProperList(0, conf2, trackclass='integer',
                                                    features=[interval(neginf, posinf, 
                                                                       name='unused', red=0, green=0,
                                                                       blue=0, alpha=0.5)]) >> alconf1.left()),
                       ('bases 2', ProperList(0, seq2, trackclass='nucleotide',
                                              features=[interval(neginf, posinf, name='unused', 
                                                                 red=0, green=0, blue=0, alpha=0.5)]) >> alconf1.left()),
                       ('confidences 1', alconf1),
                       ('bases 1', alseq1),
                       ('contig', contig)])
        a = a0.toorigin()
        return a
    elif alsegment2.width() != 0: # strand 2 only
        a0 = Assembly([('confidences 1', ProperList(0, conf1, trackclass='integer',
                                                    features=[interval(neginf, posinf, name='unused',
                                                                       red=0, green=0, blue=0, alpha=0.5)]) >> alconf2.left()),
                       ('bases 1', ProperList(0, seq1, trackclass='nucleotide',
                                              features=[interval(neginf, posinf, name='unused', 
                                                                 red=0, green=0, blue=0, alpha=0.5)]) >> alconf2.left()),
                       ('confidences 2', alconf2),
                       ('bases 2', alseq2),
                       ('contig', contig)])
        a = a0.toorigin()
        return a
    else:
        a = Assembly()
        a['confidences 1'] = ProperList(0, conf1, trackclass='integer', 
                                        features=[interval(neginf, posinf, name='unused', red=0, green=0, blue=0, alpha=0.5)])
        a['bases 1'] = ProperList(0, seq1, trackclass='nucleotide',
                                  features=[interval(neginf, posinf, name='unused', red=0, green=0, blue=0, alpha=0.5)])
        a['confidences 2'] = ProperList(0, conf2, trackclass='integer',
                                        features=[interval(neginf, posinf, name='unused', red=0, green=0, blue=0, alpha=0.5)])
        a['bases 2'] = ProperList(0, seq2, trackclass='nucleotide',
                                  features=[interval(neginf, posinf, name='unused', red=0, green=0, blue=0, alpha=0.5)])
        return a

    

