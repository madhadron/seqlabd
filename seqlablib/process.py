import collections
import syslog
import os
import shutil

def pair_up(it, key_fun):
    unpaired = {}
    pairs = {}
    for i in it:
        k = key_fun(i)
        if k in unpaired:
            pairs[k] = (unpaired.pop(k), i)
        else:
            unpaired[k] = i
    singles = unpaired
    return (pairs, singles)

def ensure_isdir(path):
    if os.path.isdir(path):
        return
    elif os.path.exists(path):
        raise ValueError('Path %s already exists, but is not a directory' % path)
    else:
        os.mkdir(path)

def ensure_paths_exist(paths):
    existant_paths = []
    for f in paths:
        if os.path.exists(f):
            existant_paths.append(f)
        else:
            syslog.syslog(syslog.LOG_WARNING, 'Not processing nonexistant file %s' % f)
    return existant_paths
    

def requeue_n_times(queue, n_retries_ref, fallthrough_fun):
    remaining_retries = collections.defaultdict(lambda: n_retries_ref.get())
    def f(k,p):
        if remaining_retries[p] == 0:
            remaining_retries.pop(p)
            syslog.syslog(syslog.WARNING, "Path %s requeued too many times: falling through." % p)
            fallthrough_fun(k,p)
        else:
            remaining_retries[p] -= 1
            queue.put(p)
    return f

def process(pair_by, unmatched_fun, pair_fun):
    def f(filepaths_set):
        paths = ensure_paths_exist(filepaths_set)
        pairs, singles = pair_up(paths, pair_by)
        for k,p in singles.iteritems():
            try:
                unmatched_fun(k,p)
            except Exception, e:
                syslog.syslog(syslog.LOG_ERR, 'There was an error in processing %s %s: %s' % \
                                  (p,str(e)))
        for k,(a,b) in pairs.iteritems():
            try:
                pair_fun(k,a,b)
            except Exception, e:
                syslog.syslog(syslog.LOG_ERR, 'There was an error in processing pair %s:(%s, %s): %s' % \
                                  (k,a,b,str(e)))
    return f
