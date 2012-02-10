"""
placed.py - Guts of the placement daemon.
"""
import os
import oursql
import syslog
import place
import config as cf
import signals
import pydaemonize
import pyinotify
import threading

def daemonaction(configpath='/etc/seqlab.conf'):
    with open(configpath) as h:
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
            place.placewrapper(db, event.pathname, config['target_path'])

    wm = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm, Handler())
    wm.add_watch(config['inbox_path'], pyinotify.IN_CREATE, rec=True)
    notifier.loop()


# def daemon():
#     pydaemonizey.daemon(config['inbox_path'],
#                                callback=action,
#                                init=init,
#                                mask=pydaemonize.inotify.IN_CREATE)
#                                # user=config['daemon_user'],
#                                # group=config['daemon_group'])

if __name__=='__main__':
    main()
    
        

