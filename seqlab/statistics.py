import assembly
import itertools
import contig

def _onboth(f):
    def wrapper(asm, key1, key2):
        interval = asm.support(key1, key2)    
        z = assembly.alzipinterval(interval, asm[key1], asm[key2])
        return f(z)
    wrapper.__doc__ = f.__doc__
    return wrapper

def _onfirst(f):
    def wrapper(asm, key1, key2):
        z = asm[key1]
        return f(z)
    wrapper.__doc__ = f.__doc__
    return wrapper

def _onsecond(f):
    def wrapper(asm, key1, key2):
        z = asm[key2]
        return f(z)
    wrapper.__doc__ = f.__doc__
    return wrapper

@_onboth
def identities(xs):
    """Number of exact matches between bases."""
    return len([(x,y) for (x,y) in xs if x==y])

def _base_inclusion(x, y):
    if x == '-' or y == '-':
        return False
    else:
        kx = contig.pacui[x]
        ky = contig.pacui[y]
        return kx.issubset(ky) or ky.issubset(kx)

@_onboth
def compatibles(xs):
    """The number of compatible bases (A and N, for example)."""
    return len([1 for x,y in xs if _base_inclusion(x, y)])

@_onboth
def bases(xs):
    """The number of bases in the overlap (so A vs - is counted, but - vs - is not)"""
    return len([(x,y) for x,y in xs if x != '-' or y != '-'])

@_onfirst
def bases1(xs):
    """The number of bases (not gaps) in the first sequence."""
    return len([x for x in xs if x != '-'])

@_onsecond
def bases2(xs):
    """Count the number of bases (not gaps) in the second sequence."""
    return len([x for x in xs if x != '-'])

@_onboth
def homopolymers(xs):
    """The number of homopolymers in the overlap of the reads (AA vs CC is one, but AA vs CT is 2)."""
    return len(list(itertools.groupby([(x,y) for x,y in xs if x != '-' or y != '-'])))

@_onfirst
def homopolymers1(xs):
    """The number of homopolymers in the first sequence."""
    return len(list(itertools.groupby([x for x in xs if x != '-'])))

@_onsecond
def homopolymers2(xs):
    """The number of homopolymers in the second sequence."""
    return len(list(itertools.groupby(xs)))

@_onboth
def conflicts(xs):
    """Positions where IUPAC characters are incompatible (ignoring indels)."""
    return len([(x,y) for (x,y) in xs if not _base_inclusion(x,y) and x != '-' and y != '-'])

@_onboth
def mismatches(xs):
    """Positions where bases are not an exact match (ignoring indels)."""
    return len([(x,y) for (x,y) in xs if x != y and x != '-' and y != '-'])

@_onboth
def indels(xs):
    """Positions where there is a gap in exactly one of the sequences."""
    return len([(x,y) for (x,y) in xs if (x == '-' or y == '-') and x != y])

@_onboth
def insertions1(xs):
    """Positions where there are gaps in the second sequence only."""
    return len([(x,y) for (x,y) in xs if x != '-' and y == '-'])

@_onboth
def insertions2(xs):
    """Positions where there are gaps in the first sequence only."""
    return len([(x,y) for (x,y) in xs if x =='-' and y !='-'])

@_onboth
def ambiguities(xs):
    """Number of positions where there is an IUPAC ambiguity code in at least one position (will count gaps in the opposite strand)"""
    return len([1 for x,y in xs if x not in "ACTG-" or y not in "ACTG-"])

@_onfirst
def ambiguities1(xs):
    """Number of positions in first reads which are IUPAC ambiguity codes."""
    return len([1 for x in xs if x not in "ACTG-"])

@_onsecond
def ambiguities2(xs):
    """Number of positions in second read which are IUPAC ambiguity codes."""
    return len([1 for x in xs if x not in "ACTG-"])

def fracoverlap(asm, key1, key2):
    """Length difference divided by mean length of the two sequences."""
    n1 = asm[key1].width()
    n2 = asm[key2].width()
    x = asm.support(key1, key2).width()
    return 2*x / float(n1+n2)

@_onboth
def overlap(xs):
    """Number of bases overlapping in the alignment (including double gaps)."""
    return len(xs)

def lengthdiff(asm, key1, key2):
    """Length of first sequence - length of second sequence."""
    return asm[key1].width() - asm[key2].width()

