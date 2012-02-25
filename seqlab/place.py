"""
place.py - Put AB1 files plus metadata into proper location

This module contains all the guts of the seqplaced daemon and the seq
place command.
"""
import shutil
import functools
import json
import time
import os
import re
import py.path



def place(filepath, keyfun, metadatafun, pathgenfun, basepath, postplacefun):
    """Generic function to place files.

    In summary, puts *filepath* in the proper subdirectory of
    *basepath*, along with a JSON file of the metadata corresponding
    to the file. The other arguments all define the specific behavior
    for doing so:

      - *keyfun*: Takes a path and produces a key identifying the
        file, which will be passed to *metadatafun*.

      - *metadatafun*: Takes a key, as produced by *keyfun*, and
        returns a dictionary of metadata about the file, including
        enough information to calculate the proper subdirectory of
        *basepath* to put it in.

      - *pathgenfun*: Takes a py.path.local object (*basepath*) and a
        dictionary of metadata (as returned by *metadatafun*) and
        returns a py.path.local path to a directory that the file and
        a JSON file containing the metadata should be placed in. The
        path need not exist --- the ``place`` function will create it
        if necessary.

      - *postplacefun*: Function that takes the full path that the
        file was written to and the metadata dictionary and does any
        post-placement actions necessary.

    This generic setup is to make testing simple. For production use,
    its use looks like::

        place(filepath, seqkey, functools.partial(metadata, db),
              genpath, basepath, functools.partial(updatepath, db))

    where ``filepath``, ``db``, and ``basepath`` are all defined
    beforehand.
    """
    if isinstance(basepath, str):
        basepath = py.path.local(basepath)
    if isinstance(filepath, str):
        filepath = py.path.local(filepath)
    if not(filepath.check(file=1, exists=1)):
        raise ValueError("No regular file to place at %s" % filepath)
    key = keyfun(filepath)
    metadata = metadatafun(key)
    targetpath = pathgenfun(basepath, metadata)
    targetpath.ensure(dir=True)
    finalpath = targetpath.join(filepath.basename)
    filepath.move(finalpath)
    targetpath.join('metadata.json').write(json.dumps(metadata))
    postplacefun(finalpath, metadata)
    return (finalpath, metadata)

def placewrapper(db, filepath, basepath):
    return place(filepath, seqkey, functools.partial(metadata, db),
                 genpath, basepath, functools.partial(updatepath, db))

def seqkey(filepath):
    """Extracts a key from *filepath*.

    *filepath* should be a py.path.local object pointing to an AB1 file.
    """
    if isinstance(filepath, str):
        filename = os.path.basename(filepath)
    else:
        filename = filepath.basename
    m = re.search(r'^\d+\.(\d+)_[A-Za-z0-9_-]+\.ab1$', filename)
    if m:
        seqkey = int(m.groups()[0])
        return seqkey
    else:
        raise ValueError("Could not find a sequence key in filepath %s" % filepath)
    

def metadata(db, key):
    """Fetch metadata from database *db* with seq_key *key*.

    The result is returned as a dictionary.
    """
    c = db.cursor()
    c.execute("""select accession, pat_name, amp_name, specimen_description,
                        specimen_category, test1_code, test1_name,
                        test2_code, test2_name,
                        test3_code, test3_name,
                        test4_code, test4_name,
                        test5_code, test5_name,
                        test6_code, test6_name,
                        test7_code, test7_name,
                        test8_code, test8_name,
                        test9_code, test9_name
                 from workups where seq_key=?""", (key,))
    row = c.fetchone()
    if row:
        accession, pat_name, amp_name, specimen_description, \
            specimen_category, test1_code, test1_name, \
                        test2_code, test2_name, \
                        test3_code, test3_name, \
                        test4_code, test4_name, \
                        test5_code, test5_name, \
                        test6_code, test6_name, \
                        test7_code, test7_name, \
                        test8_code, test8_name, \
                        test9_code, test9_name = row
        d = {'accession': accession, 
             'pat_name': pat_name, 
             'amp_name': amp_name, 
             'seq_key': key,
             'specimen_description': specimen_description,
             'specimen_category': specimen_category,
             'tests': []}
        for code,name in [(test1_code, test1_name),
                          (test2_code, test2_name), 
                          (test3_code, test3_name), 
                          (test4_code, test4_name), 
                          (test5_code, test5_name), 
                          (test6_code, test6_name), 
                          (test7_code, test7_name), 
                          (test8_code, test8_name)]:
            if code and name:
                d['tests'].append((code,name))
        return d
    else:
        raise ValueError("Sequence key %d did not correspond to any row in the database." % (sk,))

def pathify(s):
    """Replace all 'odd' characters and spaces with underscores."""
    n, c = re.subn(r'[^A-Za-z0-9-_,\.]', r'_', s)
    return n

def genpath(basepath, metadata, current_time=time.localtime()):
    """Generate a full path from *basepath* and *metadata*.

    *basepath* should be a py.path.local object and metadata a
    dictionary containing the keys 'accession', 'pat_name', and
    'amp_name'.

    *current_time* is specified for testing purposes, and otherwise
    default to the current, local time.
    """
    return basepath.join(time.strftime('%Y', current_time),
                         time.strftime('%Y_%B', current_time),
                         time.strftime('%Y_%m_%d', current_time),
                         '%s_%s_%s' % (metadata['accession'],
                                       pathify(metadata['pat_name'].split(',')[0]),
                                       pathify(metadata['amp_name'])))
    
def updatepath(db, finalpath, metadata):
    """Updates the record in *db* corresponding to the file described by *finalpath* and *metadata.

    *db* is a connection to the MDX database. *finalpath* is a
    py.path.local object giving the full path to the AB1 file after it
    has been placed. *metadata* is a dictionary giving all the
    metadata of the file.
    """
    c = db.cursor()
    c.execute("""update `seq result` set path=? where `Seq Result ID`=?""",
              (str(finalpath.dirpath()), metadata['seq_key']))




