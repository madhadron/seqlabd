import logging
import seqlab.place_file
import os

log = logging.getLogger(__name__)

def build_parser(parser):
    parser.add_argument('file',
        help='The file to place')
    parser.add_argument('-s','--sqlite',
        help='SQLite3 database to use instead of MySQL')
    parser.add_argument('-h','--host',
        help='Host where MDX database is running')
    parser.add_argument('-p','--port', type=int,
        help='Port where MDX database is running')
    parser.add_argument('-u','--user',
        help='Username to connect to MDX database')
    parser.add_argument('-P','--password',
        help='Password to connect to MDX database')
    parser.add_argument('-d','--database',
        help='Database name of MDX database')
    parser.add_argument('-t','--target',
        help='Base path where files should be placed')

def action(args):
    if args.sqlite:
        import sqlite3
        conn = sqlite3.connect(args.sqlite)
    else:
        import oursql
        conn = oursql.connect(host=args.host,
                              user=args.user,
                              passwd=args.password,
                              db=args.database,
                              port=args.port)
    try:
        seqlab.place_file.place_file(os.path.abspath(args.file),
                                     conn, args.target)
    except Exception, e:
        print "Failure: " + str(e)
        return 1
    else:
        return 0
