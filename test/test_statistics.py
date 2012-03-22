import common

from seqlab.assembly import *
from seqlab.statistics import *

def test_stats():
    a = Assembly([('a', aflist(0, 'ATGGNTGG-TC', '-')),
                  ('b', aflist(2,   'GGATCCATC', '-')),
                  ('c', aflist(0, 'AAA', '-'))])
    assert identities(a, 'a', 'b') == 5
    assert compatibles(a, 'a', 'b') == 6
    assert bases(a, 'a', 'b') == 9
    assert bases1(a, 'a', 'b') == 10
    assert bases2(a, 'a', 'b') == 9
    assert homopolymers(a, 'a', 'b') == 7
    assert homopolymers1(a, 'a', 'b') == 8
    assert homopolymers2(a, 'a', 'b') == 7
    assert conflicts(a, 'a', 'b') == 2
    assert mismatches(a, 'a', 'b') == 3
    assert indels(a, 'a', 'b') == 1
    assert insertions1(a, 'a', 'b') == 0
    assert insertions2(a, 'a', 'b') == 1
    assert ambiguities(a, 'a', 'b') == 1
    assert ambiguities1(a, 'a', 'b') == 1
    assert ambiguities2(a, 'a', 'b') == 0
    assert fracoverlap(a, 'a', 'b') == 0.9
    assert overlap(a, 'a', 'b') == 9
    assert lengthdiff(a, 'a', 'b') == 2
    assert lengthdiff(a, 'b', 'a') == -2
