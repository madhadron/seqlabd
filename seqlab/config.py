import os
import ConfigParser

def read_configuration(handle):
    default = \
        {'batch_timeout': '15', 'slurp_timeout': '600',
         'share_path': None, 'base_path': None, 'inbox_path': None,
         'db_server': None, 'db_username': None,
         'db_port': '3306', 'db_credentials': None,
         'db_name': None, 'daemon_user': None, 'daemon_group': None}

    scp = ConfigParser.SafeConfigParser(default)
    scp.readfp(handle)
    conf = {'batch_timeout': scp.getint('default','batch_timeout'),
            'slurp_timeout': scp.getint('default','slurp_timeout'),
            'db_port': scp.getint('default','db_port'),
            'db_name': scp.get('default', 'db_name'),
            'share_path': scp.get('default','share_path'),
            'base_path': scp.get('default','base_path'),
            'inbox_path': scp.get('default','inbox_path'),
            'unmatched_path': scp.get('default','unmatched_path'),
            'db_server': scp.get('default','db_server'),
            'db_username': scp.get('default','db_username'),
            'db_credentials': scp.get('default', 'db_credentials'),
            'max_retries': scp.getint('default', 'max_retries'),
            'daemon_user': scp.get('default', 'daemon_user'),
            'daemon_group': scp.get('default', 'daemon_group')}
    target_path = os.path.join(conf['share_path'], conf['base_path'])
    if conf['batch_timeout'] < 1:
        raise ValueError("batch_timeout must be a positive integer, found %d" \
                             % conf['batch_timeout'])
    if conf['slurp_timeout'] < 1:
        raise ValueError("slurp_timeout must be a positive integer, found %d" \
                             % conf['slurp_timeout'])
    if not(os.path.isdir(target_path)):
        raise ValueError("No such path: %s" % target_path)
    if not(os.path.isdir(conf['inbox_path'])):
        raise ValueError("No such path: %s" % conf['inbox_path'])
    if not(os.path.exists(conf['db_credentials'])):
        raise ValueError("No such path: %s" % conf['db_credentials'])
    conf['target_path'] = os.path.abspath(os.path.join(conf['share_path'],conf['base_path']))
    conf['inbox_path'] = os.path.abspath(conf['inbox_path'])
    try:
        with open(conf['db_credentials']) as h:
            conf['db_password'] = h.readline().strip()
    except OSError, e:
        raise ValueError("Couldn't read password from crednetials file %s" % \
                             conf['db_credentials'])
    return conf
            
