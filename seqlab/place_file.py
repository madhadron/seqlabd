import shutil
import json
import time
import os
import re

def ensure_isdir(path):
    if os.path.isdir(path):
        return
    elif os.path.exists(path):
        raise ValueError('Path %s already exists, but is not a directory' % path)
    else:
        ensure_isdir(os.path.split(path)[0])
        os.mkdir(path)


def seqkey(filepath):
    _, filename = os.path.split(filepath)
    m = re.search(r'^\d+\.(\d+)_[A-Za-z0-9_-]+\.ab1$', filename)
    if m:
        seqkey = int(m.groups()[0])
        return seqkey
    else:
        raise ValueError("Could not find a sequence key in filepath %s" % filepath)
    

def seqkey_to_workup(dbconn, sk):
    curs = dbconn.cursor()
    curs.execute("""select accession, pat_name, amp_name from workups where seq_key=?""", (sk,))
    row = curs.fetchone()
    if row:
        accession, pat_name, amp_name = row
        return {'accession': accession, 'pat_name': pat_name, 'amp_name': amp_name, 'seq_key': sk}
    else:
        raise ValueError("Sequence key %d did not correspond to any row in the database." % (sk,))

def pathify(s):
    n, c = re.subn(r'[^A-Za-z0-9-_,\.]', r'_', s)
    return n

def place_file(filepath, dbconn, target_path, leave_original=False, current_time=None):
    if not(current_time):
        t = time.localtime()
    else:
        t = current_time
    workup = seqkey_to_workup(dbconn, seqkey(filepath))
    pat_lastname = workup['pat_name'].split(',')[0]
    path = os.path.join(target_path, time.strftime('%Y', t),
                        time.strftime('%Y_%B', t), time.strftime('%Y_%m_%d', t),
                        '%s_%s_%s' % (workup['accession'], pathify(pat_lastname), pathify(workup['amp_name'])))
    ensure_isdir(path)
    workup['path'] = path
    if leave_original:
        shutil.copy(filepath, path)
    else:
        shutil.move(filepath, path)
    with open(os.path.join(path, 'workup.json'), 'w') as h:
        json.dump(workup, h)
    
