import collections
import syslog
import os
import re
import time
import shutil
import Bio.Blast.NCBIWWW
import Bio.Blast.NCBIXML

import tracks
import mdx

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
        ensure_isdir(os.path.split(path)[0])
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

def process_pair(share_path_ref, workup_path_ref, analysis_queue, mdx_ref, leave_original=False):
    def f(workup, path1, path2):
        t = time.localtime()
        pat_name = re.split(r',\s', workup.pat_name)[0].upper()
        path = os.path.join(share_path_ref.get(), workup_path_ref.get(), time.strftime('%Y', t),
                            time.strftime('%Y_%B', t), time.strftime('%Y_%m_%d', t),
                            '%s_%s_%s' % (workup.workup, pat_name, workup.amp_name))
        ensure_isdir(path)
        new_path1 = os.path.join(path, os.path.split(path1)[1])
        new_path2 = os.path.join(path, os.path.split(path2)[1])
        if leave_original:
            shutil.copy(path1, new_path1)
            shutil.copy(path2, new_path2)
        else:
            shutil.move(path1, new_path1)
            shutil.move(path2, new_path2)
        mdx_ref.update_by_workup(workup.workup, path)
        new_pair = (mdx.Workup(accession=workup.accession, workup=workup.workup, pat_name=workup.pat_name,
                               amp_name=workup.amp_name, path=path),
                    new_path1, new_path2)
        analysis_queue.put(new_pair)
    return f

def find_workup(mdx_ref):
    def f(path):
        pattern = r'^(?P<tube_number>[A-Za-z0-9]+)\.(?P<sequence_key>[A-Za-z0-9_]+)\.ab1$'
        filename = os.path.split(path)[1]
        m = re.match(pattern, filename)
        if m:
            seqkey = m.groupdict()['sequence_key']
            workup = mdx_ref.lookup_by_sequence_key(seqkey)
            return workup
        else:
            raise ValueError("Could not extract a sequence key from filepath %s" % path)
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

def blast_seq(seq, save_path, ncbi_db='nr'):
    h = Bio.Blast.NCBIWWW.qblast("blastn", ncbi_db, seq)
    res = h.read()
    h.close()
    with open(save_path, 'w') as xh:
        xh.write(res)
    with open(save_path, 'r') as xh:
        records = list(Bio.Blast.NCBIXML.parse(xh))
        return records[0]


    
             
