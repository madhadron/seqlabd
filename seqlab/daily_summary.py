import templet
import os
import time
import pprint
import locale
import math
import collections
import syslog
import json

import ab1
import contig

def subdirs(path):
    return [os.path.join(path,p) for p in os.listdir(path) if os.path.isdir(os.path.join(path, p))]

def usable_workup(path):
    json_path = os.path.join(path, 'workup.json')
    assembly_path = os.path.join(path, 'assembly_report.html')
    strandwise_path = os.path.join(path, 'strandwise_report.html')

    if not(os.path.exists(json_path)):
        return (path, False, "No workup.json in path.")
    with open(os.path.join(json_path)) as h:
        workup = json.load(h)
    if os.path.exists(os.path.join(path, 'assembly_report.html')):
        ctime = os.stat(os.path.join(path,'assembly_report.html')).st_ctime
        return (path, True, "assembled", ctime, workup)
    if os.path.exists(os.path.join(path, 'strandwise_report.html')):
        ctime = os.stat(os.path.join(path,'strandwise_report.html')).st_ctime
        return (path, True, "strandwise", ctime, workup)
    return (path, False, "No report found.")

def summarize_workups(workups):
    usable = sorted([w for w in workups if w[1]], key=lambda x: x[3])
    unusable = [w for w in workups if not w[1]]
    txt = ""
    for w in usable:
        path, usable, status, time, workup = w
        txt += "%s - %s: %s\n" % (status, path, pprint.pformat(workup))
    for w in unusable:
        path, usable, reason = w
        txt += "unusable - %s: %s\n" % (path, reason)
    return txt

def subdirs_for_summary(path):
    paths = []
    for p in os.listdir(path):
        if not(os.path.isdir(os.path.join(path,p))):
            continue
        if os.path.exists(os.path.join(path,p,'assembly_report.html')):
            assembled = True
            ctime = os.stat(os.path.join(path,p,'assembly_report.html')).st_ctime
        elif os.path.exists(os.path.join(path,p,'strandwise_report.html')):
            assembled = False
            ctime = os.stat(os.path.join(path,p,'strandwise_report.html')).st_ctime
        else:
            continue
        if not(os.path.exists(os.path.join(path,p,'workup.json'))):
            syslog.syslog(syslog.LOG_ERR, 'Report found in %s, but no workup.json' % p)
            continue
        else:
            with open(os.path.join(path,p,'workup.json')) as h:
                workup = json.load(h)
        paths.append((ctime,workup,p,assembled))
    paths.sort(key=lambda a: a[0])
    return [x[1:] for x in paths]

@templet.stringfunction
def summary_entry((workup, path, assembled)):
    """<div class="${assembled and 'assembled' or 'strandwise'} workup"><a href="${os.path.join(path,assembled and 'assembly_report.html' or 'strandwise_report.html')}">${workup['accession']} ${workup['pat_name']} (${workup['amp_name']}) - ${assembled and 'assembled' or 'no assembly'}</a></div>"""

@templet.stringfunction    
def daily_summary_html(date, entries):
    """
    <html><head><title>Daily summary: $date</title>
    <style>
    * { margin: 0; padding: 0; }
    body { font-family: "Times New Roman", serif; font-size: 100%; line-height: 1; }
    h1 { font-size: 2.617em; line-height: 1.528em; vertical-align: baseline; padding: 0 0.382em 0 0.382em; }
    div.workup { font-size: 1.618em; line-height: 2.472em; vertical-align: middle; border: 1px solid black; }
    div.assembled { background-color: #37dd6f; color: #000; }
    div.assembled:hover { background-color: #00bb3f; color: #fff; }
    div.strandwise { background-color: #ff2800; color: #000; }
    div.strandwise:hover { background-color: #ff5d40; color: #fff; }
    div.workup a { text-decoration: none; color: inherit; width: 100%; height: 2.472em; padding: 0 0.618em 0 0.618em; display: block; }
    </style>
    </head><body>
    <h1>Daily summary: $date</h1>
    ${[summary_entry(x) for x in entries]}
    </body></html>
    """

def daily_summary(path):
    date = os.path.split(path)[1]
    entries = subdirs_for_summary(path)
    text = daily_summary_html(date, entries)
    with open(os.path.join(path,'summary.html'), 'w') as h:
        print >>h, text


