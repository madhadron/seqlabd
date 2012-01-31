import templet
import os
import time
import locale
import math
import collections
import syslog
import json

import tracks
import ab1
import contig

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


