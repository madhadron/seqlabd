"""
assembly.py - Data structures for assemblies

This module provides data structures that make working with sequence
assemblies simple. A particular track is specified as an AffineList
(essentially, a list that knows where it begins in a 1D, discrete
space and is indexed by global coordinates as opposed to its own
indices. An assembly of tracks is stored in an Assembly, which
provides methods to subset and iterate over hunks of tracks.
"""

import itertools as it
import json
import collections
import bz2
import templet

class HalfOpenInterval(object):
    """Represents a half open interval [a,b), a <= b.

    Working with AffineLists and Assemblies, we regularly want to
    combine and compare various half open intervals. You can test if a
    coordinate is in a HalfOpenInterval using Python's ``in``
    command::

        3 in HalfOpenInterval(2,6)

    Or take the intersection with ``intersect``. To quickly get a
    2-tuple (a,b), call the ``bounds`` method. The individual
    coordinates are in the fields ``left`` and ``right``.

    HalfOpenInterval does not provide union or complement methods
    since the results of those need not be HalfOpenIntervals.
    """
    def __init__(self, a, b):
        """Create a HalfOpenInterval [a,b)."""
        assert a <= b
        self.left = a
        self.right = b
    def __contains__(self, x):
        """Calculate x in [a,b)."""
        return self.left <= x and x < self.right
    def __eq__(self, other):
        return self.left == other.left and self.right == other.right
    def __repr__(self):
        return "HalfOpenInterval(%s,%s)" % (str(self.left), str(self.right))
    def bounds(self):
        """Return the HalfOpenInterval as a 2-tuple (a,b)."""
        return (self.left, self.right)
    def intersect(self, other):
        """Intersect two HalfOpenIntervals.

        Empty intersections are canonically set to HalfOpenInterval(0,0).
        """
        if self.left >= other.right or other.left >= self.right:
            return HalfOpenInterval(0,0)
        else:
            left = max(self.left, other.left)
            right = min(self.right, other.right)
            if left == right:
                return HalfOpenInterval(0,0)
            else:
                return HalfOpenInterval(left, right)

class Feature(object):
    def __init__(self, name, left, right, red, green, blue, alpha):
        self.name = name
        self.pos = HalfOpenInterval(left, right)
        assert 0 <= red < 256
        assert 0 <= green < 256
        assert 0 <= blue < 256
        assert 0 <= alpha <= 1
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha
    def __contains__(self, x):
        return x in self.pos
    def bounds(self):
        return self.pos
    @templet.stringfunction
    def render(self):
        """<div class="feature" style="background-color: rgba(${self.red}, ${self.green}, ${self.blue}, ${self.alpha});"></div>"""



class AffineList(object):
    """List embedded in 1D, discrete, affine space.

    Essentially, it's a list with an offset and methods altered to
    work in terms of global coordinates instead of indices. Create it
    by specifying an offset and an iterable of values, as in::

        a = AffineList(offset=3, vals=[1,2,3,4,5])

    Most of the usual list functions are available, but work a little
    differently. ``index`` is replaced with ``find``, a more powerful
    and general function.

    Fetching items or slices is done with coordinates, not indices
    into the list, so ``a[4]`` in the list above is 2. The first item
    in the list is at the offset. Any items from outside the actual
    list are returned as ``None``.

    You can shift an AffineList left or right with the ``<<`` and
    ``>>`` operators, so::

        AffineList(3, [1]) << 1 == AffineList(2, [1])

    The method ``support`` returns a HalfOpenInterval specifying where
    the AffineList's items lie, and ``itercoords`` is equivalent to
    ``enumerate()`` on a normal list, but returns the coordinates
    instead of the indices.
    """
    def __init__(self, offset, vals, renderitem=lambda i: "", trackclass="", features=[]):
        self.offset = offset
        self.vals = list(vals)
        self.renderitem = renderitem
        self.trackclass = trackclass
        self.features = features
    def __getitem__(self, i):
        if i < self.offset or i >= self.offset+len(self.vals):
            return None
        else:
            return self.vals[i - self.offset]
    def __getslice__(self, i, j):
        if i==None:
            i = 0
        if j==None:
            j = self.offset + len(self.vals)
        newoffset = max(self.offset-i, 0)
        left = max(i-self.offset, 0)
        right = max(j-self.offset, 0)
        newvals = self.vals[left:right]
        if newvals == []: # Must impose a canonical offset on empty lists
            return AffineList(0, [])
        else:
            return AffineList(offset=newoffset, vals=newvals)
    def __rshift__(self, i):
        return AffineList(offset=self.offset+i, vals=self.vals)
    def __lshift__(self, i):
        return AffineList(offset=self.offset-i, vals=self.vals)
    def support(self):
        """Return the HalfOpenInterval containing the support of this list.

        For example, ``AffineList(offset=1, vals=[1,2]).support()`` is
        ``HalfOpenInterval(1,3)``.
        """
        return HalfOpenInterval(self.offset, self.offset + len(self.vals))
    def iter(self, start=None, end=None):
        """Return an iterator over the elements in the support of this list."""
        return it.imap(lambda (a,b): b, self.itercoords(start=start, end=end))
    def itercoords(self, start=None, end=None):
        """Return an iterator over (coordinate,item) pairs in the support of this list.

        You can specify *start* and *end* in coordinates to return
        some other range. Any items returns outside of the support are
        denoted ``None``.
        """
        if start == None:
            start = self.offset
        if end == None:
            end = self.offset + len(self.vals)
        for i in range(start, end):
            yield (i,self[i])
    def __repr__(self):
        return 'AffineList(offset=%d, vals=%s)' % (self.offset, repr(self.vals))
    def __len__(self):
        return len(self.vals)
    def append(self, x):
        """Append *x* as an item to the end of this list."""
        self.vals.append(x)
        return self
    def insert(self, i, x):
        """Insert *x* at coordinate *i*.

        The list is properly extended with ``None``s if *i* is outside
        the list's support.
        """
        if i in self.support():
            self.vals.insert(i-self.offset, x)
        elif i < self.offset:
            self.vals = [x] + [None]*(self.offset-i-1) + self.vals
            self.offset = i
        else: # i off to right of support
            self.vals = self.vals + [None]*(i - (self.offset+len(self.vals))) + [x]
        return self
    def extend(self, vals):
        """Append all items in *vals* to the end of the list."""
        self.vals.extend(vals)
        return self
    def find(self, template, all=False, start=None, end=None):
        """Find the coordinates matching *template*.

        *template* may be a value or a callable object. If callable,
        it is treated as a predicate. Specifying ``all=True`` makes
        ``find`` return all coordinates where the template is matched.
        Otherwise it returns only the first. *start* and *end* can be
        used to restrict the search area.
        """
        if not(callable(template)):
            f = lambda x: x==template
        else:
            f = template
        if start == None:
            start = self.support().left
        if end == None:
            end = self.support().right
        
        coords = []
        for i in range(start, end):
            if f(self[i]):
                if all:
                    coords.append(i)
                else:
                    return i
        return coords
    def __setitem__(self, i, x):
        if i in self.support():
            self.vals[i-self.offset] = x
        elif i < self.offset:
            self.vals = [x] + [None]*(self.offset-i-1) + self.vals
            self.offset = i
        else: # i off to right of support
            self.vals = self.vals + [None]*(i - (self.offset+len(self.vals))) + [x]
        return x
    def __eq__(self, other):
        return self.offset == other.offset and self.vals == other.vals
    @templet.stringfunction
    def render(self, additionalfeatures=[], start=None, end=None):
        """<div class="track ${self.trackclass}">
${[self.renderitem(i,v, self.features + additionalfeatures) 
   for i,v in self.itercoords(start=start, end=end)]}
</div>"""

class Assembly(collections.OrderedDict):
    """Class representing an assembly of sequences.

    ``Assembly`` is an extension of an ordered dictionary. All its
    values should be ``AffineList`` objects. It provides numerous
    methods to make working with such collections simple. It also has
    a slot ``metadata`` to store information about the assembly. The
    ``metadata`` is properly propogated through all operations on
    ``Assembly``.
    """
    def __init__(self, items, metadata={}, features=[]):
        collections.OrderedDict.__init__(self, items)
        self.metadata = metadata
        self.features = features
    def filterkeys(self, pred):
        """Return an Assembly containing only the items for which *pred*(key) is true."""
        return Assembly([(k,v) for k,v in self.iteritems() if pred(k)], metadata=self.metadata)
    def filteritems(self, pred):
        """Return an Assembly containing only the items for which *pred*(key,value) is true."""
        return Assembly([(k,v) for k,v in self.iteritems() if pred(k,v)], metadata=self.metadata)
    def filtervalues(self, pred):
        """Return an Assembly containing only the items for which *pred*(value) is true."""
        return Assembly([(k,v) for k,v in self.iteritems() if pred(v)], metadata=self.metadata)
    def mapkeys(self, fun):
        """Return an Assembly where the keys are replaced by *fun*(key,val)."""
        return Assembly([(fun(k,v), v) for k,v in self.iteritems()], metadata=self.metadata)
    def mapitems(self, fun):
        """Return an Assembly with items replaced by 2-tuples returned by *fun*(key,val)."""
        return Assembly([fun(k,v) for k,v in self.iteritems()], metadata=self.metadata)
    def mapvalues(self, fun):
        """Return an Assembly with values replaced by *fun*(key,value)."""
        return Assembly([(k,fun(k,v)) for k,v in self.iteritems()], metadata=self.metadata)
    def __add__(self, other):
        """Append the entries in *other* to this.
        
        There must not be any duplicate keys.
        """
        return Assembly([(k,v) for k,v in self.iteritems()] + \
                            [(k,v) for k,v in other.iteritems()], metadata=self.metadata)
    def support(self, *keys):
        """Return the support of the intersection of *keys*.

        If there are no arguments (keys is ``[]``), returns the
        HalfOpenInterval of the support of all data in the assembly.
        Otherwise, the keys are taken to be keys into the dict, and
        the HalfOpenInterval of the intersection of the support of
        each key's value is returned.
        """
        v = HalfOpenInterval(min([v.offset for v in self.itervalues()] or [0]),
                             max([v.offset+len(v) for v in self.itervalues()] or [0]))
        for k in keys:
            v = v.intersect(self[k].support())
        return v
    def itercolumns(self, start=None, end=None):
        """Iterate over columns in the Assembly.

        Each column is yielded as a 2-tuple of
        (coordinate,OrderedDict), where OrderedDict has the same keys
        as the original, but with a single item as its key. If *start*
        and *end* are omitted, it iterates over the whole support of
        the ``Assembly``.
        """
        whole = self.support()
        if start == None:
            start = whole.left
        if end == None:
            end = whole.right
        for i in range(start,end):
            yield (i,collections.OrderedDict([(k,v[i]) for k,v in self.iteritems()]))
    def subset(self, start=0, end=None):
        """Return an Assembly of a subset of columns.

        If *start* and *end* are omitted, returns the Assembly itself.
        Otherwise, returns an Assembly with its origin at *start* and
        with all the columns out to *end*.
        """
        if isinstance(start, HalfOpenInterval):
            end = start.right
            start = start.left
        if end == None:
            end = self.support().right
        return Assembly([(k, v[start:end]) for k,v in self.iteritems()], metadata=self.metadata)
    def narrowto(self, *keys):
        """Return an Assembly subset to the support of *keys*.

        *keys* is specified in the same way as for the ``support`` method.
        """
        print self.support(*keys)
        return self.subset(self.support(*keys))
    def width(self, *keys):
        """Return the width of the support of *keys* in the Assembly.

        If *keys* is empty, then the width of the whole assembly.
        *keys* is specified as for the ``support`` method.
        """
        s = self.support(*keys)
        return s.right - s.left
    @templet.stringfunction
    def render(self):
        """ """
        

def as_assembly(dct):
    if '__Assembly' in dct:
        return Assembly(dct['tracks'], metadata=dct['metadata'])
    elif '__AffineList' in dct:
        return AffineList(offset=dct['offset'], vals=dct['vals'])
    else:
        return dct

class AssemblyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, AffineList):
            return {'__AffineList': True, 'offset': obj.offset, 'vals': obj.vals}
        elif isinstance(obj, Assembly):
            return {'__Assembly': True, 'metadata': obj.metadata, 
                    'tracks': [(k,v) for k,v in obj.iteritems()]}
        else:
            return json.JSONEncoder.default(self, obj)
            
def serialize(obj, filename):
    """Dump *obj* to *filename* as bz2 compressed JSON."""
    with bz2.BZ2File(filename, 'w') as out:
        json.dump(obj, out, cls=AssemblyEncoder)

def deserialize(filename):
    """Load an object from a bz2 compressed JSON file *filename*."""
    with bz2.BZ2File(filename, 'r') as input:
        return json.load(input, object_hook=as_assembly)
    
@templet.stringfunction
def renderinteger(coord, val, features):
    """<div>
  ${val == None and "&nbsp;" or val}
  ${[f.render() for f in features if coord in f]}
</div>"""

def base_color(base):
    base_coloring = {'A': 'green', 'C': 'blue', 'T': 'red', 
                     'G': 'black', 'U': 'red', 'X': 'black'}
    try:
        return base_coloring[base]
    except KeyError:
        return 'yellow'

@templet.stringfunction
def rendernucleotide(coord, val, features):
    """<div>
  ${val == None and "&nbsp;" or '<span style="color: %s;">%s</span>' % (base_color(val), val)}
  ${[f.render() for f in features if coord in f]}
</div>"""
    
css = """
div.track div { position: relative; display: inline-block; width: 1.5em; height: 1.5em; margin: 0; padding: 0; }
div.track div div.feature { position: absolute; top: 0; bottom: 0; left: 0; right: 0; z-index: +2; }
"""