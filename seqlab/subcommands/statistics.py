"""Calculate statistics on an assembly."""
import logging
import seqlab.config
import seqlab.statistics
import seqlab.assembly
import os
import sys
import csv


log = logging.getLogger(__name__)

def build_parser(parser):
    parser.epilog = """The following statistical functions are available:""" + \
        ''.join(["%s:\%s\n" % (n, seqlab.statistics.__getattribute__(n).__doc__) for f in dir(seqlab.statistics)])
    parser.add_argument('assembly', type=str,
        help='Path to the assembly')
    parser.add_argument('label1',
        help='Label of first track to compare')
    parser.add_argument('label2',
        help='Label of second track to compare')
    parser.add_argument('fields', type=str,
        help='Comma separated list of statistics to report (available: ' + \
                            ', '.join(seqlab.statistics.commands.keys()))
    parser.add_argument('-o','--output', default=None,
        help='File to write CSV output to (default: stdout). Appends instead of overwriting.')


def action(args):
    try:
        stats = args.fields.split(',')
        commands = dir(seqlab.statistics)
        for s in stats:
            if not s in commands:
                raise ValueError("No such statistic: %s" % s)
        if not os.path.exists(args.assembly):
            raise ValueError("No such assembly file: %s" % args.assembly)
        assembly = seqlab.assembly.deserialize(args.assembly)
        if not args.label1 in assembly:
            raise ValueError("No such label %s in assembly %s" % (args.labe1l, args.assembly))
        if not args.label2 in assembly:
            raise ValueError("No such label %s in assembly %s" % (args.label2, args.assembly))
        result = [seqlab.statistics.__getattribute__(s)(assembly, args.label1, args.label2)
                  for s in stats]
        if args.output is None:
            cw = csv.writer(sys.stdout)
            cw.writerow(result)
        else:
            with open(args.output, 'a') as output:
                cw = csv.writer(output)
                cw.writerow(result)
        return 0
    except Exception, e:
        print "Error: " + str(e)
        return -1
