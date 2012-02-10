import logging
import seqlab.config
import seqlab.place
import os
import oursql
import json

log = logging.getLogger(__name__)

def build_parser(parser):
    parser.add_argument('file', type=str,
        help='Path to the file to place')
    parser.add_argument('-H','--host', type=str,
        help='Host where MDX database is running')
    parser.add_argument('-P','--port', type=int,
        help='Port where MDX database is running')
    parser.add_argument('-u','--user',
        help='Username to connect to MDX database')
    parser.add_argument('-p','--password',
        help='Password to connect to MDX database')
    parser.add_argument('-d','--database',
        help='Database name of MDX database')
    parser.add_argument('-c','--config', default='/etc/seqlab.conf',
        help='Configuration file to read')
    parser.add_argument('-o','--output',
        help='File to write JSON output to (default: stdout)')

def configuration(args):
    with open(args.config) as c:
        config = seqlab.config.read_configuration(c)
    if args.port:
        config['db_port'] = args.port
    if args.host:
        config['db_server'] = args.host
    if args.user:
        config['db_username'] = args.user
    if args.password:
        config['db_password'] = args.password
    if args.database:
        config['db_name'] = args.database
    return config

def action(args):
    config = configuration(args)
    import oursql
    conn = oursql.connect(host=config['db_server'],
                          user=config['db_username'],
                          passwd=config['db_password'],
                          db=config['db_name'],
                          port=config['db_port'])
    try:
        key = seqlab.place.seqkey(args.file)
        metadata = seqlab.place.metadata(conn, key)
        s = json.dumps(metadata, sort_keys=True, indent=2)
        if args.output:
            with open(args.output, 'w') as h:
                print >>h, s
        else:
            print s
    except Exception, e:
        print "Failure: " + str(e)
        return 1
    else:
        return 0
