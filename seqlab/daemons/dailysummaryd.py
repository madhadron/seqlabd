"""
Daemon to monitor a file hierarchy and create sequence reports.

Any time 'workup.json' or any .ab1 file is added to a directory, check
if there is a usable set of files in that directory. If so, generate a
sequence report for them.
"""
import os
import pydaemonize
import pyinotify
import syslog
import json
import seqlab.daily_summary as ds
import seqlab.config as cf


def summarize(path):
    try:
        return True, ds.daily_summary(path)
    except Exception, e:
        return False, str(e)


class DailySummaryDaemon(pydaemonize.Daemon):
    def __init__(self, config_path='/etc/seqlab.conf', omit_blast=False, 
                 *args, **kwargs):
        self.config_path = config_path
        pydaemonize.Daemon.__init__(self, *args, **kwargs)
    def action(self):
        with open(self.config_path) as h:
            config = cf.read_configuration(h)
        monitor_path = os.path.join(config['share_path'],
                                    config['base_path'])
        syslog.syslog(syslog.LOG_NOTICE, "dailysummaryd monitoring %s for reports to summarize." % monitor_path)
        class Handler(pyinotify.ProcessEvent):
            def process_IN_UNMOUNT(self, event):
                syslog.syslog(syslog.LOG_NOTICE, "Backing filesystem of %s was unmounted. Exiting." % \
                                  (event.path,))
                exit(0)
            def process_default(self, event):
                syslog.syslog(syslog.LOG_NOTICE, "Event on %s in monitored share." % (event.pathname,))
                if not event.name.endswith('report.html'):
                    syslog.syslog(syslog.LOG_NOTICE, "Ignoring event on %s." % (event.pathname,))
                    return
                wrote, result = summarize(os.path.dirname(event.path))
                if not wrote:
                    syslog.syslog(syslog.LOG_NOTICE, "No action in %s: %s" % \
                                      (event.path,result))
                else:
                    syslog.syslog(syslog.LOG_NOTICE, "Wrote summary in %s." % (result,))
        wm = pyinotify.WatchManager()
        notifier = pyinotify.Notifier(wm, Handler())
        wm.add_watch(monitor_path,
                     pyinotify.IN_CREATE |
                     pyinotify.IN_DELETE |
                     pyinotify.IN_MOVED_TO |
                     pyinotify.IN_ATTRIB | 
                     pyinotify.IN_MODIFY,
                     rec=True)
        notifier.loop()


def main(args=None):
    parser = argparse.ArgumentParser(description='Daily summary generation daemon')
    parser.add_argument('-c','--config', default=None,
        help="Config file to read (default: /etc/seqlab.conf")
    parser.parse_args(args)
    daemon = DailySummaryDaemon(config_path=parser.config)
    exit(0)
