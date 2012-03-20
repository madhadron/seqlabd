"""
fasta.py - Module to run and parse FASTA alignment

This module only binds the ssearch36 program, which does pairwise,
global alignment with Smith-Waterman.
"""
import re
import os
import shutil
import tempfile
import subprocess
import contextlib
import Bio.SeqIO
import Bio.Seq

@contextlib.contextmanager
def as_fasta(seq, tmpdir=None, label='sequence'):
    """Create a temporary FASTA files containing the sequence *seq*.

    Many external programs insist on a file, not being fed from stdin.
    as_fasta takes a string, writes it to a temporary file under the
    label *label*, returns that file's name, then deletes the file at
    the end of the with block.
    """
    (db_fd, db_name) = tempfile.mkstemp(text=True, dir=tmpdir)
    db_handle = os.fdopen(db_fd, 'w')
    seqrecord = Bio.SeqIO.SeqRecord(id=label, seq=Bio.Seq.Seq(seq))
    Bio.SeqIO.write([seqrecord], db_handle, 'fasta')
    db_handle.close()
    try:
        yield db_name
    finally:
        os.unlink(db_name)

def ssearch36(seq1, seq2, ssearch36_path="ssearch36", tmpdir='/tmp'):
    if len(seq1) == 0:
        return (0, ''), (0, seq2)
    if len(seq2) == 0:
        return (0, seq1), (0, '')
    with as_fasta(seq1, tmpdir) as fasta1, as_fasta(seq2, tmpdir) as fasta2:
        command = ' '.join([ssearch36_path, '-a', '-d','1','-m','10', fasta1, fasta2])
        pipe = subprocess.Popen(str(command), shell=True, 
                                stdout=subprocess.PIPE)
        (alignment, _) = pipe.communicate()
        res = parse_ssearch36m10(alignment)
        return res


def spliton(f, xs):
    i = 0
    while not(f(xs[i])) and i < len(xs):
        i += 1
    return (xs[:i], xs[i:])


def parse_ssearch36m10(alignment):
    a = alignment.split('\n')
    a = spliton(lambda s: s.startswith('>>>'), a)[1]
    a = spliton(lambda s: s.startswith('>>><<<'), a)[0]
    seqsect, parsect = spliton(lambda s: s.startswith('; al_cons:'), a)
    seqsect = filter(lambda s: not(s.startswith(';')), seqsect)[3:]
    seq1, seqsect = spliton(lambda s: s.startswith('>'), seqsect)
    seq1 = ''.join(seq1)
    seq2 = ''.join(seqsect[1:])
    par = ''.join(parsect[1:])
    gaps, seq1 = spliton(lambda s: s!='-', seq1)
    offset1 = len(gaps)
    gaps, seq2 = spliton(lambda s: s!='-', seq2)
    offset2 = len(gaps)
    return ((offset1,seq1), (offset2,seq2))
    


            

