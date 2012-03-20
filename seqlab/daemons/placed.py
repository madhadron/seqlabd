"""
placed.py - Guts of the placement daemon.
"""
import sys
import os
import oursql
import syslog
import seqlab.place
import seqlab.config as cf
import pydaemonize
import pyinotify

# This is still using the old pydaemonize API, and at some point
# should be upgraded to the new one.
class PlacementDaemon(pydaemonize.Daemon):
    def __init__(self, config_path='/etc/seqlab.conf', *args, **kwargs):
        self.config_path = config_path
        pydaemonize.Daemon.__init__(self, *args, **kwargs)
    def action(self):
        with open(self.config_path) as h:
            config = cf.read_configuration(h)
        db = oursql.connect(host=config['db_server'],
                            user=config['db_username'],
                            passwd=config['db_password'],
                            db=config['db_name'],
                            port=config['db_port'])
    
        syslog.syslog(syslog.LOG_NOTICE, "Placed monitoring %s for incoming files." % (config['inbox_path'],))
    
        class Handler(pyinotify.ProcessEvent):
            def process_IN_UNMOUNT(self, event):
                syslog.syslog(syslog.LOG_NOTICE, "Backing filesystem of %s was unmounted. Exiting." % event.path)
                exit(0)
            def process_default(self, event):
                syslog.syslog(syslog.LOG_NOTICE, "File %s created...processing." % (event.pathname,))
                seqlab.place.placewrapper(db, event.pathname, config['target_path'])
    
        wm = pyinotify.WatchManager()
        notifier = pyinotify.Notifier(wm, Handler())
        wm.add_watch(config['inbox_path'], pyinotify.IN_CREATE, rec=True)
        notifier.loop()


def main(args=None):
    parser = argparse.ArgumentParser(description='File placing daemon')
    parser.add_argument('-c','--config', default=None,
        help="Config file to read (default: /etc/seqlab.conf")
    parser.parse_args(args)
    daemon = PlacementDaemon(parser.config)
    exit(0)
