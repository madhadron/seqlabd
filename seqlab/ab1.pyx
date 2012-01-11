from libc.stdio cimport fopen, fclose, fseek, fread, FILE, SEEK_SET, ftell

import tracks

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
            if data_index < 8:
                pass
            else:
                data.append(fread_short_array_at(p, d.numelements, d.dataoffset))
            data_index += 1

    confidence_track = tracks.numeric(confidences)
    sequence_track = tracks.sequence(bases)

    traces_track = tracks.traces(A=data[base_order['A']],
                                 C=data[base_order['C']],
                                 T=data[base_order['T']],
                                 G=data[base_order['G']],
                                 centers=centers)
    val = {'sequence': sequence_track,
           'confidences': confidence_track,
           'traces': traces_track}
    return val
