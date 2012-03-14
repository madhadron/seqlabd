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
import ab1

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
    def meta(self, key, default=None):
        return self.metadata.get(key, default)
    def setmeta(self, key, value):
        self.metadata[key] = value
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
    def overlaps(self, other):
        return intersection(self.support(), other.support()).isproper()
    def isinfinite(self):
        return not(self.isfinite())
    def __lshift__(self, n):
        return self >> -n
    def toorigin(self):
        if self.isproper():
            return self << self.left()
        else:
            return self
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
    def serialize(self, filename=None):
        if filename is None:
            return json.dumps(self, cls=AffineEncoder)
        else:
            with bz2.BZ2File(filename, 'w') as out:
                json.dump(self, out, cls=AffineEncoder)





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
        newmetadata = self.metadata.copy()
        if 'features' in newmetadata:
            newmetadata['features'] = [f >> n for f in self.metadata['features']]
        return ProperInterval(self._left+n, self._right+n,
                              **newmetadata)
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


def interval(left, right, **metadata):
    if right <= left:
        return EmptyInterval(**metadata)
    else:
        return ProperInterval(left, right, **metadata)


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

class AffineList(Affine):
    def appendfeature(self, feature):
        if 'features' not in self.metadata:
            self.metadata['features'] = []
        self.metadata['features'].append(feature)

class EmptyList(AffineList):
    """Object representing an empty AffineList."""
    def __getslice__(self, left, right):
        return self
    def __getitem__(self, i):
        if isinstance(i, int) or i is None or \
                i == posinf or i == neginf:
            return None
        else:
            return self
    

class ProperList(AffineList):
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
    def __init__(self, offset, values, **kwargs):
        if len(values) == 0:
            raise ValueError("Cannot create a ProperList with no contents.")
        self.metadata = kwargs
        self.offset = offset
        self.values = list(values)
    def isempty(self):
        return False
    def left(self):
        return self.offset
    def right(self):
        return self.offset + len(self.values)
    def strip(self):
        return AffineList(self.offset, self.values)
    def __rshift__(self, n):
        newmetadata = self.metadata.copy()
        if 'features' in newmetadata:
            newmetadata['features'] = [f >> n for f in self.metadata['features']]
        return ProperList(self.offset+n, self.values, **newmetadata)
    def __getitem__(self, i):
        if isinstance(i, int):
            if i < self.left():
                return None
            elif i >= self.right():
                return None
            else:
                return self.values[i-self.offset]
        elif isinstance(i, slice):
            return self.__getitem__(i.start, i.stop)
        elif isinstance(i, EmptyInterval):
            return EmptyList(**self.metadata)
        elif isinstance(i, ProperInterval):
            return self.__getslice__(i.left(), i.right())
    def __getslice__(self, left, right):
        assert left <= right
        if left == right:
            return EmptyList(**self.metadata)
        offset = max(self.left(), left)
        i = offset - self.left()
        j = min(self.right(), right) - self.offset
        body = self.values[i:j]
        if len(body) == 0:
            return EmptyList(**self.metadata)
        else:
            return ProperList(offset, body, **self.metadata)
    def featureson(self, left=None, right=None):
        if 'features' not in self.metadata:
            return []
        else:
            # Munge the arguments into something useful
            if right is None and isinstance(left, int) or left == neginf:
                pos = ProperInterval(left, left+1)
            elif right is None and isinstance(left, Interval):
                pos = left
            elif right > left:
                pos = ProperInterval(left, right)
            else:
                pos = EmptyInterval()
        return [f for f in self.metadata['features'] if f.overlaps(pos)]
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
            end = self.offset + len(self.values)
        for i in range(start, end):
            yield (i,self[i])
    def __repr__(self):
        return 'ProperList(offset=%d, values=%s' % (self.offset, repr(self.values)) + \
            "".join(", %s=%s" % (k, repr(v)) for k,v in self.metadata.iteritems()) + ")"
    def __len__(self):
        return len(self.values)
    def append(self, x):
        """Append *x* as an item to the end of this list."""
        self.values.append(x)
        return self
    def insert(self, i, x):
        """Insert *x* at coordinate *i*.

        The list is properly extended with ``None``s if *i* is outside
        the list's support.
        """
        if i in self.support():
            self.values.insert(i-self.offset, x)
        elif i < self.offset:
            self.values = [x] + [None]*(self.offset-i-1) + self.values
            self.offset = i
        else: # i off to right of support
            self.values = self.values + [None]*(i - (self.offset+len(self.values))) + [x]
        return self
    def extend(self, vals):
        """Append all items in *vals* to the end of the list."""
        self.values.extend(vals)
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
            start = self.left()
        if end is None:
            end = self.right()
        
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
            self.values[i-self.offset] = x
        elif i < self.offset:
            self.values = [x] + [None]*(self.offset-i-1) + self.values
            self.offset = i
        else: # i off to right of support
            self.values = self.values + [None]*(i - (self.offset+len(self.values))) + [x]
        return x
    def __eq__(self, other):
        return self.offset == other.offset and self.values == other.values and \
            self.metadata == other.metadata

def aflist(offset, values, **metadata):
    if len(values) == 0:
        return EmptyList(**metadata)
    else:
        return ProperList(offset, values, **metadata)


class Assembly(OrderedDict, Affine):
    """Class representing an assembly of sequences.

    ``Assembly`` is an extension of an ordered dictionary. All its
    values should be ``AffineList`` objects. It provides numerous
    methods to make working with such collections simple. It also has
    a slot ``metadata`` to store information about the assembly. The
    ``metadata`` is properly propogated through all operations on
    ``Assembly``.
    """
    def __init__(self, items=[], **metadata):
        OrderedDict.__init__(self, items)
        self.metadata = metadata
    def isempty(self):
        return len(self) == 0
    def __rshift__(self, n):
        newmetadata = self.metadata.copy()
        if 'features' in newmetadata:
            newmetadata['features'] = [f >> n for f in self.metadata['features']]
        return Assembly(items=[(k, v >> n) for k,v in self.iteritems()], **newmetadata)
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
    def left(self):
        return self.support().left()
    def right(self):
        return self.support().right()
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
        if start is None:
            start = self.left()
        if end is None:
            end = self.right()
        for i in range(start,end):
            yield (i,OrderedDict([(k,v[i]) for k,v in self.iteritems()]))
    def subset(self, start=0, end=None):
        """Return an Assembly of a subset of columns.

        If *start* and *end* are omitted, returns the Assembly itself.
        Otherwise, returns an Assembly with its origin at *start* and
        with all the columns out to *end*.
        """
        if isinstance(start, Interval):
            end = start.right
            start = start.left
        if end is None:
            end = self.support().right
        return Assembly([(k, v[v.support()]) for k,v in self.iteritems()], **self.metadata)
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
        return s.width()
    def coordinates(self):
        """Return an AffineList of the coordinates in the Assembly's support."""
        return range(self.left(), self.right())
    def serialize(self, filename=None):
        d = dictunion({'__Assembly': True,
                       'items': [(k,v) for k,v in self.iteritems()]},
                      self.metadata)
        if filename is None:
            return json.dumps(d, cls=AffineEncoder)
        else:
            with bz2.BZ2File(filename, 'w') as out:
                json.dump(d, out, cls=AffineEncoder)


        

def affine_hooks(dct):
    classkeys = [k[2:] for k in dct if k.startswith('__')]
    if classkeys == []:
        return dct
    elif len(classkeys) > 1:
        raise ValueError("Found more than one class specifier in JSON")
    else:
        c = classkeys[0]
        s = c + '(' + ', '.join(['%s=%s' % (k,repr(v)) for k,v in dct.iteritems() if not(k.startswith('__'))]) + ")"
        return eval(s)

class AffineEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ProperInterval):
            v = {'left': obj.left(), 'right': obj.right()}
        elif isinstance(obj, ProperList):
            v = {'offset': obj.left(), 'values': obj.values}
        elif isinstance(obj, Affine):
            v = {}
        elif obj == neginf:
            return {'__NegInf': True}
        elif obj == posinf:
            return {'__PosInf': True}
        else:
            return json.JSONEncoder.default(self, obj)
        d = dictunion(v, {'__'+obj.__class__.__name__: True}, obj.metadata)
        return d

def deserializes(txt):
    return json.loads(txt, object_hook=affine_hooks)

def deserialize(filename):
    """Load an object from a bz2 compressed JSON file *filename*."""
    with bz2.BZ2File(filename, 'r') as input:
        return json.load(input, object_hook=affine_hooks)

    
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
def renderfeature(f):
    """<div class="feature" id="${f.meta('name','')}" style="background-color: rgba(${f.meta('red',0)}, ${f.meta('green',0)}, ${f.meta('blue',0)}, ${f.meta('alpha', 0)});"></div>"""

@templet.stringfunction
def renderbaseitem(coord, val, features, trackclass):
    """<div class="${trackclass or ""} ${val is None and "empty" or ""}">
  ${val is None and "&nbsp;" or renderfun[trackclass](coord,val)}
  ${[renderfeature(f) for f in features if coord in f]}
</div>"""


@templet.stringfunction
def rendertext(coord,val):
    """$val"""

@templet.stringfunction
def rendercolumn(assembly, i):
    """<div>
      ${renderbaseitem(i, i, assembly.meta('features',[]), 'coordinate')}
      ${[renderbaseitem(i, v[i], v.meta('features',[]) + assembly.meta('features',[]), v.meta('trackclass',''))
         for v in assembly.itervalues()]}
    </div>"""


@templet.stringfunction
def renderassembly(assembly):
        """
<div class="assembly">
  <style>${css}</style>
  <div class="label-column">
    <div class="label"><span>Position</span></div>
    ${['<div class="label %s"><span>%s</span></div>' % (v.metadata.get('trackclass',''), k)
       for k,v in assembly.iteritems()]}
  </div>
  <div class="scrolling-container">
    ${[rendercolumn(assembly, i) for i in assembly.coordinates()]}
  </div>
</div>"""

def ab1tohtml(ab1filename):
    r = ab1.read(ab1filename)
    a = Assembly([('traces', aflist(0, r['traces'], trackclass='svg')),
                  ('confidences', aflist(0, r['confidences'], trackclass='integer')),
                  ('bases', aflist(0, r['sequence'], trackclass='nucleotide'))])
    s = ""
    s += "<html><body>"
    s += renderassembly(a)
    s += "</body></html>"
    return s


def tracealong(target, template, targetgap=None, templategap='-'):
    """Given a list *target*, string it along *template*, inserting gaps.

    *target* is assumed to have no gaps.
    """
    if template.isempty():
        raise ValueError("Can't trace along an empty list.")
    result = []
    i = template.left()
    j = 0
    while i < template.right() and j < len(target):
        if template[i] == templategap:
            i += 1
            result.append(targetgap)
        else:
            result.append(target[j])
            i += 1
            j += 1
    if j < len(target):
        result.extend(target[j:])
    return ProperList(template.left(), result)

def alzipinterval(interval, *als):
    """Zip AffineLists *als* over *interval*.

    *als* should be AffineLists, and *interval* a HalfOpenInterval.
    """
    if interval.isempty():
        return EmptyList()
    offset = interval.left()
    body = []
    for i in range(interval.left(), interval.right()):
        body.append(tuple(a[i] for a in als))
    return ProperList(offset, body)

def alzipnarrow(*als):
    """Zip *als* over the intersection of their supports."""
    interval = intersection(*[x.support() for x in als])
    return alzipinterval(interval, *als)

def alzipsupport(*als):
    """Zip *als* over the union of their supports, with gaps filled by ``None``."""
    interval = support(*als)
    return alzipinterval(interval, *als)


def almap(f, xs, start=None, end=None):
    if start is None:
        start = xs.left()
    if end is None:
        end = xs.right()
    return ProperList(start, [f(i,x) for i,x in xs.itercoords(start=start,end=end)])

    
css = """
* { margin: 0; padding: 0; -webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; }

.scrolling-container { position: relative; width: auto; right: 0; max-width: 100%; }

.label-column { float: left; max-width: 10em; overflow: hidden; white-space: nowrap; border-right: 0.2em solid black; }
.label-column div { display: block; font-family: Optima, Myriad, sans-serif; vertical-align: middle; color: #fff; border-top: 0.01em solid #eee; background-color: #111; padding-right: 0.1em; padding-left: 0.2em; padding-top: 0.2em; padding-bottom: 0.2em; height: 1.2em; text-align: right; }
div.label-column div span { font-size: 0.6em; display: block; vertical-align: middle; }
div.label-column div:first-child { border-top: none; }
div.label-column div.svg { height: 4em !important; }
div.label-column div.svg span { height: 6em !important; line-height: 6em !important; }

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
