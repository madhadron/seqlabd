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
import seqlab.sequence_report as sr
import seqlab.config as cf

def try_report(path, omit_blast):
    files = os.listdir(path)
    ab1s = [x for x in files if x.endswith('.ab1')]
    if 'workup.json' in files and len(ab1s) >= 2:
        with open(os.path.join(path,'workup.json')) as h:
            workup = json.load(h)
        try:
            syslog.syslog(syslog.LOG_NOTICE, 'Building sequence report in %s' % (path,))
            fate, body = sr.sequence_report((workup, \
                                             os.path.join(path,ab1s[0]),
                                             os.path.join(path, ab1s[1])),
                                            omit_blast)
        except Exception, ex:
            return False, str(ex)
        if fate == 'assembled':
            output_filename = os.path.join(path, 'assembly_report.html')
        elif fate == 'strandwise':
            output_filename = os.path.join(path, 'assembly_report.html')
        with open(output_filename, 'w') as output:
            print >>output, body
        return True, output_filename
    else:
        return False, 'Not a full complement of files.'


class SequenceReportDaemon(pydaemonize.Daemon):
    def __init__(self, config_path='/etc/seqlab.conf', omit_blast=False, 
                 *args, **kwargs):
        self.config_path = config_path
        self.omit_blast = omit_blast
        pydaemonize.Daemon.__init__(self, *args, **kwargs)
    def action(self):
        omit_blast = self.omit_blast
        with open(self.config_path) as h:
            config = cf.read_configuration(h)
        monitor_path = config['target_path']
        syslog.syslog(syslog.LOG_NOTICE, "sequencereportd monitoring %s for runs to process." % monitor_path)
        class Handler(pyinotify.ProcessEvent):
            def process_IN_UNMOUNT(self, event):
                syslog.syslog(syslog.LOG_NOTICE, "Backing filesystem of %s was unmounted. Exiting." % \
                                  (event.path,))
                exit(0)
            def process_default(self, event):
                syslog.syslog(syslog.LOG_NOTICE, "Event on %s in monitored share." % (event.pathname,))
                if event.name != 'workup.json' and \
                        not event.name.endswith('.ab1'):
                    syslog.syslog(syslog.LOG_NOTICE, "Ignoring event on %s." % (event.pathname,))
                    return

                wrote, result = try_report(event.path, omit_blast)
                if not wrote:
                    syslog.syslog(syslog.LOG_NOTICE, "No action in %s: %s" % \
                                      (event.path,result))
                else:
                    syslog.syslog(syslog.LOG_NOTICE, "Wrote report in %s." % (result,))
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
    parser = argparse.ArgumentParser(description='Sequence report generation daemon')
    parser.add_argument('-c','--config', default=None,
        help="Config file to read (default: /etc/seqlab.conf")
    parser.add_argument('--noblast', action='store_true',
        help="Don't run BLAST")
    parser.parse_args(args)
    daemon = SequenceReportDaemon(config_path=parser.config, 
                                  omit_blast=parser.noblast)
    exit(0)
