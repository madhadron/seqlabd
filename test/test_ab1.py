import common
from seqlab.ab1 import *

def test_sparsify():
    xs = numpy.arange(14)
    ys = numpy.arange(14)/5.0
    assert psparsify(xs,ys) == [(0,0), (11,11/5.0), (13,13/5.0)]
    xs = numpy.arange(4)
    ys = numpy.arange(4)
    assert psparsify(xs,ys) == [(0,0), (3,3)]


def test_cutoff():
    xs = numpy.arange(50)
    assert pcutoff(xs) == 45
    assert pcutoff(numpy.array([2]*5 + [10]*50 + [40]*4)) == 40

if __name__ == '__main__':
    test_cutoff()
