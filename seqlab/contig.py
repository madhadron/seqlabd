import numpy
import re
import collections
import fasta
import tracks

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

def dashify(target,template):
    for i in [j for j,v in enumerate(template) if v=='-']:
        target.insert(i, 0)
    return target

def find_steps(bs):
    ups = []
    downs = []
    for i in range(len(bs)-1):
        if bs[i] and not(bs[i+1]):
            downs.append(i)
        elif not(bs[i]) and bs[i+1]:
            ups.append(i+1)
        else:
            pass
    return (ups,downs)

def canny_mask(vals, high_threshold=40, low_threshold=10):
    mask = [c >= high_threshold for c in vals]
    N = len(vals)
    ups, downs = find_steps(mask)
    for i in ups:
        assert i > 0 and i < N
        j = i-1
        while j >= 0:
            if vals[j] >= low_threshold:
                mask[j] = True
                j -= 1
            else:
                break
    for i in downs:
        assert i >= 0 and i < N-1
        j = i+1
        while j < N:
            if vals[j] >= low_threshold:
                mask[j] = True
                j += 1
            else:
                break
    return mask

def test_canny_mask():
    assert canny_mask([]) == []
    assert canny_mask([50]) == [True]
    assert canny_mask([20]) == [False]
    assert canny_mask([50,20]) == [True,True]
    assert canny_mask([20,50]) == [True,True]
    assert canny_mask([50,5]) == [True,False]
    assert canny_mask([5,50]) == [False,True]
    assert canny_mask([5,15,50]) == [False,True,True]
    assert canny_mask([50,15,5]) == [True,True,False]
    assert canny_mask([50,15,15,50,15,15,5]) == [True]*6 + [False]
    

def contig(seq1, conf1, seq2, conf2, high_threshold=40, low_threshold=10, call_threshold=20):
    mask1 = canny_mask(conf1, high_threshold, low_threshold)
    mask2 = canny_mask(conf2, high_threshold, low_threshold)
    masked_seq1 = ''.join([m and c or 'N' for m,c in zip(mask1,seq1)])
    masked_seq2 = ''.join([m and c or 'N' for m,c in zip(mask2,seq2)])
    r = r'(?=[^N]{10,})(?:[^N]|N(?=.*[^N]{10,}))+'
    m1 = re.search(r, ''.join([m>high_threshold and c or 'N' for m,c in zip(conf1,seq1)]))
    m2 = re.search(r, ''.join([m>high_threshold and c or 'N' for m,c in zip(conf2,seq2)]))
    if not(m1) and not(m2): # Neither sequence is usable.
        return {'reference': None, 'read1': (0, seq1), 'read2': (0, seq2), 'strands': 'none'}
    elif m1 and not(m2):
        # Only sequence 1 is usable. Take its masked, acceptable part
        # as the reference.
        return {'reference': (m1.start(), tracks.sequence(masked_seq1[m1.start():m1.end()])),
                'read1': (0, seq1), 'read2': (0, seq2),
                'strands': 'strand 1'}
    elif m2 and not(m1):
        # Same as above, but only sequence 2 is usable.
        return {'reference': (m2.start(), tracks.sequence(masked_seq2[m2.start():m2.end()])),
                'read1': (0, seq1), 'read2': (0, seq2),
                'strands': 'strand 2'}
    else:
        # Both are usable. Align them.
        l1, r1 = m1.start(), m1.end()
        seg1 = masked_seq1[l1:r1]
        segconf1 = conf1[l1:r1]
        l2, r2 = m2.start(), m2.end()
        seg2 = masked_seq2[l2:r2]
        segconf2 = conf2[l2:r2]
        (offset1, aligned1), (offset2, aligned2) = fasta.fasta(seg1, seg2)

        if offset1 != 0:
            left, right, leftconf, rightconf = \
                (aligned2,aligned1,
                 dashify(segconf2,aligned2), 
                 dashify(segconf1,aligned1)) 
        else:
            left, right, leftconf, rightconf = \
                (aligned1,aligned2,
                 dashify(segconf1,aligned1),
                 dashify(segconf2,aligned2))

        offset = max(offset1, offset2)

        left_end = min(len(left), len(right)+offset)
        right_end = min(len(right), len(left)-offset)

        reference = left[:offset]

        def combine(b1, c1, b2, c2):
            d = collections.defaultdict(lambda: 0)
            d[b1] += c1
            d[b2] += c2
            key = tuple(sorted(k for k,v in d.iteritems() if v > call_threshold))
            return iupac_table[key]

        # Use left, right, and the resulting confs instead
        reference += ''.join([combine(b1,c1,b2,c2) for b1,c1,b2,c2
                              in zip(left[offset:left_end],
                                     leftconf[offset:left_end],
                                     right[:right_end],
                                     rightconf[:right_end])])

        reference += right[right_end:] + left[left_end:] # One of these is ''

        read1 = tracks.sequence(seq1[:l1] + aligned1 + seq1[r1:])
        read2 = tracks.sequence(seq2[:l2] + aligned2 + seq2[r2:])
 
        maxo = min(max(l1,l2)-(l1-offset1), max(l1,l2)-(l2-offset2))

        v = {'reference': (max(l1,l2)-maxo, tracks.sequence(reference)),
             'read1': (max(l1,l2)-(l1-offset1)-maxo, read1),
             'read2': (max(l1,l2)-(l2-offset2)-maxo, read2),
             'strands': 'both'}
        return v
        

def test_contig():
    ref = 'ACTGATGAGATTGAGACCATTAGGGTAGTTGGAGGCC'
    pref1 = 'TTATTTTTTTTTTAATTTAAA'
    pref2 = 'CCCATTGAGTCCCCCACACCCCACACCCTC'
    s1 = pref1 + ref[:-2] + pref1
    c1 = [1]*len(pref1) + [60]*(len(ref)-2) + [1]*len(pref1)
    s2 = pref2 + ref + pref2
    c2 = [1]*len(pref2) + [60]*len(ref) + [1]*len(pref2)
    assert contig(s1,c1,s2,c2) == {'reference': (30,ref),
                                   'read1': (9, s1),
                                   'read2': (0, s2)}

