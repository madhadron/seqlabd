"""
fasta.py - Module to run and parse FASTA alignment

This module only binds the ssearch36 program, which does pairwise,
global alignment.
"""
import re
import os
import shutil
import tempfile
import subprocess
import contextlib
import Bio.SeqIO

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
    seqrecord = Bio.SeqIO.SeqRecord(id=label, seq=Bio.SeqIO.Seq(seq))
    Bio.SeqIO.write([seqrecord], db_handle, 'fasta')
    db_handle.close()
    try:
        yield db_name
    finally:
        os.unlink(db_name)

def fasta(seq1, seq2, ssearch36_path="ssearch36", tmpdir='/tmp'):
    with as_fasta(seq1, tmpdir) as fasta1, as_fasta(seq2, tmpdir) as fasta2:
        command = ' '.join([ssearch36_path, '-d','1','-m','3', fasta1, fasta2])
        pipe = subprocess.Popen(str(command), shell=True, 
                                stdout=subprocess.PIPE)
        (alignment, _) = pipe.communicate()
        res = parse_fasta(alignment, seq1, seq2)
        assert len(seq1) == len(res[0][1])
        assert len(seq2) == len(res[1][1])
        return res



def parse_fasta(alignment, origseq1, origseq2):
    lines = alignment.split('\n')
    l = lines.index('>sequen ..') + 1
    c = lines[l:].index('>sequen ..') + l
    r = lines[c:].index('') + c
    l1, r1 = l, c
    l2, r2 = c+1, r
    seq1 = ''.join(lines[l1:r1])
    spaces1, bases1 = re.match(r'( *)([A-Z-]+)', seq1).groups()
    offset1 = len(spaces1)

    seq2 = ''.join(lines[l2:r2])
    spaces2, bases2 = re.match(r'( *)([A-Z-]+)', seq2).groups()
    offset2 = len(spaces2)

    ungapped1 = bases1.replace('-','')
    if len(ungapped1) < len(origseq1):
        i = origseq1.find(ungapped1)
        assert i > -1
        bases1 = origseq1[:i] + bases1 + origseq1[i+len(ungapped1):]
        offset1 -= len(ungapped1[:i])

    ungapped2 = bases2.replace('-','')
    if len(ungapped2) < len(origseq2):
        i = origseq2.find(ungapped2)
        assert i > -1
        bases2 = origseq2[:i] + bases2 + origseq2[i+len(ungapped2):]
        offset2 -= len(origseq2[:i])

    if min(offset1,offset2) < 0:
        offset1 -= min(offset1,offset2)
        offset2 -= min(offset1,offset2)

    return ((offset1, bases1), (offset2, bases2))
        

def test_ssearch():
    s1 = 'CTCAGGATGAACGCTGGCGGCGTGCCTAATACATGCMAGTCGAGCGAACAGATAAGGAGCTTGCTCCTTTGACGTTAGCGGCGGACGGGTGAGTAACACGTGGGTAACCTACCTATAAGACTGGGACAACTTCGGGAAACCGGAGCTAATACCGGATAATATGTTGAACCGCATGGTTCAATAGTGAAAGATGGTTTTGCTATCACTTATAGATGGACCCGCGCCGTATTAGCTAGTTGGTGAGGTAACGGCTCACCAAGGCAACGATACGTAGCCGACCTGAGAGGGTGATCGGCCACACTGGAACTGAGACACGGTCCAGACTCCTACGGGAGGCAGCAGTAGGGAATCTTCCGCAATGGGCGAAAGCCTGACGGAGCAACGCCGCGTGAGTGATGAAGGTCTTAGGATCGTAAAACTCTGTTATTAGGGAAGAACAAACGTGTAAGTAACTGTGCACGTCTTGACGGTACCTAATCAGAAAGCCACGGCTAACTACG'
    s2 = 'GATGAACGCTGGCGGCGTGCCTAATACATGCAAGTCGAGCGAACAGATAAGGAGCTTGCTCCTTTGACGTTAGCGGCGGACGGGTGAGTAACACGTGGGTAACCTACCTATAAGACTGGGACAACTTCGGGAAACCGGAGCTAATACCGGATAATATGTTGAACCGCATGGTTCAATAGTGAAAGATGGTTTTGCTATCACTTATAGATGGACCCGCGCCGTATTAGCTAGTTGGTGAGGTAACGGCTCACCAAGGCAACGATACGTAGCCGACCTGAGAGGGTGATCGGCCACACTGGAACTGAGACACGGTCCAGACTCCTACGGGAGGCAGCAGTAGGGAATCTTCCGCAATGGGCGAAAGCCTGACGGAGCAACGCCGCGTGAGTGATGAAGGTCTTAGGATCGTAAAACTCTGTTATTAGGGAAGAACAAACGTGTAAGTAACTGTGCACGTCTTGACGGTACCTAATCAGAAAGCCACGGCTAACTA'
    print fasta(s1,s2)

if __name__=='__main__':
    test_ssearch()
