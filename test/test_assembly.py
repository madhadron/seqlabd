import common
from seqlab.assembly import *
import os
import random

# Intervals
def test_intervals():
    # Does the intersection convenience function work?
    assert intersection(hoi(1,3), hoi(5,7)) == hoi(1,3).intersect(hoi(5,7))
    # Is intersection idempotent?
    assert intersection(hoi(1,3), hoi(1,3)) == hoi(1,3)
    # Is the empty set a zero of intersection?
    assert intersection(hoi(1,3), EmptyInterval()) == EmptyInterval()
    # Do disjoint intervals intersect to empty?
    assert intersection(hoi(1,3), hoi(5,7)) == EmptyInterval()
    # Does the closure convenience function work?
    assert closure(hoi(1,3), hoi(5,7)) == hoi(1,3).closure(hoi(5,7))
    # Is closure idempotent?
    assert closure(hoi(1,3), hoi(1,3)) == hoi(1,3)
    # Empty is a unit of closure
    assert closure(hoi(1,3), EmptyInterval()) == hoi(1,3)
    # Are intervals containing posinf and neginf infinite?
    for i in [hoi(neginf,posinf), hoi(neginf,5), hoi(5,posinf), hoi(3,5)]:
        assert i.isfinite() != i.isinfinite()
        assert i.isinfinite() == (i.left() == neginf or i.right() == posinf)
    # Does contains work?
    assert 3 in hoi(1,6)
    assert not(3 in hoi(5,6))
    assert not(3 in EmptyInterval())
    assert 3 in hoi(neginf,posinf)
    assert not(3 in hoi(neginf,0))
    assert not(3 in hoi(5,posinf))
    # Does width work?
    for i in [hoi(neginf,posinf), hoi(1,3), hoi(neginf,3), hoi(1,posinf)]:
        assert i.width() == i.right() - i.left()
    assert EmptyInterval().width() == 0
    # Are metadata propogated properly?
    assert closure(EmptyInterval(a=3),EmptyInterval(b=5)) == EmptyInterval(a=3,b=5)
    assert closure(hoi(3,8,a=3),hoi(3,8,b=5)) == hoi(3,8,a=3,b=5)
    assert intersection(EmptyInterval(a=3),EmptyInterval(b=5)) == EmptyInterval(a=3,b=5)
    assert intersection(hoi(3,8,a=3),hoi(3,8,b=5)) == hoi(3,8,a=3,b=5)
    # Are metadata left weighted?
    assert closure(EmptyInterval(a=3),EmptyInterval(a=5)) == EmptyInterval(a=3)
    assert closure(hoi(3,8,a=3), hoi(3,8,a=5)) == hoi(3,8,a=3)
    # Does strip remove metadata?
    assert EmptyInterval(a=3).strip() == EmptyInterval()
    assert hoi(3,8,a=3).strip() == hoi(3,8)

# Affine lists
def test_affinelist():
    a = AffineList(offset=0, vals=range(20))
    # Shifting commutes with subsetting in the expected way for coordinates
    assert a[5:10] >> 3 == (a >> 3)[8:13]
    assert a[hoi(5,10)] << 3 == (a << 3)[2:7]
    assert EmptyList() << 3 == EmptyList()
    assert EmptyList() >> 3 == EmptyList()
    # Are shifting operators inverses?
    assert (a >> 3) << 3 == a
    # Fetching outside the range returns None
    for i in range(-20,50):
        assert a[i] == None if i < 0 or i >= 20 else i
        assert EmptyList()[i] == None
    # Is featuresat sane?
    b = AffineList(offset=3, vals=[1,2,3,4,5], 
                   features=[hoi(neginf,5), hoi(1,4), hoi(3,posinf)])
    assert b.featuresat(-10) == [hoi(neginf,5)]
    assert b.featuresat(3) == [hoi(neginf,5), hoi(1,4), hoi(3,posinf)]
    # Is support sane?
    assert a.support() == hoi(0,20)
    assert EmptyList().support() == EmptyInterval()
    # Does width work?
    assert a.width() == a.right() - a.left()
    # Does iteration work?
    assert list(iter(a)) == zip(range(20),range(20))
    # Do list operations work?
    a.append(20)
    assert a == AffineList(0, range(21))
    a.insert(-1,-1)
    assert a == AffineList(-1, range(-1,21))
    a.extend([21,22])
    assert a == AffineList(-1, range(-1,23))
    # Does find work?
    assert AffineList(3, [1,2,3,4,5]).find(lambda x: x%2==0, all=True) == [4,6]
    assert AffineList(3, [1,2,3,4,5]).find(lambda x: x%2==0) == 4
    assert AffineList(3, [1,2,1,2,1]).find(1, all=True) == [3,5,7]
    assert AffineList(3, [1,2,1,2,1]).find(1) == 3
    assert AffineList(3, [1,2,1,2,1]).find(1, all=True, start=4) == [5,7]
    assert AffineList(3, [1,2,1,2,1]).find(1, all=True, end=5) == [3]
    # Does setting items work, in the support and to both sides of it?
    a = AffineList(3, [1,2,3,4,5]); a[3] = 0
    assert a == AffineList(3, [0,2,3,4,5])
    a = AffineList(3, [1,2,3,4,5]); a[1] = 0
    assert a == AffineList(1, [0,None,1,2,3,4,5])
    a = AffineList(3, [1,2,3,4,5]); a[9] = 0
    assert a == AffineList(3, [1,2,3,4,5,None,0])
    # Is metadata propogated properly?
    c = AffineList(3, range(20), a=12)
    assert c[3:4].metadata == c.metadata
    

# Assemblies
def test_assembly():
    entries = [('a', AffineList(3, range(20), features=[hoi(3,5), hoi(neginf,2)])),
               ('b', EmptyList(features=[hoi(12,posinf)])),
               ('c', AffineList(-2, range(8))),
               ('d', AffineList(0, range(6), features=[hoi(1,2)]))]
    a = Assembly(entries, features=[hoi(0,3)])
    # Do iterators work?
    assert list(iter(a)) == [x[0] for x in entries]
    assert list(a.iterkeys()) == [x[0] for x in entries]
    assert list(a.itervalues()) == [x[1] for x in entries]
    assert list(a.iteritems()) == entries
    # Do filters work?
    assert a.filterkeys(lambda k: k=='a' or k=='b') == Assembly(entries[0:2], features=[hoi(0,3)])
    assert a.filteritems(lambda k,v: 5 in v.support()) == Assembly([entries[0]] + entries[2:], features=[hoi(0,3)])
    assert a.filtervalues(lambda v: 5 in v.support()) == Assembly([entries[0]] + entries[2:], features=[hoi(0,3)])
    # Do maps work?
    assert a.mapkeys(lambda k: k+'x') == Assembly([(x[0]+'x', x[1]) for x in entries], features=[hoi(0,3)])
    assert a.mapvalues(lambda v: v[0:5]) == Assembly([(x[0],x[1][0:5]) for x in entries], features=[hoi(0,3)])
    assert a.mapitems(lambda k,v: (k+'x', v[0:5])) == Assembly([(x[0]+'x', x[1][0:5]) for x in entries], features=[hoi(0,3)])
    # Does appending work?
    assert Assembly([('ax', AffineList(0,[]))], features=[hoi(0,3)]) + \
        Assembly([('bx', AffineList(0,[]))], features=[hoi(3,5)]) == \
        Assembly([('ax', AffineList(0,[])), ('bx', AffineList(0,[]))],
                 features=[hoi(0,3),hoi(3,5)])
    # Does support work?
    assert a.support() == hoi(-2,23)
    assert a.support('b') == EmptyInterval()
    assert a.support('a', 'd') == hoi(3,6)
    # Does iterating columns work?
    a = Assembly([('a', AffineList(1, [1,2,3,4,5])),
                  ('b', AffineList(4, [1,2,3,4,5]))])
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
    a = Assembly([('a', AffineList(1, [1,2,3,4,5])),
                  ('b', AffineList(4, [1,2,3,4,5]))])
    assert Assembly([]).width() == 0
    assert a.width() == 8
    assert a.width('a') == 5
    assert a.width('a','b') == 2

# Serialization

def test_json_dumpload():
    import json
    altxt = """{"__AffineList": true,
                "offset": 3,
                "vals": [1,2,3,4,5],
                "features": [],
                "trackclass": "integer"}"""
    alval = AffineList(3, [1,2,3,4,5], trackclass='integer', features=[])
    astxt = """{"__Assembly": true,
                "features": [],
                "metadata": {"boris": "hilda", "meep": 3},
                "tracks": [["b", {"__AffineList": true, "offset": 1, "vals": [1,2,3], 
                                  "features": [], "trackclass": "integer"}],
                           ["a", {"__AffineList": true, "offset": 3, "vals": [4,4,4], 
                                  "features": [], "trackclass": "integer"}]]}"""
    asval = Assembly([('b', AffineList(1, [1,2,3], trackclass='integer', features=[])),
                      ('a', AffineList(3, [4,4,4], trackclass='integer', features=[]))],
                     metadata={'boris': 'hilda', 'meep': 3})
    assert json.loads(altxt, object_hook=as_assembly) == alval
    assert json.loads(astxt, object_hook=as_assembly) == asval
    assert json.loads(json.dumps(alval, cls=AssemblyEncoder), object_hook=as_assembly) == alval
    assert json.loads(json.dumps(asval, cls=AssemblyEncoder), object_hook=as_assembly) == asval

def test_serialize_deserialize():
    a = Assembly([('b', AffineList(1, [1,2,3])),
                  ('a', AffineList(3, [4,4,4]))],
                 metadata={'boris': 'hilda', 'meep': 3})
    import tempfile
    filename = tempfile.mktemp()
    serialize(a, filename)
    assert deserialize(filename) == a
    os.unlink(filename)
    

def test_render_feature():
    assert Feature('boris', 3, 5, 255, 0, 0, 0.3).render() == \
        """<div class="feature" id="boris" style="background-color: rgba(255, 0, 0, 0.3);"></div>"""

def test_rendernucleotide():
    print rendernucleotide(3, 'A')
    assert rendernucleotide(3, 'A') == """<span style="color: green;">A</span>"""

  
def test_assembly_coordinates():
    a = Assembly([('a', AffineList(1, [1,2,3,4,5])),
                  ('b', AffineList(3, [1,2,3,4,5]))])
    assert a.coordinates() == [1,2,3,4,5,6,7]
      
def test_assembly_render():
    a = Assembly([('bases', AffineList(8, ['A','C','T','T','N','R','T','A','G'],
                                       trackclass='nucleotide')),
                  ('a', AffineList(1, range(50), 
                                   trackclass='integer',
                                   features=[Feature('b', 6,12, 0,255,0, 0.4)])),
                  ('q', AffineList(3, [{'A': [(0,0), (1,1)],
                                        'C': [(0,1), (1,0)],
                                        'T': [(0, 0.5), (1, 0.5)],
                                        'G': [(0, 0.25), (1,0.25)]},
                                       {'A': [(0,0), (1,1)],
                                        'C': [(0,1), (1,0)],
                                        'T': [(0, 0.5), (1, 0.5)],
                                        'G': [(0, 0.25), (1,0.25)]}],
                                   trackclass="svg")),
                  ('b', AffineList(4, [1,2,3,4,5], trackclass='integer'))],
                 features=[Feature('q', 11,15, 255,0,0, 0.3)])
    s = renderassembly(a)
    with open('assembly_render_test.html','w') as o:
        print >>o, "<html><head><style>"
        print >>o, css
        print >>o, "</style></head><body>"
        print >>o, s
        print >>o, "</body></html>"

def test_tracealong():
    template = AffineList(3, 'ACTG-TT--GGG')
    assert tracealong([1]*2, template) == AffineList(3, [1]*2)
    assert tracealong([1]*9, template) == AffineList(3, [1,1,1,1,None,1,1,None,None,1,1,1])
    assert tracealong([1]*12, template) == AffineList(3, [1,1,1,1,None,1,1,None,None,1,1,1,1,1,1])

def test_alzip():
    a = AffineList(2, [1]*3)
    b = AffineList(0, [1]*6)
    assert alzipsupport(a,b) == AffineList(0, [(None,1), (None,1), (1,1), (1,1), (1,1), (None, 1)])
    assert alzipnarrow(a,b) == AffineList(2, [(1,1), (1,1), (1,1)])

def test_almap():
    a = AffineList(3, [1,2,3])
    assert almap(lambda i,x: x+1, a) == AffineList(3, [2,3,4])
    assert almap((lambda i,x: x), a, start = 0, end = 7) == AffineList(0, [None,None,None,1,2,3,None])


if __name__=='__main__':
    test_affinelist_narrowto()
