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
import sequence_report

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
        if os.path.exists(os.path.join(path,p,'blast.json')):
            with open(os.path.join(path,p,'blast.json')) as h:
                blast = json.load(h)
        else:
            blast = None
        paths.append((ctime,workup,p,assembled,blast))
    paths.sort(key=lambda a: a[0])
    return [x[1:] for x in paths]

def blast_hit(blast):
    if blast is None or len(blast) == 0:
        return ""
    else:
        usable = [b for b in blast if not sequence_report.is_unclassified(b['hit_def'])]
        if usable == []:
            return "No well annotated BLAST hit found. Found %s" % (blast[0]['hit_def'],)
        else:
            b = usable[0]
            return sequence_report.render_blast_alignment(b, 0, 0, b['query_length'], hidden=True)

@templet.stringfunction
def summary_entry((workup, path, assembled, blast)):
    """<div class="${assembled and 'assembled' or 'strandwise'} workup"><a href="${os.path.join(path,assembled and 'assembly_report.html' or 'strandwise_report.html')}"><div class="entry">
       <h2>${workup['accession']} ${workup['pat_name']} (${workup['amp_name']}) - ${assembled and 'assembled' or 'no assembly'}</h2>
       <p>${sequence_report.description(workup)}</p>
       <p>Top hit:</p>
       ${blast_hit(blast)}
       </div></a></div>"""

@templet.stringfunction    
def daily_summary_html(date, entries):
    """
    <html><head><title>Daily summary: $date</title>
    <style>
    * { margin: 0; padding: 0; }
    body { font-family: "Times New Roman", serif; font-size: 100%; line-height: 1; }
    h1 { font-size: 2.617em; line-height: 1.528em; vertical-align: baseline; padding: 0 0.382em 0 0.382em; }
    h2 { font-size: 1.618em; line-height: 1.618em; }
    div.workup { font-size: 1.618em; line-height: 2.472em; vertical-align: middle; border: 1px solid black; }
    div.assembled { background-color: #37dd6f; color: #000; }
    div.assembled:hover { background-color: #00bb3f; }
    div.strandwise { background-color: #ff2800; color: #000; }
    div.strandwise:hover { background-color: #ff5d40; }
    div.workup a { text-decoration: none; color: inherit; width: 100%; padding: 0; display: block; }
    div.entry { margin: 0.5em; line-height: 1.2; }
    li { margin-left: 1em; padding-left: 0.5em; list-style: dot; }
    ${sequence_report.blast_css()}
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
    output_filename = os.path.join(path, 'summary.html')
    with open(output_filename, 'w') as h:
        print >>h, text
    return output_filename


