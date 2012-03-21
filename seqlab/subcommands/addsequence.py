"""Assemble a pair of AB1 files and store the result in a file."""
import os
import logging
import Bio.SeqIO

import seqlab.assembly

log = logging.getLogger(__name__)

def build_parser(parser):
    parser.add_argument('assembly',
        help='bzipped JSON file containing assembly')
    parser.add_argument('-o','--output', default=None,
        help='File to write new assembly to (default: overwrite input.')
    parser.add_argument('-n','--no-alignment', action='store_true',
        help="Don't try to align new sequences, just add them at offset 0.")
    parser.add_argument('-a','--align-to', default='contig',
        help='Sequence to align new sequences to')                        
    parser.add_argument('fastas', nargs='+', 
                        metavar='seq.fasta ...',
                        help='FASTA files of additional sequences to include')

def action(args):
    if not os.path.exists(args.assembly):
        raise ValueError("No such file: %s" % (args.assembly,))
    for f in args.fastas:
        if not os.path.exists(f):
            raise ValueError("No such file: %s" % (f,))

    assembly = seqlab.assembly.deserialize(args.assembly)
    for f in args.fastas:
        with open(f):
            for seq in Bio.SeqIO.parse(f, 'fasta'):
                assembly.add_sequence(seq.description, seq.seq.tostring(),
                                      align_to=args.align_to if not args.no_alignment else None)
    assembly.serialize(args.output if args.output else args.assembly)
    return 0 
