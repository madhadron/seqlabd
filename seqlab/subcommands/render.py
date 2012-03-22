"""Render an AB1 file to HTML for viewing."""

import logging
import os
import sys
from seqlab.assembly import renderassembly, deserialize

log = logging.getLogger(__name__)

def build_parser(parser):
    parser.add_argument('assembly',
        help='Assembly to render')
    parser.add_argument('-o', '--output',
        action='store', default=None,
        help='filename to write HTML to')

def action(args):
    if not os.path.exists(args.assembly):
        raise ValueError("No such file: %s" % (args.assembly,))
    asm = deserialize(args.assembly)
    s = renderassembly(asm)
    if args.output:
        with open(args.output, 'w') as out:
            print >>out, s
    else:
        print s
    return 0

