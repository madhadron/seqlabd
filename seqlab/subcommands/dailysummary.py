"""Create summary.html for a set of subdirectories containing workups."""

import subprocess
import tempfile
import logging
import shutil
import os

from seqlab.daily_summary import *

log = logging.getLogger(__name__)

def build_parser(parser):
    parser.add_argument('path',
        help='The path to search for workups in')
    parser.add_argument('-n','--nop', action='store_true',
        help="Print details of workups found instead of writing a summary file.")

def action(args):
    if not(os.path.isdir(args.path)):
        raise ValueError("No such path: %s" % (args.path,))
    if args.nop:
        print summarize_workups(map(usable_workup, subdirs(args.path)))
    else:
        daily_summary(args.path)
    return 0
