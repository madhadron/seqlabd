"""BLAST sequence from an assembly."""
import os
import sys
import json
import tempfile
from seqlab.assembly import *
from seqlab.sequence_report import blast_seq

def build_parser(parser):
    parser.add_argument('assembly',
        help='Assembly containing sequence to BLAST')
    parser.add_argument('-l','--label', default='contig',
        help="Label of sequence in assembly to BLAST (default: 'contig')")
    parser.add_argument('-j','--json', default=None, metavar='hits.json',
        help="Write hits to hits.json'")
    parser.add_argument('-x','--xml', default=None, metavar='blast.xml',
        help="Write XML returned by BLAST to blast.xml")
    parser.add_argument('-n', default=None, metavar='N',
        help="Restrict JSON file to top N hits")

def action(args):
    if not os.path.exists(args.assembly):
        raise ValueError("No such file: %s" % (args.assembly,))
    asm = deserialize(args.assembly)
    if not args.label in asm:
        raise ValueError("No label %s in assembly" % (repr(args.label),))
    seq = ''.join([x for x in asm[args.label]])
    if args.xml is None:
        xml_handle, xml_path = tempfile.mkstemp()
        xml_handle.close()
    else:
        xml_path = args.xml

    hits = blast_seq(seq, xml_path)
    query_length = hits.query_length
    hits_for_json = [{'hit_id': h.hit_id,
                      'hit_def': h.hit_def,
                      'length': h.length,
                      'query_length': query_length,
                      'hsps': [{'score': hs.score,
                                'expect': hs.expect,
                                'align_length': hs.align_length,
                                'identities': hs.identities,
                                'gaps': hs.gaps,
                                'query_start': hs.query_start,
                                'query_end': hs.query_end,
                                'sbjct_start': hs.sbjct_start,
                                'sbjct_end': hs.sbjct_end,
                                'query': hs.query,
                                'sbjct': hs.sbjct,
                                'match': hs.match}
                               for hs in h.hsps]}
                     for h in hits.alignments]
    with open(args.json, 'w') as output:
        json.dump(hits_for_json[:args.n], output)
    return 0
