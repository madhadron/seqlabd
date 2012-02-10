import logging
import os

#from  seqlab.sequence_report import sequence_report

log = logging.getLogger(__name__)

def build_parser(parser):
    parser.add_argument('reportpath', help='Path containing AB1 and JSON files where the report will be written.')

def action(args):
    path = os.path.abspath(args.reportpath)
    if not(os.path.exists(os.path.join(path, 'workup.json'))):
        print "Error: Could not find workup.json in %s" % path
        return 1
    ab1_files = [x for x in os.listdir(path) if x.endswith('.ab1')]
    if len(ab1_files) != 2:
        print "Error: Expected 2 AB1 files; found %d" % len(ab1_files)
        return 1
    try:
        # result, html = sequence_report(workup, ab1_files[0], ab1_files[1])
        html_filename = result=='assembled' and 'assembly_report.html' or 'strandwise_report.html'
        # with open(os.path.join(path, html_filename), 'w') as h:
        #     print >>h, html
    except Exception, e:
        print "Error: " + str(e)
        return 1
    else:
        return 0
