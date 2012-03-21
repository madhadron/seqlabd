# cython: profile=True
from libc.stdio cimport fopen, fclose, fseek, fread, FILE, SEEK_SET, ftell

import numpy
cimport numpy

cdef extern from "arpa/inet.h":
    int ntohl(int)
    short ntohs(short)

ctypedef struct DirEntry:
    char[4] name
    int number
    short elementtype
    short elementsize
    int numelements
    int datasize
    int dataoffset
    int datahandle

cdef short fread_short(FILE *p):
    cdef short s = 0
    fread(&s, 2, 1, p)
    host_s = ntohs(s)
    return host_s

cdef char fread_byte(FILE *p):
    cdef char c = 0
    fread(&c, 1, 1, p)
    return c

cdef numpy.ndarray fread_byte_array_at(FILE *p, int N, int offset):
    cdef long return_to = ftell(p)
    fseek(p, offset, SEEK_SET)
    cdef numpy.ndarray[numpy.int8_t, ndim=1] arr = numpy.zeros(N, dtype=numpy.byte)
    cdef int j
    for j in range(N):
        arr[j] = fread_byte(p)
    fseek(p, return_to, SEEK_SET)
    return arr

cdef numpy.ndarray fread_short_array_at(FILE *p, int N, int offset):
    cdef long return_to = ftell(p)
    fseek(p, offset, SEEK_SET)
    cdef numpy.ndarray[numpy.int16_t, ndim=1] arr = numpy.zeros(N, dtype=numpy.short)
    cdef int j
    for j in range(N):
        arr[j] = fread_short(p)
    fseek(p, return_to, SEEK_SET)
    return arr

cdef DirEntry fread_direntry(FILE *p):
    cdef DirEntry td
    fread(&td, sizeof(DirEntry), 1, p)
    td.number = ntohl(td.number)
    td.elementtype = ntohs(td.elementtype)
    td.elementsize = ntohs(td.elementsize)
    td.numelements = ntohl(td.numelements)
    td.datasize = ntohl(td.datasize)
    td.dataoffset = ntohl(td.dataoffset)
    td.datahandle = ntohl(td.datahandle)
    return td

def read(filename):
    tmp = filename.encode('UTF-8')
    cdef char* c_filename = tmp
    cdef FILE *p
    p = fopen(c_filename, "rb")
    if p == NULL:
        raise ValueError("Failed to open file %s" % filename)

    cdef char* magic_number = b'0000'
    fread(magic_number, 4, 1, p)
    if magic_number != b'ABIF':
        raise ValueError("Not a valid ABI file: bad magic number.")

    host_version = fread_short(p)
    if host_version < 100 or host_version > 199:
        raise ValueError("ABI file version not supported by this library.")

    td = fread_direntry(p)
    assert td.name[:4] == b'tdir'.encode()
    assert td.number == 1
    assert td.elementtype == 1023
    assert td.elementsize == 28
    
    # Find the entries for eight fields: FWO_ to give base order, the
    # last four DATA fields of 12, PBAS for basis, PLOC for ceners,
    # and PCON for confidences.
    
    fseek(p, td.dataoffset, SEEK_SET)
    entries = {}
    cdef short data_index = 0, pbas_index = 0, pcon_index = 0, ploc_index = 0
    cdef int i, j
    cdef char ctmp
    cdef long return_to
    cdef numpy.ndarray bases_array, confidences, centers
    cdef str bases
    data = []
    raw_data = []
    processed_data = []
    cdef int c, q
    for i in range(td.numelements):
        d = fread_direntry(p)
        name = d.name[:4]
        if name == b'PBAS':
            if pbas_index == 1: # We want the second entry, the BaseCaller's entry
                bases_array = fread_byte_array_at(p, d.numelements, d.dataoffset)
                bases = ''.join(chr(x) for x in bases_array)
            pbas_index += 1
        if name == b'PCON':
            if pcon_index == 1:
                confidences = fread_byte_array_at(p, d.numelements, d.dataoffset)
            pcon_index += 1
        if name == b'PLOC':
            if ploc_index == 1:
                centers = fread_short_array_at(p, d.numelements, d.dataoffset)
            ploc_index += 1
        if name == b'FWO_':
            base_order = []
            for q,sh in enumerate([24, 16, 8, 0]):
                c = 255 & (d.dataoffset >> sh)
                base_order.append((chr(c), q))
            base_order = dict(base_order)
        if name == b'DATA':
            if data_index < 4:
                raw_data.append(fread_short_array_at(p, d.numelements, d.dataoffset))
            elif data_index < 8:
                pass
            else:
                data.append(fread_short_array_at(p, d.numelements, d.dataoffset))
                processed_data.append(fread_short_array_at(p, d.numelements, d.dataoffset))
            data_index += 1

    # confidences and bases are numpy arrays
    traces = tracify(A=data[base_order['A']],
                     C=data[base_order['C']],
                     T=data[base_order['T']],
                     G=data[base_order['G']],
                     centers=centers)
    val = {'sequence': bases,
           'confidences': [int(x) for x in confidences],
           'traces': traces}
    return val

def tracify(A, C, T, G, centers):
    assert len(A) == len(C) 
    assert len(A) == len(T)
    assert len(A) == len(G)
    assert len(A) > 0
    assert len(centers) > 0
    assert all(centers >= 0) and all(centers < len(A)) and all(sorted(centers) == centers)
    # Left and right limits of each base
    _limits = [int(numpy.ceil((centers[i]+centers[i-1])/2.0))
               for i in range(1, len(centers))]
    limits = zip([0] + _limits, [x+1 for x in _limits] + [len(A)])

    maxima = numpy.array(sorted([max(numpy.concatenate([A[i:j],C[i:j],T[i:j],G[i:j]]))
                                 for i,j in limits]))
    rmax = cutoff(maxima)
    result = []
    for l,r in limits:
        xs = numpy.arange(0, r-l) / float(r-l-1)
        assert len(xs) == len(A[l:r]) == len(C[l:r]) \
            == len(T[l:r]) == len(G[l:r])
        result.append({'A': sparsify(xs, 1-A[l:r]/rmax), 
                       'C': sparsify(xs, 1-C[l:r]/rmax),
                       'T': sparsify(xs, 1-T[l:r]/rmax),
                       'G': sparsify(xs, 1-G[l:r]/rmax)})
    return result

cdef list sparsify(numpy.ndarray xs, numpy.ndarray ys):
    cdef double Lx, Ly, Rx, Ry, nextx, nexty
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


cdef bint close_enough(double Lx, double Ly, double Rx, double Ry, double px, double py):
    """Is px,py close enough to the line given by L and R to be approximated by it?"""
    # Find the vertical distance of px,py from the line through Lx,Ly
    # and Rx,Ry.  px,py is defined to be "close enough" if it no more
    # than a fraction alpha of the average height of the line away
    # from it.  The value of alpha here was selected by looking at the
    # output by eye and taking the highest value that left the curves
    # still looking reasonably smooth.
    cdef double alpha = 0.005
    return abs(py - ((Ry-Ly)/float(Rx-Lx))*(px-Lx) - Ly) < alpha * (Ly + Ry)/2.0




cdef double cutoff(numpy.ndarray xs):
    # Calculate the scaling factor, so that
    #     scaled = raw / rmax
    # Ideally 0.25 <= scaled <= 1, but that is not in general possible
    # with one degree of freedom. Instead, we will take the largest
    # rmax such that P(scaled < 0.25) = P(scaled > 1).
    # Assume xs is already sorted ascending.
    cdef double ratio = 1/8.0
    cdef double righti = -1
    cdef double rmax = xs[righti]
    cdef double lefti = 0
    while xs[lefti] < rmax*ratio:
        lefti += 1
    while lefti > -righti:
        righti -= 1
        rmax = xs[righti]
        while xs[lefti] > rmax*ratio:
            lefti -= 1
    return rmax

def psparsify(xs, ys):
    return sparsify(xs, ys)

def pcutoff(vals):
    return cutoff(vals)
    




    
