import os
import ConfigParser

def read_configuration(handle):
    default = \
        {'target_path': None, 'inbox_path': None,
         'db_server': None, 'db_username': None,
         'db_port': '3306', 'db_credentials': None,
         'db_name': None}

    scp = ConfigParser.SafeConfigParser(default)
    scp.readfp(handle)
    conf = {'db_port': scp.getint('default','db_port'),
            'db_name': scp.get('default', 'db_name'),
            'target_path': scp.get('default','target_path'),
            'inbox_path': scp.get('default','inbox_path'),
            'db_server': scp.get('default','db_server'),
            'db_username': scp.get('default','db_username'),
            'db_credentials': scp.get('default', 'db_credentials')}
    if not(os.path.isdir(conf['target_path'])):
        raise ValueError("No such path: %s" % conf['target_path'])
    if not(os.path.isdir(conf['inbox_path'])):
        raise ValueError("No such path: %s" % conf['inbox_path'])
    if not(os.path.exists(conf['db_credentials'])):
        raise ValueError("No such path: %s" % conf['db_credentials'])
    conf['inbox_path'] = os.path.abspath(conf['inbox_path'])
    try:
        with open(conf['db_credentials']) as h:
            conf['db_password'] = h.readline().strip()
    except OSError, e:
        raise ValueError("Couldn't read password from credentials file %s" % \
                             conf['db_credentials'])
    return conf
            
