import numpy
from collections import namedtuple

def base_color(base):
    base_coloring = {'A': 'green', 'C': 'blue', 'T': 'red', 
                     'G': 'black', 'U': 'red', 'X': 'black'}
    try:
        return base_coloring[base]
    except KeyError:
        return 'yellow'

class Traces(list, object):
    css_class = 'Traces'
    def __comp__(self):
        return Traces([{'A': d['T'], 'C': d['G'], 'T': d['A'], 'G': d['C']}
                       for d in self])
    def __rev__(self):
        return Traces([{'A': rev_entry(d['A']), 
                        'T': rev_entry(d['T']),
                        'C': rev_entry(d['C']),
                        'G': rev_entry(d['G'])}
                       for d in self[::-1]])
    def __render__(self, pos):
        entry = self[pos]
        paths = ''
        for b in 'ACTG':
            paths += path(M(entry[b][0]) + \
                              ''.join([L(x) for x in entry[b][1:]]),
                          stroke=base_color(b))
        return div(classes=['track-entry','Traces'],
                   body=div(classes='svg-container',
                            body=unit_svg(paths)))
    gap = {'A': numpy.array([(0.5,0)]), 'C': numpy.array([(0.5,0)]),
           'T': numpy.array([(0.5,0)]), 'G': numpy.array([(0.5,0)])}


def rev_entry(d):
    return [(1-x,y) for x,y in d[::-1]]


def cutoff(a, n_hinges=6.1):
    m = numpy.median(numpy.log(a+1))
    h = sorted(numpy.log(a+1))[int(0.75*len(a))]
    d = h-m
    c = numpy.exp(m + n_hinges*d) - 1
    return c

def sparsify(xs, ys):
    new_points = [(xs[0], ys[0])]
    i = 0
    while i < len(ys)-1:
        Lx, Ly, Rx, Ry = xs[i], ys[i], xs[i+1], ys[i+1]
        skipped = []
        while i < len(ys)-2 and len(skipped) < 10:
            nextx, nexty = xs[i+2], ys[i+2]
            if all([close_enough(Lx,Ly, nextx,nexty, px,py)
                    for px,py in skipped + [(Rx,Ry)]]):
                skipped += [(Rx,Ry)]
                Rx,Ry = nextx,nexty
                i += 1
            else:
                break
        new_points.append((Rx,Ry))
        i += 1
    return new_points

def test_sparsify():
    xs = range(14)
    ys = numpy.arange(14)/5.0
    assert sparsify(xs,ys) == [(0,0), (11,11/5.0), (13,13/5.0)]
    xs = range(4)
    ys = numpy.arange(4)
    assert sparsify(xs,ys) == [(0,0), (3,3)]


def traces(A, C, T, G, centers):
    A = numpy.array(A).astype(numpy.float)
    C = numpy.array(C).astype(numpy.float)
    G = numpy.array(G).astype(numpy.float)
    T = numpy.array(T).astype(numpy.float)
    centers = numpy.array(centers).astype(numpy.integer)
    assert len(A) == len(C) == len(T) == len(G)
    assert all(centers >= 0) and all(centers < len(A))
    assert all(sorted(centers) == centers)
    _limits = [int(numpy.ceil((centers[i]+centers[i-1])/2.0)) 
               for i in range(1, len(centers))]
    limits = zip([0] + _limits, [x+1 for x in _limits] + [len(A)])
    all_traces = numpy.concatenate([A,C,T,G])
    maxima = [max(numpy.concatenate([A[i:j],C[i:j],T[i:j],G[i:j]]))
              for i,j in limits]
    m = min(2*numpy.median(maxima), max(maxima))
    t = Traces()
    for l,r in limits:
        xs = numpy.arange(0,r-l) / float(r-l-1)
        assert len(xs) == len(A[l:r]) == len(C[l:r]) \
            == len(T[l:r]) == len(G[l:r])
        t.append({'A': sparsify(xs, 1-A[l:r]/m), 
                  'C': sparsify(xs, 1-C[l:r]/m),
                  'T': sparsify(xs, 1-T[l:r]/m),
                  'G': sparsify(xs, 1-G[l:r]/m)}), 
    return t

def close_enough(Lx,Ly, Rx,Ry, px,py):
    """Is px,py close enough to the line given by L and R to be approximated by it?"""
    # Find the vertical distance of px,py from the line through Lx,Ly
    # and Rx,Ry.  px,py is defined to be "close enough" if it no more
    # than a fraction alpha of the average height of the line away
    # from it.  The value of alpha here was selected by looking at the
    # output by eye and taking the highest value that left the curves
    # still looking reasonably smooth.
    alpha = 0.005
    return abs(py - ((Ry-Ly)/float(Rx-Lx))*(px-Lx) - Ly) < alpha * (Ly + Ry)/2.0

    
def test_traces():
    centers = [2,4,7]
    ys = range(14)
    t = traces(ys,ys,ys,ys,centers)
    for x in t:
        assert sorted(list(x.keys())) == ['A','C','G','T']
    assert len(t[0]['A']) == 2
    assert len(t[0]['C']) == 2
    assert len(t[1]['A']) == 2



class Sequence(str, object):
    css_class = 'Sequence'
    def __comp__(self):
        return Sequence(self. \
                            replace('A','t'). \
                            replace('T','a'). \
                            replace('C','g'). \
                            replace('G','c').upper())
    def __rev__(self):
        return Sequence(self[::-1])
    def __render__(self, pos):
        return div(classes=['track-entry','Sequence'],
                   style="color: %s" % base_color(self[pos]),
                   body=self[pos])
    gap = '-'
    def __isgap__(self, other):
        return other == '-' or other == '.'
    def insert(self, pos, item):
        return Sequence(self[:pos] + item + self[pos:])

def sequence(s):
    return Sequence(s)

class Numeric(list, object):
    css_class = 'Numeric'
    def __rev__(self):
        return numeric(self[::-1])
    def __comp__(self):
        return self
    def __render__(self, pos):
        return div(classes=['track-entry','Numeric'],
                   body=str(self[pos]))
    gap = None

def numeric(vals):
    return Numeric(vals)

TrackEntry = namedtuple('TrackEntry', ['name', 'offset', 'track'])

class TrackSet(list, object):
    def __render__(self):
        labels = div(classes='label', body=span('Position'))
        for t in self:
            if isinstance(t.track, Traces):
                labels += div(classes='chromatogram-label',
                              body=span(t.name))
            else:
                labels += div(classes='label',
                              body=span(t.name))
        maxlen = max([len(x.track)+x.offset for x in self])
        tracks = ""
        for i in range(len(self)):
            colbody = div(classes=['track-entry','integer'], body=str(i))
            for t in self:
                L = len(t.track)
                c = t.track.css_class
                if i < t.offset:
                    colbody += div(classes=['track-entry','empty',c])
                elif i < t.offset + L:
                    colbody += render(t.track, pos=i-t.offset)
                else:
                    colbody += div(classes=['track-entry','empty',c])
            tracks += div(classes=['track-column'], body=colbody)

        return div(classes='trackset',
                   body=div(classes='label-column', body=labels) + \
                       div(classes='scrolling-container',
                           body=tracks))
    def __len__(self):
        return max([len(t.track)+t.offset for t in self])


def rev(s):
    return s.__rev__()

def comp(s):
    return s.__comp__()

def revcomp(s):
    return rev(comp(s))

def render(s, *args, **kwargs):
    assert isinstance(s, TrackSet) or isinstance(s, Sequence) or \
        isinstance(s, Numeric) or isinstance(s, Traces)
    return s.__render__(*args, **kwargs)


def regap(template, target):
    result = target
    gaps = [i for i,t in enumerate(template)
            if t == template.gap]
    for i in gaps:
        a = result.insert(i, result.gap)
        if a != None:
            result = a
    return result



### XML
def tag(name):
    def f(body="", classes=[], style=""):
        if not(isinstance(classes, list)):
            classes = [classes]
        return ("""<%s class="%s" style="%s">""" % (name,
                                                    ' '.join(classes),
                                                    style)) + \
            body + \
            ("""</%s>""" % (name,))
    return f

div = tag('div')
span = tag('span')

def unit_svg(body=""):
    return """<svg preserveAspectRatio="none" viewbox="0 -0.05 1 1.05" version="1.1">""" + \
        body + """</svg>"""

def M((x,y)):
    return "M%0.3f,%0.3f" % (x,y)

def L((x,y)):
    return "L%0.3f,%0.3f" % (x,y)

def path(d, stroke="black", strokeWidth="0.03", fill="none"):
    dstr = ''.join(d)
    return """<path stroke="%s" stroke-width="%s" fill="%s" d="%s" />""" % \
        (stroke, strokeWidth, fill, dstr)
        
def standalone(tracksets):
    if isinstance(tracksets, TrackSet):
        tracksets = [tracksets]
    xml = """<html><head>\n"""
    xml += """<style>\n""" + stylesheet + "</style>\n"
    xml += """</head><body>"""
    for title,t in tracksets:
        xml += ("<h1>%s</h1>\n" % title) + render(t)
    xml += """</body></html>"""
    return xml


stylesheet = """
* {
    margin: 0;
    padding: 0;
}

@media print { * { font-size: 10pt; } }

.scrolling-container {
    position: relative;
}

@media screen { .scrolling-container { overflow: scroll; white-space: nowrap; } }

.label-column {
    float: left;
    max-width: 10em;
    overflow: hidden;
    white-space: nowrap;
    border-right: 0.2em solid black;
}


.label-column div {
    display: block;
    font-family: Optima, Myriad, sans-serif;
    vertical-align: middle;
    color: white;
    border-top: 0.01em solid #eee;
    background-color: #111;
    background-image: url('concrete_wall.png');
    padding-right: 0.1em;
    padding-left: 0.2em;
    padding-top: 0.2em;
    padding-bottom: 0.2em;
    height: 0.59em;
    text-align: right;
}

.label-column div span {
    font-size: 0.6em;
}

.label-column div:first-child {
    border-top: none;
}

.chromatogram-label {
    height: 3.6em !important;
}

.chromatogram-label span {
    height: 6em !important;
    vertical-align: middle;
    line-height: 6em;
}

.trackset {
    width: 100%;
    max-width: 100%;
}

.track-column {
    display: inline-block;
    width: 1.3em;
    vertical-align: top;
}

@media print { .track-column {     
                   padding-bottom: 0.5em;
                   border-bottom: 0.1em double #000;
                   margin-bottom: 0.5em; }}


.track-entry {
    display: block;
    padding-left: 0.3em;
    padding-right: 0.3em;
    text-align: center;
    height: 1.1em;
}


.track .track-entry:nth-of-type(odd) {
    background-color: #eee;
}
.track .track-entry:nth-of-type(even) {
    background-color: #fff;
}

.track .empty:nth-of-type(odd) {
    background-color: #ccc;
}
.track .empty:nth-of-type(even) {
    background-color: #ddd;
}

.Traces {
    height: 4em !important;
    padding: 0;
}

.track-entry > .svg-container {
    width: 100%;
    height: 100%;
    font-size: 0;
}

.integer {
    font-size: 70%;
    color: #666;
    line-height: 143%;
}

.track-name {
    position: fixed;
    vertical-align: middle;
    left: 0;
    text-align: right;
    white-space: wrap;
    overflow: wrap;
}

"""
