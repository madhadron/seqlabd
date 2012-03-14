"""Template for a subcommand."""

import subprocess
import tempfile
import logging
import shutil
import os

import seqlab.sequence_report

log = logging.getLogger(__name__)

def build_parser(parser):
    parser.add_argument('path_or_json', type=str,
        help='A required input file')
    parser.add_argument('-1', dest='read1', type=str, default=None,
        help='AB1 file of first read')
    parser.add_argument('-2', dest='read2', type=str, default=None,
        help='AB1 file of second record')
    parser.add_argument('-v', '--verbose', action='store_true',
        help='Run verbosely')
    parser.add_argument('--omit-blast', action='store_true',
        help="Assembly, but don't run BLAST.")
    parser.add_argument('-o', '--output', default=None,
        help='File to write HTML to (default: stdout)')


def workup_files(path):
    """Return the absolute path to workup.json in *path*, and AB1 files.

    If there are more than 2 .ab1 files in the directory, raises an
    error. Otherwise, the returned value is a 3-tuple of workup.json
    and the two AB1s.
    """
    if not(os.path.isfile(os.path.join(path, 'workup.json'))):
        raise ValueError("No workup.json in %s" % (path,))
    workup = os.path.abspath(os.path.join(path, 'workup.json'))
    ab1files = [f for f in os.listdir(path) if f.endswith('.ab1')]
    if len(ab1files) != 2:
        raise ValueError("Could not find precisely 2 .ab1 files in %s" % (path,))
    else:
        return (workup, 
                os.path.abspath(os.path.join(path, ab1files[0])),
                os.path.abspath(os.path.join(path, ab1files[1])))


def action(args):
    if not(os.path.exists(args.path_or_json)):
        raise ValueError("No such path: %s" % args.path_or_json)
    if os.path.isdir(args.path_or_json):
        workup, ab1file1, ab1file2 = workup_files(args.path_or_json)
    else:
        if args.read1 is None or args.read2 is None:
            raise ValueError("Must specify path to AB1 files if path is not a directory.")
        workup = args.path_or_json
        ab1file1 = args.read1
        ab1file2 = args.read2
        
