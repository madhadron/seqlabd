import os
import ConfigParser

def read_configuration(handle):
    default = \
        {'batch_timeout': 15, 'slurp_timeout': 600,
         'share_path': None, 'base_path': None, 'inbox_path': None,
         'unmatched_path': None, 'db_server': None, 'db_username': None,
         'max_retries': 3}

    scp = ConfigParser.SafeConfigParser(default)
    scp.readfp(handle)
    conf = {'batch_timeout': scp.getint('default','batch_timeout'),
            'slurp_timeout': scp.getint('default','slurp_timeout'),
            'share_path': scp.get('default','share_path'),
            'base_path': scp.get('default','base_path'),
            'inbox_path': scp.get('default','inbox_path'),
            'unmatched_path': scp.get('default','unmatched_path'),
            'db_server': scp.get('default','db_server'),
            'db_username': scp.get('default','db_username'),
            'max_retries': scp.getint('default', 'max_retries')}
    target_path = os.path.join(conf['share_path'], conf['base_path'])
    if conf['batch_timeout'] < 1:
        raise ValueError("batch_timeout must be a positive integer, found %d" \
                             % conf['batch_timeout'])
    if conf['slurp_timeout'] < 1:
        raise ValueError("slurp_timeout must be a positive integer, found %d" \
                             % conf['slurp_timeout'])
    if conf['max_retries'] < 1:
        raise ValueError("max_retries must be a postive integer, found %d" \
                             % conf['max_retries'])
    if not(os.path.isdir(target_path)):
        raise ValueError("No such path: %s" % target_path)
    if not(os.path.isdir(conf['inbox_path'])):
        raise ValueError("No such path: %s" % conf['inbox_path'])
    if not(os.path.isdir(conf['unmatched_path'])):
        raise ValueError("No such path: %s" % conf['unmatched_path'])
    return conf
            
