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
from collections import defaultdict
try:
    from collections import OrderedDict
except:
    from ordereddict import OrderedDict
import bz2
import templet

# Utility methods
def max(a, b):
    if a == None and b == None:
        return None
    elif a == None:
        return b
    elif b == None:
        return a
    else:
        return a if a > b else b

def min(a, b):
    if a == None and b == None:
        return None
    elif a == None:
        return b
    elif b == None:
        return a
    else:
        return a if a < b else b

def dictunion(*dicts):
    new = {}
    for d in reversed(dicts):
        for k,v in d.iteritems():
            new[k] = v
    return new

def closure(*intervals):
    c = EmptyInterval()
    for i in intervals:
        c = c.closure(i)
    return c

def intersection(*intervals):
    c = ProperInterval(neginf,posinf)
    for i in intervals:
        c = c.intersection(i)
    return c

def support(*affinelists):
    c = EmptyInterval()
    for a in affinelists:
        c = c.closure(a.support())
    return c


# Positive and negative infinity
class NegInf(object):
    def __repr__(self):
        return "NegInf()"
    def __eq__(self, other):
        return isinstance(other,NegInf)
    def __lt__(self, other):
        return False if isinstance(other,NegInf) else True
    def __le__(self, other):
        return True
    def __gt__(self, other):
        return False
    def __ge__(self, other):
        return True if isinstance(other,NegInf) else False
    def __ne__(self, other):
        return not(isinstance(other,NegInf))
    def __sub__(self, other):
        return self
    def __rsub__(self, other):
        return posinf
    def __add__(self, other):
        return self
    def __radd__(self, other):
        return self
    def __mul__(self, other):
        if other == 0:
            raise ValueError("NegInf*0 is undefined.")
        elif other > 0:
            return self
        else:
            return posinf
    def __div__(self, other):
        if other == 0:
            raise ZeroDivisionError()
        elif other > 0:
            return self
        else:
            return posinf
    def __neg__(self):
        return posinf

class PosInf(object):
    def __repr__(self):
        return "PosInf()"
    def __eq__(self, other):
        return isinstance(other,PosInf)
    def __gt__(self, other):
        return False if isinstance(other,PosInf) else True
    def __ge__(self, other):
        return True
    def __lt__(self, other):
        return False
    def __le__(self, other):
        return True if isinstance(other,PosInf) else False
    def __ne__(self, other):
        return not(isinstance(other,PosInf))
    def __sub__(self, other):
        return self
    def __rsub__(self, other):
        return neginf
    def __add__(self, other):
        return self
    def __radd__(self, other):
        return self
    def __mul__(self, other):
        if other == 0:
            raise ValueError("NegInf*0 is undefined.")
        elif other > 0:
            return posinf
        else:
            return neginf
    def __div__(self, other):
        if other == 0:
            raise ZeroDivisionError()
        elif other > 0:
            return self
        else:
            return neginf
    def __neg__(self):
        return neginf

posinf = PosInf()
neginf = NegInf()

# Intervals
class Affine(object):
    def __init__(self, **kwargs):
        self.metadata = kwargs
    def left(self):
        return None
    def right(self):
        return None
    def strip(self):
        return self.__class__()
    def __rshift__(self, n):
        return self
    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
            self.metadata == other.metadata
    def width(self):
        return self.right() - self.left() if self.isproper() else 0
    def isempty(self):
        return True
    def isproper(self):
        return not(self.isempty())
    def __contains__(self, other):
        if self.isproper():
            if isinstance(other, Affine):
                return (other.left() >= self.left() and other.right <= self.right()) 
            else:
                return other >= self.left() and other < self.right()
        else:
            return False
    def isfinite(self):
        return self.width() < posinf
    def isinfinite(self):
        return not(self.isfinite())
    def __lshift__(self, n):
        return self >> -n
    def toorigin(self):
        return self << self.left() if self.isproper() else self
    def support(self):
        if self.isempty():
            return EmptyInterval()
        else:
            return ProperInterval(self.left(), self.right())
    def __repr__(self):
        return self.__class__.__name__ + "(" + ", ".join("%s=%s" % (k,repr(v)) for k,v in self.metadata.iteritems()) + ")"
    def __iter__(self):
        while False:
            yield None
    def iter(self, left=None, right=None):
        while False:
            yield None


class Interval(Affine):
    def intersection(self, other, **kwargs):
        pass
    def closure(self, other, **kwargs):
        pass


class EmptyInterval(Interval):
    def intersection(self, other):
        metadata = dictunion(self.metadata, other.metadata)
        return EmptyInterval(**metadata)
    def closure(self, other):
        metadata = dictunion(self.metadata, other.metadata)
        if other.isempty():
            return EmptyInterval(**metadata)
        else:
            return ProperInterval(other.left(), other.right(), **metadata)

class ProperInterval(Interval):
    def __init__(self, left, right, **kwargs):
        assert left <= right
        self._left = left
        self._right = right
        self.metadata = kwargs
    def left(self):
        return self._left
    def right(self):
        return self._right
    def strip(self):
        return ProperInterval(self._left, self._right)
    def isempty(self):
        return False
    def __rshift__(self, n):
        return ProperInterval(self._left+n, self._right+n,
                              **self.metadata)
    def __eq__(self, other):
        return isinstance(other, ProperInterval) and \
            self.left() == other.left() and \
            self.right() == other.right() and \
            self.metadata == other.metadata
    def __repr__(self):
        return "ProperInterval(%s, %s" % (self.left(), self.right()) + \
            "".join(", %s=%s" % (k,repr(v)) for k,v in self.metadata.iteritems()) + ")"
    def intersection(self, other):
        metadata = dictunion(self.metadata, other.metadata)
        if other.isempty():
            return EmptyInterval(**metadata)
        else:
            left = max(self.left(), other.left())
            right = min(self.right(), other.right())
            print left, right
            if right <= left:
                return EmptyInterval(**metadata)
            else:
                return ProperInterval(left, right, **metadata)
    def closure(self, other):
        metadata = dictunion(self.metadata, other.metadata)
        if other.isempty():
            return ProperInterval(self.left(), self.right(), **metadata)
        else:
            left = min(self.left(), other.left())
            stop = max(self.right(), other.right())
            return ProperInterval(left, stop, **metadata)
    def __iter__(self):
        for i in range(self.left(), self.right()):
            yield i
    def iter(self, start=None, stop=None):
        for i in range(max(start, self.left()),
                       min(stop, self.right())):
            yield i





class Feature(object):
    def __init__(self, name, left, right, red, green, blue, alpha):
        assert isinstance(name, str)
        assert isinstance(left, int) or left is None
        assert isinstance(right, int) or right is None
        assert isinstance(red, int)
        assert isinstance(green, int)
        assert isinstance(blue, int)
        assert isinstance(alpha, float)
        self.name = name
        self.pos = ProperInterval(left, right)
        assert 0 <= red < 256
        assert 0 <= green < 256
        assert 0 <= blue < 256
        assert 0 <= alpha <= 1
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha
    def __eq__(self, other):
        return self.name == other.name and \
            self.pos == other.pos and \
            self.red == other.red and self.green == other.green and self.blue == other.blue and \
            self.alpha == other.alpha
    def __repr__(self):
        return "Feature(%s, %s,%s, %s,%s,%s, %s)" % (repr(self.name), self.pos.left, self.pos.right, self.red,
                                                     self.green, self.blue, self.alpha)
    def __contains__(self, x):
        return x in self.pos
    def bounds(self):
        return self.pos
    @templet.stringfunction
    def render(self):
        """<div class="feature" id="${self.name}" style="background-color: rgba(${self.red}, ${self.green}, ${self.blue}, ${self.alpha});"></div>"""



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
    def __init__(self, offset, vals, trackclass="", features=[]):
        self.offset = offset
        self.vals = list(vals)
        self.trackclass = trackclass
        self.features = features
    def __getitem__(self, i):
        if isinstance(i, HalfOpenInterval):
            return self.__getslice__(i.left, i.right)
        if i < self.offset or i >= self.offset+len(self.vals):
            return None
        else:
            return self.vals[i - self.offset]
    def featureson(self, left=None, right=None):
        if left is None and right is None:
            pos = EmptyInterval()
        elif not(isinstance(left, HalfOpenInterval)):
            pos = ProperInterval(left,right)
        else:
            assert right is None
            pos = left
        return [f for f in self.features
                if f.pos.overlaps(pos)]
        
    def __getslice__(self, start, end):
        if start < self.offset:
            newoffset = self.offset
            newleft = 0
        elif start < self.offset + len(self):
            newoffset = start
            newleft = start - self.offset
        else:
            return AffineList(0, [], trackclass=self.trackclass, features = []) # Canonical empty list

        if end < self.offset:
            return AffineList(0, [], trackclass=self.trackclass, features=[])
        elif end < self.offset + len(self):
            return AffineList(newoffset, self.vals[newleft : end-self.offset], 
                              trackclass=self.trackclass, features=self.featureson(start,end))
        else:
            return AffineList(newoffset, self.vals[newleft:], 
                              trackclass=self.trackclass, features=self.featureson(start,end))
    def narrowto(self, i=None, j=None):
        if isinstance(i,HalfOpenInterval):
            j = i.right
            i = i.left
        if i==None:
            i = self.offset
        if j==None:
            j = self.offset + len(self.vals)
        return self[i:j] << i
    def __rshift__(self, i):
        if len(self) == 0: # Handle empty lists
            return self
        n = AffineList(offset=self.offset+i, vals=self.vals, trackclass=self.trackclass, features=[])
        s = n.support()
        for f in self.features:
            newf = Feature(f.name,
                           f.pos.left+i if f.pos.left!=None else None,
                           f.pos.right+i if f.pos.right!=None else None,
                           f.red,f.green,f.blue,f.alpha)
            n.features.append(newf)
        return n
    def __lshift__(self, i):
        return self >> (-1*i)
    def support(self):
        """Return the HalfOpenInterval containing the support of this list.

        For example, ``AffineList(offset=1, vals=[1,2]).support()`` is
        ``ProperInterval(1,3)``.
        """
        return ProperInterval(self.offset, self.offset + len(self.vals))
    def iter(self, start=None, end=None):
        """Return an iterator over the elements in the support of this list."""
        return it.imap(lambda (a,b): b, self.itercoords(start=start, end=end))
    def __iter__(self):
        return self.iter()
    def itercoords(self, start=None, end=None):
        """Return an iterator over (coordinate,item) pairs in the support of this list.

        You can specify *start* and *end* in coordinates to return
        some other range. Any items returns outside of the support are
        denoted ``None``.
        """
        if start is None:
            start = self.offset
        if end is None:
            end = self.offset + len(self.vals)
        for i in range(start, end):
            yield (i,self[i])
    def __repr__(self):
        return 'AffineList(offset=%d, vals=%s, trackclass="%s", features=%s)' % (self.offset, repr(self.vals), self.trackclass, repr(self.features))
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
        if start is None:
            start = self.support().left
        if end is None:
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
        return self.offset == other.offset and self.vals == other.vals and \
            self.trackclass == other.trackclass and \
            self.features == other.features



class Assembly(OrderedDict):
    """Class representing an assembly of sequences.

    ``Assembly`` is an extension of an ordered dictionary. All its
    values should be ``AffineList`` objects. It provides numerous
    methods to make working with such collections simple. It also has
    a slot ``metadata`` to store information about the assembly. The
    ``metadata`` is properly propogated through all operations on
    ``Assembly``.
    """
    def __init__(self, items=[], metadata={}, features=[]):
        OrderedDict.__init__(self, items)
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
        if len(self) == 0:
            return EmptyInterval()
        v = closure(*[v.support() for v in self.itervalues()])
        for k in keys:
            v = v.intersection(self[k].support())
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
        if start is None:
            start = whole.left
        if end is None:
            end = whole.right
        for i in range(start,end):
            yield (i,OrderedDict([(k,v[i]) for k,v in self.iteritems()]))
    def subset(self, start=0, end=None):
        """Return an Assembly of a subset of columns.

        If *start* and *end* are omitted, returns the Assembly itself.
        Otherwise, returns an Assembly with its origin at *start* and
        with all the columns out to *end*.
        """
        if isinstance(start, HalfOpenInterval):
            end = start.right
            start = start.left
        if end is None:
            end = self.support().right
        return Assembly([(k, v.narrowto(start,end)) for k,v in self.iteritems()], metadata=self.metadata)
    def narrowto(self, *keys):
        """Return an Assembly subset to the support of *keys*.

        *keys* is specified in the same way as for the ``support`` method.
        """
        return self.subset(self.support(*keys))
    def width(self, *keys):
        """Return the width of the support of *keys* in the Assembly.

        If *keys* is empty, then the width of the whole assembly.
        *keys* is specified as for the ``support`` method.
        """
        s = self.support(*keys)
        return len(s)
    def coordinates(self):
        """Return an AffineList of the coordinates in the Assembly's support."""
        h = self.support()
        return range(h.left, h.right)
        

def as_assembly(dct):
    if '__Assembly' in dct:
        return Assembly(dct['tracks'], metadata=dct['metadata'], features=dct['features'])
    elif '__AffineList' in dct:
        return AffineList(offset=dct['offset'], vals=dct['vals'], features=dct['features'],
                          trackclass=dct['trackclass'])
    elif '__Feature' in dct:
        return Feature(dct['name'], dct['left'], dct['right'], dct['red'], dct['green'],
                       dct['blue'], dct['alpha'])
    else:
        return dct

class AssemblyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, AffineList):
            return {'__AffineList': True, 'offset': obj.offset, 'vals': obj.vals,
                    'trackclass': obj.trackclass, 'features': obj.features}
        elif isinstance(obj, Assembly):
            return {'__Assembly': True, 'metadata': obj.metadata, 
                    'tracks': [(k,v) for k,v in obj.iteritems()],
                    'features': obj.features}
        elif isinstance(obj, Feature):
            return {'__Feature': True, 'name': obj.name, 'left': obj.pos.left,
                    'right': obj.pos.right, 'red': obj.red, 'green': obj.green,
                    'blue': obj.blue, 'alpha': obj.alpha}
        else:
            return json.JSONEncoder.default(self, obj)
            
def serialize(obj, filename):
    """Dump *obj* to *filename* as bz2 compressed JSON."""
    try:
        out = bz2.BZ2File(filename, 'w')
        json.dump(obj, out, cls=AssemblyEncoder)
    finally:
        out.close()


def deserialize(filename):
    """Load an object from a bz2 compressed JSON file *filename*."""
    try:
        input = bz2.BZ2File(filename, 'r')
        return json.load(input, object_hook=as_assembly)
    finally:
        input.close()
    
@templet.stringfunction
def renderinteger(coord, val):
    """<span>$val</span>"""

def base_color(base):
    base_coloring = {'A': 'green', 'C': 'blue', 'T': 'red', 
                     'G': 'black', 'U': 'red', 'X': 'black'}
    try:
        return base_coloring[base]
    except KeyError:
        return 'yellow'
   

@templet.stringfunction
def rendernucleotide(coord, val):
    """<span style="color: ${base_color(val)};">$val</span>"""

def path(coords, stroke="black", strokeWidth="0.03", fill="none"):
    d = "M%0.3f,%0.3f" % coords[0] + ''.join("L%0.3f,%0.3f" % c for c in coords[1:])
    return """<path stroke="%s" stroke-width="%s" fill="%s" d="%s" />""" % (stroke, strokeWidth, fill, d)

def rendersvg(coord, val):
    @templet.stringfunction
    def _rendersvg(coord, val):
        """<div class="svg-container">
  <svg preserveAspectRatio="none" viewbox="0 -0.05 1 1.05" version="1.1">
    ${[path(v, stroke=base_color(k)) for k,v in val.iteritems()]}
  </svg></div>"""
    
    if val != None:
        return _rendersvg(coord, val)

renderfun = defaultdict(lambda: rendertext,
                        [('nucleotide', rendernucleotide),
                         ('coordinate', renderinteger),
                         ('integer', renderinteger),
                         ('svg', rendersvg)])


@templet.stringfunction
def renderbaseitem(coord, val, features, trackclass):
    """<div class="${trackclass or ""} ${val is None and "empty" or ""}">
  ${val is None and "&nbsp;" or renderfun[trackclass](coord,val)}
  ${[f.render() for f in features if coord in f]}
</div>"""


@templet.stringfunction
def rendertext(coord,val):
    """$val"""

@templet.stringfunction
def rendercolumn(assembly, i):
    """<div>
      ${renderbaseitem(i, i, assembly.features, 'coordinate')}
      ${[renderbaseitem(i, v[i], v.features + assembly.features, v.trackclass)
         for v in assembly.itervalues()]}
    </div>"""


@templet.stringfunction
def renderassembly(assembly):
        """
<div class="assembly">
  <div class="label-column">
    <div class="label"><span>Position</span></div>
    ${['<div class="label %s"><span>%s</span></div>' % (v.trackclass, k)
       for k,v in assembly.iteritems()]}
  </div>
  <div class="scrolling-container">
    ${[rendercolumn(assembly, i) for i in assembly.coordinates()]}
  </div>
</div>"""


def tracealong(target, template, targetgap=None, templategap='-'):
    """Given a list *target*, string it along *template*, inserting gaps.

    *target* is assumed to have no gaps.
    """
    result = AffineList(template.offset, [])
    i = template.offset
    j = 0
    while i < template.support().right and j < len(target):
        if template[i] == templategap:
            i += 1
            result.append(targetgap)
        else:
            result.append(target[j])
            i += 1
            j += 1
    if j < len(target):
        result.extend(target[j:])
    return result

def alzipinterval(interval, *als):
    """Zip AffineLists *als* over *interval*.

    *als* should be AffineLists, and *interval* a HalfOpenInterval.
    """
    result = AffineList(interval.left, [])
    for i in range(interval.left, interval.right):
        result.append(tuple(a[i] for a in als))
    return result

def alzipnarrow(*als):
    """Zip *als* over the intersection of their supports."""
    interval = intersection(*[x.support() for x in als])
    return alzipinterval(interval, *als)

def alzipsupport(*als):
    """Zip *als* over the union of their supports, with gaps filled by ``None``."""
    interval = support(*als)
    return alzipinterval(interval, *als)


def almap(f, xs, start=None, end=None):
    print start,end
    if start is None:
        start = xs.support().left
    if end is None:
        end = xs.support().right
    return AffineList(start, [f(i,x) for i,x in xs.itercoords(start=start,end=end)])

    
css = """
* { margin: 0; padding: 0; }

.scrolling-container { position: relative; width: 100%; max-width: 100%; }

.label-column { float: left; max-width: 10em; overflow: hidden; white-space: nowrap; border-right: 0.2em solid black; }
.label-column div { display: block; font-family: Optima, Myriad, sans-serif; vertical-align: middle; color: #fff; border-top: 0.01em solid #eee; background-color: #111; padding-right: 0.1em; padding-left: 0.2em; padding-top: 0.2em; padding-bottom: 0.2em; height: 0.59em; text-align: right; }
div.label-column div span { font-size: 0.6em; }
div.label-column div:first-child { border-top: none; }
div.label-column div.svg { height: 3.6em !important; }
div.label-column div.svg span { height: 6em !important; vertical-align: middle; line-height: 6em; }

div.scrolling-container div { display: inline-block; width: 1.9em; vertical-align: top; text-align: center; }
div.scrolling-container div div { display: block; position: relative; }
div.scrolling-container div div div.feature { position: absolute; top: 0; bottom: 0; left: 0; right: 0; z-index: +2; }

@media print { 
  * { font-size: 10pt; }
  div.scrolling-container > div > div:last-child { margin-bottom: 10pt; }
  div.scrolling-container div:nth-of-type(odd) div { background-color: #f5f5f5; }
  div.scrolling-container div:nth-of-type(even) div { background-color: #fff; }
  div.scrolling-container div:nth-of-type(odd) div div svg { background-color: #f5f5f5; }
  div.scrolling-container div:nth-of-type(even) div div svg { background-color: #fff; }
}

@media screen { 
  .scrolling-container { overflow-x: scroll; overflow-y: hidden; white-space: nowrap; } 
  div.scrolling-container div:nth-of-type(odd) div { background-color: #eee; }
  div.scrolling-container div:nth-of-type(odd) div.empty { background-color: #aaa; }
  div.scrolling-container div:nth-of-type(even) div { background-color: #fff; }
  div.scrolling-container div:nth-of-type(even) div.empty { background-color: #bbb; }
  div.scrolling-container div:nth-of-type(odd) div div svg { background-color: #eee; }
  div.scrolling-container div:nth-of-type(even) div div svg { background-color: #fff; }
}


div.scrolling-container div div.svg { height: 4em !important; width: 1.9em; padding: 0; }
div.scrolling-container div div.svg div.svg-container { width: 100%; height: 100%;  }
div.scrolling-container div div.integer span { font-size: 70%; color: #666; line-height: 1.43; vertical-align: bottom; }
div.scrolling-container div div.coordinate span { font-weight: bold; font-size: 70%; line-height: 1.43; vertical-align: bottom; }
"""
