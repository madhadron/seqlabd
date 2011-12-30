from signal import *
import functools

import config

def set_signal_handlers(conf_ref, exit_evt):
    signal(SIGHUP, functools.partial(sighup, conf_ref))
    signal(SIGTERM, functools.partial(sigterm, exit_evt))
    signal(SIGINT, SIG_DFL)
    signal(SIGPIPE, SIG_IGN)
    signal(SIGALRM, SIG_IGN)
    signal(SIGUSR1, SIG_IGN)
    signal(SIGUSR2, SIG_IGN)
    signal(SIGCHLD, SIG_IGN)

def sighup(conf_ref, sig, stackframe):
    try:
        with open('/etc/seqlabd.conf') as h:
            conf = config.read_configuration(h)
        conf_ref.put(conf)
        syslog.syslog(syslog.LOG_INFO, "Received SIGHUP. Reread configuration.")
    except:
        syslog.syslog(syslog.LOG_ERROR, "Received SIGHUP, but failed to reread"
                      "configuration. Continuing with old configuration.")

def sigterm(exit_evt, sig, stackframe):
    syslog.syslog(syslog.LOG_INFO, "Received SIGTERM. Signalling exit internally.")
    exit_evt.set()
