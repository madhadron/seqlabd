"""Render an AB1 file to HTML for viewing."""

import subprocess
import tempfile
import logging
import shutil
import os
import sys
import seqlab.ab1
from seqlab.assembly import ab1tohtml

log = logging.getLogger(__name__)

def build_parser(parser):
    parser.add_argument('ab1',
        help='AB1 of file to render')
    parser.add_argument('-o', '--output',
        action='store', default=None,
        help='filename to write HTML to')

def action(args):
    s = ab1tohtml(args.ab1)
    if args.output:
        with open(args.output, 'w') as out:
            print >>out, s
    else:
        print s
    return 0

