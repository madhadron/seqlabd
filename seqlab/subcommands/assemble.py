"""Assemble a pair of AB1 files and store the result in a file."""
import os
import bz2
import json
import logging
import Bio.SeqIO

import seqlab.contig
import seqlab.assembly

log = logging.getLogger(__name__)

def build_parser(parser):
    parser.add_argument('output',
        help='bzipped JSON file to contain the assembly')
    parser.add_argument('first_ab1',
        help='AB1 file of strand 1')
    parser.add_argument('second_ab1',
        help='AB1 file of strand 2')
    parser.add_argument('-m','--metadata', default=None, metavar='metadata.json',
        help='JSON file of metadata to store in assembly')
    parser.add_argument('-a', '--additional-sequences', nargs='+', 
                        metavar='seq.fasta ...',
                        help='FASTA files of additional sequences to include')

def action(args):
    if not os.path.exists(args.first_ab1):
        raise ValueError("No such file: %s" % (args.first_ab1,))
    if not os.path.exists(args.second_ab1):
        raise ValueError("No such file: %s" % (args.second_ab1,))
    if args.metadata and not os.path.exists(args.metadata):
        raise ValueError("No such file: %s" % (args.metadata))
    for f in args.additional_sequences:
        if not os.path.exists(f):
            raise ValueError("No such file: %s" % (f,))

    assembly = seqlab.contig.ab1toassembly(args.first_ab1, args.second_ab1)
    if args.metadata:
        with open(args.metadata) as h:
            assembly.metadata = json.load(h)
    for f in args.additional_sequences:
        with open(f):
            for seq in Bio.SeqIO.parse(f, 'fasta'):
                assembly.add_sequence(seq.description, seq.seq.tostring(),
                                      align_to='contig')
    assembly.serialize(args.output)
    return 0 
