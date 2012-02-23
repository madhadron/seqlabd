import common
from seqlab.assembly import *
import os
import random

# Intervals
def test_intervals():
    # Does the intersection convenience function work?
    assert intersection(ProperInterval(1,3), ProperInterval(5,7)) == ProperInterval(1,3).intersection(ProperInterval(5,7))
    # Is intersection idempotent?
    assert intersection(ProperInterval(1,3), ProperInterval(1,3)) == ProperInterval(1,3)
    # Is the empty set a zero of intersection?
    assert intersection(ProperInterval(1,3), EmptyInterval()) == EmptyInterval()
    # Do disjoint intervals intersect to empty?
    assert intersection(ProperInterval(1,3), ProperInterval(5,7)) == EmptyInterval()
    # Does the closure convenience function work?
    assert closure(ProperInterval(1,3), ProperInterval(5,7)) == ProperInterval(1,3).closure(ProperInterval(5,7))
    # Is closure idempotent?
    assert closure(ProperInterval(1,3), ProperInterval(1,3)) == ProperInterval(1,3)
    # Empty is a unit of closure
    assert closure(ProperInterval(1,3), EmptyInterval()) == ProperInterval(1,3)
    # Are intervals containing posinf and neginf infinite?
    for i in [ProperInterval(neginf,posinf), ProperInterval(neginf,5), ProperInterval(5,posinf), ProperInterval(3,5)]:
        assert i.isfinite() != i.isinfinite()
        assert i.isinfinite() == (i.left() == neginf or i.right() == posinf)
    # Does contains work?
    assert 3 in ProperInterval(1,6)
    assert not(3 in ProperInterval(5,6))
    assert not(3 in EmptyInterval())
    assert 3 in ProperInterval(neginf,posinf)
    assert not(3 in ProperInterval(neginf,0))
    assert not(3 in ProperInterval(5,posinf))
    # Does overlaps work?
    assert ProperInterval(1,6).overlaps(ProperInterval(4,12))
    assert not(EmptyInterval().overlaps(EmptyInterval()))
    assert not(EmptyInterval().overlaps(ProperInterval(4,12)))
    # Does width work?
    for i in [ProperInterval(neginf,posinf), ProperInterval(1,3), ProperInterval(neginf,3), ProperInterval(1,posinf)]:
        assert i.width() == i.right() - i.left()
    assert EmptyInterval().width() == 0
    # Are metadata propogated properly?
    assert closure(EmptyInterval(a=3),EmptyInterval(b=5)) == EmptyInterval(a=3,b=5)
    assert closure(ProperInterval(3,8,a=3),ProperInterval(3,8,b=5)) == ProperInterval(3,8,a=3,b=5)
    assert intersection(EmptyInterval(a=3),EmptyInterval(b=5)) == EmptyInterval(a=3,b=5)
    assert intersection(ProperInterval(3,8,a=3),ProperInterval(3,8,b=5)) == ProperInterval(3,8,a=3,b=5)
    # Are metadata left weighted?
    assert closure(EmptyInterval(a=3),EmptyInterval(a=5)) == EmptyInterval(a=3)
    assert closure(ProperInterval(3,8,a=3), ProperInterval(3,8,a=5)) == ProperInterval(3,8,a=3)
    # Does strip remove metadata?
    assert EmptyInterval(a=3).strip() == EmptyInterval()
    assert ProperInterval(3,8,a=3).strip() == ProperInterval(3,8)
    # Does support work?
    assert support(ProperInterval(0,20), ProperInterval(-3,5)) == ProperInterval(-3,20)

# Affine lists
def test_affinelist():
    a = ProperList(offset=0, values=range(20))
    # Does repr work?
    assert eval(repr(a)) == a
    q = ProperList(0, [0,1,2], a=3, boris={1:2})
    assert eval(repr(q)) == q
    # Shifting commutes with subsetting in the expected way for coordinates
    assert a[5:10] >> 3 == (a >> 3)[8:13]
    assert a[ProperInterval(5,10)] << 3 == (a << 3)[2:7]
    assert EmptyList() << 3 == EmptyList()
    assert EmptyList() >> 3 == EmptyList()
    assert a[5:5] == EmptyList()
    # Are shifting operators inverses?
    assert (a >> 3) << 3 == a
    # Fetching outside the range returns None
    for i in range(-20,50):
        assert a[i] == (None if i < 0 or i >= 20 else i)
        assert EmptyList()[i] == None
    # Is featureson sane?
    b = ProperList(offset=3, values=[1,2,3,4,5], 
                   features=[ProperInterval(neginf,5), ProperInterval(1,4), ProperInterval(3,posinf)])
    assert b.featureson(-10) == [ProperInterval(neginf,5)]
    assert b.featureson(3) == [ProperInterval(neginf,5), ProperInterval(1,4), ProperInterval(3,posinf)]
    # Is support sane?
    assert a.support() == ProperInterval(0,20)
    assert EmptyList().support() == EmptyInterval()
    assert support(a,b) == ProperInterval(0,20)
    # Does width work?
    assert a.width() == a.right() - a.left()
    # Does iteration work?
    assert list(iter(a)) == range(20)
    assert list(a.itercoords()) == zip(range(20), range(20))
    # Do list operations work?
    a.append(20)
    assert a == ProperList(0, range(21))
    a.insert(-1,-1)
    assert a == ProperList(-1, range(-1,21))
    a.extend([21,22])
    assert a == ProperList(-1, range(-1,23))
    a.extend(EmptyList())
    assert a == ProperList(-1, range(-1,23))
    a.extend(ProperList(56, [23,24]))
    assert a == ProperList(-1, range(-1,25))
    assert list(a) == range(-1,25)
    assert list(EmptyList()) == []
    # Does find work?
    assert ProperList(3, [1,2,3,4,5]).find(lambda x: x%2==0, all=True) == [4,6]
    assert ProperList(3, [1,2,3,4,5]).find(lambda x: x%2==0) == 4
    assert ProperList(3, [1,2,1,2,1]).find(1, all=True) == [3,5,7]
    assert ProperList(3, [1,2,1,2,1]).find(1) == 3
    assert ProperList(3, [1,2,1,2,1]).find(1, all=True, start=4) == [5,7]
    assert ProperList(3, [1,2,1,2,1]).find(1, all=True, end=5) == [3]
    # Does setting items work, in the support and to both sides of it?
    a = ProperList(3, [1,2,3,4,5]); a[3] = 0
    assert a == ProperList(3, [0,2,3,4,5])
    a = ProperList(3, [1,2,3,4,5]); a[1] = 0
    assert a == ProperList(1, [0,None,1,2,3,4,5])
    a = ProperList(3, [1,2,3,4,5]); a[9] = 0
    assert a == ProperList(3, [1,2,3,4,5,None,0])
    # Is metadata propogated properly?
    c = ProperList(3, range(20), a=12)
    assert c[3:4].metadata == c.metadata
    

# Assemblies

def assertassemblies(a, b):
    assert a.keys() == b.keys()
    for k in a.keys():
        assert (k, a[k]) == (k, b[k])
    assert a.metadata == b.metadata

def test_assembly():
    entries = [('a', ProperList(3, range(20), features=[ProperInterval(3,5), ProperInterval(neginf,2)])),
               ('b', EmptyList(features=[ProperInterval(12,posinf)])),
               ('c', ProperList(-2, range(8))),
               ('d', ProperList(0, range(6), features=[ProperInterval(1,2)]))]
    a = Assembly(entries, features=[ProperInterval(0,3)])
    # Do iterators work?
    assert list(iter(a)) == [x[0] for x in entries]
    assert list(a.iterkeys()) == [x[0] for x in entries]
    assert list(a.itervalues()) == [x[1] for x in entries]
    assert list(a.iteritems()) == entries
    # Do filters work?
    assert a.filterkeys(lambda k: k=='a' or k=='b') == Assembly(entries[0:2], features=[ProperInterval(0,3)])
    assert a.filteritems(lambda k,v: 5 in v.support()) == Assembly([entries[0]] + entries[2:], features=[ProperInterval(0,3)])
    assert a.filtervalues(lambda v: 5 in v.support()) == Assembly([entries[0]] + entries[2:], features=[ProperInterval(0,3)])
    # Do maps work?
    assert a.mapkeys(lambda k,v: k+'x') == Assembly([(x[0]+'x', x[1]) for x in entries], features=[ProperInterval(0,3)])
    assert a.mapvalues(lambda k,v: v[0:5]) == Assembly([(x[0],x[1][0:5]) for x in entries], features=[ProperInterval(0,3)])
    assert a.mapitems(lambda k,v: (k+'x', v[0:5])) == Assembly([(x[0]+'x', x[1][0:5]) for x in entries], features=[ProperInterval(0,3)])
    # Do shifts work?
    assert (a >> 2) << 2 == a
    assert ProperList(0, [1,2], features=[interval(3,5)]) >> 2 == ProperList(2, [1,2], features=[interval(5,7)])
    # Does appending work?
    assert Assembly([('ax', EmptyList())], features=[ProperInterval(0,3)]) + \
        Assembly([('bx', EmptyList())], features=[ProperInterval(3,5)]) == \
        Assembly([('ax', EmptyList()), ('bx', EmptyList())],
                 features=[ProperInterval(0,3),ProperInterval(3,5)])
    # Does support work?
    assert a.left() == -2
    assert a.right() == 23
    assert a.support() == ProperInterval(-2,23)
    assert a.support('b') == EmptyInterval()
    assert a.support('a', 'd') == ProperInterval(3,6)
    # Does iterating columns work?
    a = Assembly([('a', ProperList(1, [1,2,3,4,5])),
                  ('b', ProperList(4, [1,2,3,4,5]))])
    assert list(a.itercolumns()) == [(1, OrderedDict([('a',1),('b',None)])),
                                     (2, OrderedDict([('a',2),('b',None)])),
                                     (3, OrderedDict([('a',3),('b',None)])),
                                     (4, OrderedDict([('a',4),('b',1)])),
                                     (5, OrderedDict([('a',5),('b',2)])),
                                     (6, OrderedDict([('a',None),('b',3)])),
                                     (7, OrderedDict([('a',None),('b',4)])),
                                     (8, OrderedDict([('a',None),('b',5)]))]
    assert list(a.itercolumns(start=3,end=5)) == \
        [(3, OrderedDict([('a',3),('b',None)])),
         (4, OrderedDict([('a',4),('b',1)]))]
    # Does width work?
    a = Assembly([('a', ProperList(1, [1,2,3,4,5])),
                  ('b', ProperList(4, [1,2,3,4,5]))])
    assert Assembly([]).width() == 0
    assert a.width() == 8
    assert a.width('a') == 5
    assert a.width('a','b') == 2

# Serialization
def test_serialize(tmpdir):
    assert affine_hooks({'__ProperInterval': True, 'left': 5, 'right': 12, 'a': 3}) == ProperInterval(5,12,a=3)

    a = Assembly([('a', ProperList(3, range(20), features=[ProperInterval(3,5), ProperInterval(neginf,2)])),
                  ('b', EmptyList(features=[ProperInterval(12,posinf)])),
                  ('c', ProperList(-2, range(8))),
                  ('d', ProperList(0, range(6), features=[ProperInterval(1,2,red=55,green=12,blue=13,alpha=0.5)]))],
                 features=[ProperInterval(0,3,name='boris')])

    assert deserializes("""{"__Assembly": true, "items": [["a", {"__ProperList": true, "offset": 3, "values": [1,2,3]}]]}""") == \
        Assembly([('a', ProperList(3, [1,2,3]))])

    newa = deserializes(a.serialize())
    assert a.keys() == newa.keys()
    for k in a.keys():
        assert a[k] == newa[k]
    assert a.metadata == newa.metadata

    t = tmpdir.join('afile')
    a.serialize(str(t))
    assert deserialize(str(t)) == a

    
    

def test_render_feature():
    assert renderfeature(ProperInterval(3, 5, name='boris', red=255, blue=0, green=0, alpha=0.3)) == \
        """<div class="feature" id="boris" style="background-color: rgba(255, 0, 0, 0.3);"></div>"""

def test_rendernucleotide():
    print rendernucleotide(3, 'A')
    assert rendernucleotide(3, 'A') == """<span style="color: green;">A</span>"""

  
def test_assembly_coordinates():
    a = Assembly([('a', ProperList(1, [1,2,3,4,5])),
                  ('b', ProperList(3, [1,2,3,4,5]))])
    assert a.coordinates() == [1,2,3,4,5,6,7]
      
def test_assembly_render():
    a = Assembly([('bases', ProperList(8, ['A','C','T','T','N','R','T','A','G'],
                                       trackclass='nucleotide')),
                  ('a', ProperList(1, range(50), 
                                   trackclass='integer',
                                   features=[ProperInterval(6, 12, name='b', red=0, green=255, blue=0, alpha=0.4)])),
                  ('q', ProperList(3, [{'A': [(0,0), (1,1)],
                                        'C': [(0,1), (1,0)],
                                        'T': [(0, 0.5), (1, 0.5)],
                                        'G': [(0, 0.25), (1,0.25)]},
                                       {'A': [(0,0), (1,1)],
                                        'C': [(0,1), (1,0)],
                                        'T': [(0, 0.5), (1, 0.5)],
                                        'G': [(0, 0.25), (1,0.25)]}],
                                   trackclass="svg")),
                  ('b', ProperList(4, [1,2,3,4,5], trackclass='integer'))],
                 features=[ProperInterval(11, 15, name='q', red=255, green=0, blue=0, alpha=0.3)])
    s = renderassembly(a)
    with open('assembly_render_test.html','w') as o:
        print >>o, "<html><head><style>"
        print >>o, css
        print >>o, "</style></head><body>"
        print >>o, s
        print >>o, "</body></html>"

def test_tracealong():
    template = ProperList(3, 'ACTG-TT--GGG')
    assert tracealong([1]*2, template) == ProperList(3, [1]*2)
    assert tracealong([1]*9, template) == ProperList(3, [1,1,1,1,None,1,1,None,None,1,1,1])
    assert tracealong([1]*12, template) == ProperList(3, [1,1,1,1,None,1,1,None,None,1,1,1,1,1,1])

def test_alzip():
    a = ProperList(2, [1]*3)
    b = ProperList(0, [1]*6)
    assert alzipsupport(a,b) == ProperList(0, [(None,1), (None,1), (1,1), (1,1), (1,1), (None, 1)])
    assert alzipnarrow(a,b) == ProperList(2, [(1,1), (1,1), (1,1)])

def test_almap():
    a = ProperList(3, [1,2,3])
    assert almap(lambda i,x: x+1, a) == ProperList(3, [2,3,4])
    assert almap((lambda i,x: x), a, start = 0, end = 7) == ProperList(0, [None,None,None,1,2,3,None])


if __name__=='__main__':
    test_affinelist_narrowto()
