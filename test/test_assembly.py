import common
from seqlab.assembly import *
import os

def test_halfopeninterval_intersect():
    assert HalfOpenInterval(1,3).intersect(HalfOpenInterval(5,7)) == HalfOpenInterval(0,0)
    assert HalfOpenInterval(1,3).intersect(HalfOpenInterval(1,2)) == HalfOpenInterval(1,2)

def test_halfopeninterval_closure():
    assert HalfOpenInterval(1,3).closure(HalfOpenInterval(5,7)) == HalfOpenInterval(1,7)
    assert HalfOpenInterval(1,3).closure(HalfOpenInterval(0,0)) == HalfOpenInterval(1,3)
    assert HalfOpenInterval(1,3).closure(HalfOpenInterval(1,3)) == HalfOpenInterval(1,3)
    assert HalfOpenInterval(0,0).closure(HalfOpenInterval(1,3)) == HalfOpenInterval(1,3)

def test_halfopeninterval_contains():
    assert 3 in hoi(1,6)
    assert not(3 in hoi(5,6))
    assert not(3 in hoi(0,0))
    assert 3 in hoi(None,5)
    assert 3 in hoi(1, None)
    assert not(3 in hoi(None, 1))
    assert not(3 in hoi(5,None))

def test_intersection():
    assert intersection(hoi(0,0), hoi(3,6), hoi(3,5)) == hoi(3,5)

def test_affinelist_getitem():
    a = AffineList(offset=3, vals=[1])
    assert a[2] == None
    assert a[3] == 1
    assert a[4] == None
    assert a[HalfOpenInterval(0,4)] == AffineList(3, [1])

def test_affinelist_narrowto():
    a = AffineList(3, [1,2,3,4,5])
    assert a.narrowto() == AffineList(0, [1,2,3,4,5])
    assert a.narrowto(1, 6) == AffineList(2, [1,2,3])
    assert a.narrowto(4,6) == AffineList(0, [2,3])

def test_affinelist_getslice():
    a = AffineList(offset=3, vals=[1,2,3,4,5])
    assert a[0:4] == AffineList(3, [1])
    assert a[0:6] == AffineList(3, [1,2,3])
    assert a[4:6] == AffineList(4, [2,3])
    assert a[4:25] == AffineList(4, [2,3,4,5])
    assert a[25:28] == AffineList(0, [])
    assert a[0:2] == AffineList(0, [])

def test_affinelist_shifts():
    a = AffineList(offset=3, vals=[1,2,3,4,5])
    assert a << 3 == AffineList(0, [1,2,3,4,5])
    assert a >> 2 == AffineList(5, [1,2,3,4,5])
    assert a << 0 == a
    assert a >> 0 == a
    assert a >> 1 == a << -1
    assert a << 1 == a >> -1

def test_affinelist_support():
    assert AffineList(3, [1,2,3,4,5]).support() == HalfOpenInterval(3,8)
    assert AffineList(0, []).support() == HalfOpenInterval(0,0)
    assert AffineList(1, []).support() == HalfOpenInterval(1,1)
    assert AffineList(1, [3]).support() == HalfOpenInterval(1,2)

def test_affinelist_iter():
    a = AffineList(offset=3, vals=[1,2,3,4,5])    
    assert list(a.iter()) == [1,2,3,4,5]
    assert list(a.iter(start=0)) == [None,None,None,1,2,3,4,5]
    assert list(a.iter(start=0, end=2)) == [None,None]
    assert list(a.iter(start=0, end=9)) == [None,None,None,1,2,3,4,5,None]

def test_affinelist_itercoords():
    a = AffineList(offset=3, vals=[1,2,3,4,5])    
    assert list(a.itercoords()) == [(3,1),(4,2),(5,3),(6,4),(7,5)]
    assert list(a.itercoords(start=0)) == [(0,None),(1,None),(2,None),(3,1),
                                           (4,2),(5,3),(6,4),(7,5)]
    assert list(a.itercoords(start=0, end=2)) == [(0,None),(1,None)]
    assert list(a.itercoords(start=0, end=9)) == [(0,None),(1,None),(2,None),(3,1),(4,2),
                                            (5,3),(6,4),(7,5),(8,None)]

def test_affinelist_repr():
    a = AffineList(offset=3, vals=[1,2,3,4,5])    
    assert eval(repr(a)) == a

def test_affinelist_append():
    a = AffineList(offset=3, vals=[1,2,3,4,5])
    assert a.append(1) == AffineList(3, [1,2,3,4,5,1])

def test_affinelist_insert():
    assert AffineList(3, [1,2,3,4,5]).insert(3,0) == AffineList(3, [0,1,2,3,4,5])
    assert AffineList(0, []).insert(0, 12) == AffineList(0, [12])
    assert AffineList(3, [1,2]).insert(1, 5) == AffineList(1, [5,None,1,2])
    assert AffineList(3, [1,2]).insert(7, 13) == AffineList(3, [1,2,None,None,13])

def test_affinelist_find():
    assert AffineList(3, [1,2,3,4,5]).find(lambda x: x%2==0, all=True) == [4,6]
    assert AffineList(3, [1,2,3,4,5]).find(lambda x: x%2==0) == 4
    assert AffineList(3, [1,2,1,2,1]).find(1, all=True) == [3,5,7]
    assert AffineList(3, [1,2,1,2,1]).find(1) == 3
    assert AffineList(3, [1,2,1,2,1]).find(1, all=True, start=4) == [5,7]
    assert AffineList(3, [1,2,1,2,1]).find(1, all=True, end=5) == [3]

def test_affinelist_setitem():
    a = AffineList(3, [1,2,3,4,5]); a[3] = 0
    assert a == AffineList(3, [0,2,3,4,5])
    a = AffineList(3, [1,2,3,4,5]); a[1] = 0
    assert a == AffineList(1, [0,None,1,2,3,4,5])
    a = AffineList(3, [1,2,3,4,5]); a[9] = 0
    assert a == AffineList(3, [1,2,3,4,5,None,0])

def test_assembly_init():
    a = Assembly([('qboris', AffineList(0,[])),
                  ('hilda', AffineList(0,[]))])
    assert list(a.iteritems()) == [('qboris', AffineList(0, [])),
                                   ('hilda', AffineList(0, []))]

def test_assembly_filters():
    a = Assembly([('ax', AffineList(3, [1,2,3])),
                  ('ay', AffineList(3, [2,5,6])),
                  ('bx', AffineList(0, [1,1,1]))])
    assert a.filterkeys(lambda k: k.startswith('a')) == \
        Assembly([('ax', AffineList(3, [1,2,3])),
                  ('ay', AffineList(3, [2,5,6]))])
    assert a.filteritems(lambda k,v: 5 in v.support()) == \
        Assembly([('ax', AffineList(3, [1,2,3])),
                  ('ay', AffineList(3, [2,5,6]))])
    assert a.filtervalues(lambda v: 5 in v.support()) == \
        Assembly([('ax', AffineList(3, [1,2,3])),
                  ('ay', AffineList(3, [2,5,6]))])

def test_assembly_maps():
    a = Assembly([('ax', AffineList(3, [1,2,3])),
                  ('ay', AffineList(3, [2,5,6])),
                  ('bz', AffineList(0, [1,1,1]))])
    assert a.mapkeys(lambda k,v: k[1]) == \
        Assembly([('x', AffineList(3, [1,2,3])),
                  ('y', AffineList(3, [2,5,6])),
                  ('z', AffineList(0, [1,1,1]))])
    assert a.mapitems(lambda k,v: (k,v[:5])) == \
        Assembly([('ax', AffineList(3, [1,2])),
                  ('ay', AffineList(3, [2,5])),
                  ('bz', AffineList(0, [1,1,1]))])
    assert a.mapvalues(lambda k,v: v[:5]) == \
        Assembly([('ax', AffineList(3, [1,2])),
                  ('ay', AffineList(3, [2,5])),
                  ('bz', AffineList(0, [1,1,1]))])

def test_assembly_adding():
    a = Assembly([('ax', AffineList(0,[]))])
    b = Assembly([('bx', AffineList(0,[]))])
    assert a+b == Assembly([('ax', AffineList(0,[])),
                            ('bx', AffineList(0,[]))])

def test_assembly_support():
    a = Assembly([('a', AffineList(1, [1,2,3,4,5])),
                  ('b', AffineList(4, [1,2,3,4,5]))])
    assert a.support() == HalfOpenInterval(1,9)
    assert a.support('a') == HalfOpenInterval(1,6)
    assert a.support('a', 'b') == HalfOpenInterval(4,6)

def test_assembly_itercolumns():
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

def test_assembly_subset():
    a = Assembly([('a', AffineList(1, [1,2,3,4,5])),
                  ('b', AffineList(4, [1,2,3,4,5]))])    
    assert a.subset(start=3,end=5) == \
        Assembly([('a', AffineList(0, [3,4])),
                  ('b', AffineList(1, [1]))])
    assert a.subset() == a
    assert a.subset(HalfOpenInterval(3,5)) == \
        Assembly([('a', AffineList(0, [3,4])),
                  ('b', AffineList(1, [1]))])

def test_assembly_narrowto():
    a = Assembly([('a', AffineList(1, [1,2,3,4,5])),
                  ('b', AffineList(4, [1,2,3,4,5]))])
    assert a.narrowto() == Assembly([('a', AffineList(0, [1,2,3,4,5])),
                                     ('b', AffineList(3, [1,2,3,4,5]))])
    assert a.narrowto('a') == Assembly([('a', AffineList(0, [1,2,3,4,5])),
                                        ('b', AffineList(3, [1,2]))])
    assert a.narrowto('a','b') == Assembly([('a', AffineList(0, [4,5])),
                                            ('b', AffineList(0, [1,2]))])
    
def test_assembly_width():
    a = Assembly([('a', AffineList(1, [1,2,3,4,5])),
                  ('b', AffineList(4, [1,2,3,4,5]))])
    assert Assembly([]).width() == 0
    assert a.width() == 8
    assert a.width('a') == 5
    assert a.width('a','b') == 2

def test_json_dumpload():
    import json
    altxt = """{"__AffineList": true,
                "offset": 3,
                "vals": [1,2,3,4,5]}"""
    alval = AffineList(3, [1,2,3,4,5])
    astxt = """{"__Assembly": true,
                "metadata": {"boris": "hilda", "meep": 3},
                "tracks": [["b", {"__AffineList": true, "offset": 1, "vals": [1,2,3]}],
                           ["a", {"__AffineList": true, "offset": 3, "vals": [4,4,4]}]]}"""
    asval = Assembly([('b', AffineList(1, [1,2,3])),
                      ('a', AffineList(3, [4,4,4]))],
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
        """<div class="feature" style="background-color: rgba(255, 0, 0, 0.3);"></div>"""

def test_rendernucleotide():
    print rendernucleotide(3, 'A')
    assert rendernucleotide(3, 'A') == """<span style="color: green;">A</span>"""

  
def test_assembly_coordinates():
    a = Assembly([('a', AffineList(1, [1,2,3,4,5])),
                  ('b', AffineList(3, [1,2,3,4,5]))])
    assert a.coordinates() == [1,2,3,4,5,6,7]
      
def test_assembly_render():
    a = Assembly([('bases', AffineList(8, ['A','C','T','T','N','R','T','A','G'],
                                       trackclass='nucleotide', renderitem=rendernucleotide)),
                  ('a', AffineList(1, range(50), 
                                   trackclass='integer', renderitem=renderinteger,
                                   features=[Feature('b', 6,12, 0,255,0, 0.4)])),
                  ('q', AffineList(3, [{'A': [(0,0), (1,1)],
                                        'C': [(0,1), (1,0)],
                                        'T': [(0, 0.5), (1, 0.5)],
                                        'G': [(0, 0.25), (1,0.25)]},
                                       {'A': [(0,0), (1,1)],
                                        'C': [(0,1), (1,0)],
                                        'T': [(0, 0.5), (1, 0.5)],
                                        'G': [(0, 0.25), (1,0.25)]}],
                                   trackclass="svg", renderitem=rendersvg)),
                  ('b', AffineList(4, [1,2,3,4,5], trackclass='integer', 
                                   renderitem=renderinteger))],
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


