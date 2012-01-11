import templet
import os
import time
import locale
import math
import collections

import tracks
import ab1
import contig

@templet.stringfunction
def tab_li(i, text):
    """<li id="tab$i"><a href="javascript:show_tab('tab$i')">$text</a></li>"""

@templet.stringfunction
def pane_div(i, text):
    """<div class="hiddentab" id="tab$i">$text</div>"""

@templet.stringfunction
def tabbed_page(title, additional_css, additional_javascript, tabs):
    """
    <html><head>
    <title>$title</title>
    <script type="text/javascript">
    function map_children(fn,tgt){
        var arr=document.getElementById(tgt).childNodes;
        var l=arr.length;
        for(var i=0;i<l;i++){fn(arr[i]);}
    }
    function show_tab(to_show) {
        map_children(function(n) {
                         n.className = n.id==to_show ? "visibletab" : "hiddentab";
                     }, "pane_container");
        map_children(function(n) {
                         n.className = n.id==to_show ? "active" : "";
                     }, "tab_container");
    }
    $additional_javascript
    </script>
    <style>
    $additional_css
    * { margin: 0; padding: 0; }
    div.tab { display: none; }
    body { font-size: 100%; font-family: "Times New Roman", serif; }

    h1 { font-size: 2.617em; line-height: 1.146em; vertical-align: baseline; }

    #tab_container { display: block; white-space: nowrap; width: 100%; height: 2em; background-color: #444; }
    #tab_container li { display: block; float: left; list-style-type: none; font-size: 1.618em; line-height: 1.236em; vertical-align: middle; color: #aaa; border-right: 1px solid black; }
    #pane-container { width: 100%; bottom: 0; }
    #tab_container li a { padding: 0 2em 0 2em; color: inherit; text-decoration: none; }
    #tab_container li a:hover { background-color: #000; }
    #tab_container li.active { color: #fff; }
    #tab_container li.active a:hover { background-color: inherit; }
    .hiddentab { display: none; }
    .visibletab { display: block; margin: 1em 0.2em; }

    h2 { font-size: 1.618em; line-height: 1.236em; }

    /* phi = 1.618 ... 3 font sizes: 1em, 1.618em, 2.617em */

    </style>
    </head><body onload="show_tab('tab0')">
    <h1>$title</h1>

    <ul id="tab_container">${[tab_li(i,k) for i,k in enumerate(tabs.keys())]}</ul>
    <div id="pane_container">${[pane_div(i,v) for i,v in enumerate(tabs.values())]}</div>
    </body></html>
    """

def subdirs_for_summary(path, mdx, key_fun=lambda p: p.split('_')[0]):
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
        k = key_fun(p)
        w = mdx.lookup_by_workup(k)
        paths.append((ctime,w,p,assembled))
    paths.sort(key=lambda a: a[0])
    return [x[1:] for x in paths]

@templet.stringfunction
def summary_entry((workup, path, assembled)):
    """<div class="${assembled and 'assembled' or 'strandwise'} workup"><a href="${os.path.join(path,assembled and 'assembly_report.html' or 'strandwise_report.html')}">${workup.workup} ${workup.pat_name} (${workup.amp_name}) - ${assembled and 'assembled' or 'no assembly'}</a></div>"""

@templet.stringfunction    
def daily_summary(date, entries):
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

def generate_daily_summary(mdx):
    def f(path):
        date = os.path.split(path)[1]
        entries = subdirs_for_summary(path, mdx)
        text = daily_summary(date, entries)
        with open(os.path.join(path,'summary.html'), 'w') as h:
            print >>h, text
    return f


def render_ab1(ab1_dict):
    """*ab1_dict* should be a dict containing keys ``'sequence'``, ``'traces'``, and ``'confidences'``."""
    t = tracks.TrackSet()
    t.extend([tracks.TrackEntry('traces', 0, ab1_dict['traces']),
              tracks.TrackEntry('confidences', 0, ab1_dict['confidences']),
              tracks.TrackEntry('sequence', 0, ab1_dict['sequence'])])
    return tracks.render(t)


def alignment_css():
    return tracks.stylesheet

@templet.stringfunction
def pprint_seq(seq, container=True):
    """
    ${container and '<div class="pprint_seq">' or ""}
    ${['<span class="%s">%s</span>' % (x,x) for x in seq]}    
    ${container and '</div>' or ''}
    """

@templet.stringfunction
def pprint_seq_css():
    """
    div.pprint_seq {
    margin: 1em 3em;
    border: 1px solid black;
    word-wrap: break-word;
    padding: 0.25em;
    }

    span.A { color: green; }
    span.T { color: red; }
    span.G { color: black; }
    span.C { color: blue; }
    """

def render_alignment(assembly, ab1dict1, ab1dict2):
    t = tracks.TrackSet()

    read1_offset, read1_sequence = assembly['read1']
    read2_offset, read2_sequence = assembly['read2']
    read1_confs = tracks.regap(read1_sequence, ab1dict1['confidences'])
    read2_confs = tracks.regap(read2_sequence, tracks.revcomp(ab1dict2['confidences']))
    read1_traces = tracks.regap(read1_sequence, ab1dict1['traces'])
    read2_traces = tracks.regap(read2_sequence, tracks.revcomp(ab1dict2['traces']))

    t.extend([
              tracks.TrackEntry('read 1 traces', read1_offset, read1_traces),
              tracks.TrackEntry('read 1 confidences', read1_offset, read1_confs),
              tracks.TrackEntry('read 1 bases', read1_offset, read1_sequence),
              tracks.TrackEntry('read 2 traces', read2_offset, read2_traces),
              tracks.TrackEntry('read 2 confidences', read2_offset, read2_confs),
              tracks.TrackEntry('read 2 bases', read2_offset, read2_sequence)])

    assert assembly['reference'] != None
    reference_offset, reference_sequence = assembly['reference']
    t.append(tracks.TrackEntry('reference', reference_offset, reference_sequence))

    return tracks.render(t)

# NCBI BLAST returns a closed interval for start and end, not a half open one, so end-start = length-1
def overlap_bar(hsp, query_length):
    template = """<div style="background-color: %s; width: %s%%; margin-left: %s%%;">%s</div>"""
    if hsp.score >= 200:
        color = "#f00"
    elif hsp.score >= 80 and hsp.score < 200:
        color = "#f0f"
    elif hsp.score >= 50 and hsp.score < 80:
        color = "#0f0"
    elif hsp.score >= 40 and hsp.score < 50:
        color = "#00f"
    else: # hsp.XSscore < 40:
        color = "#000"
    percid = hsp.identities / float(hsp.align_length)
    # NCBI BLAST returns a closed interval for start and end, not a
    # half open one, so end-start = length-1
    sbjct_right = hsp.query_end
    sbjct_left = hsp.query_start
    width = 100*(sbjct_right - sbjct_left + 1)/float(query_length) # in percent
    offset = 100*sbjct_left / float(query_length)
    return template % (color, width, offset, pprint_percent(percid))

def pprint_int(n):
    locale.setlocale(locale.LC_ALL, '')
    return locale.format("%d", n, grouping=True)

def pprint_sci(x):
    locale.setlocale(locale.LC_ALL, '')
    exponent = math.floor(math.log10(x))
    radix = x * 10**(-exponent)
    return "%1.1f" % radix + "&times;10<sup>" + "%d"%exponent + "</sup>"

def pprint_percent(x):
    return "%.1f" % (100*x)

@templet.stringfunction
def render_hsp(hsp, query_length):
    """
    <ul class="stats">
      <li><span class="label">Score</span><span class="value">${str(hsp.score)} (E=${pprint_sci(hsp.expect)})</span></li>
      <li><span class="label">Coverage</span><span class="value">${str(hsp.align_length)}/${str(query_length)} query bases</span></li>
      <li><span class="label">Identities</span><span class="value">${str(hsp.identities)}/${str(hsp.align_length)} (${pprint_percent(hsp.identities/float(hsp.align_length))}%)</span></li>
      <li><span class="label">Gaps</span><span class="value">${hsp.gaps}/${hsp.align_length} (${pprint_percent(hsp.gaps/float(hsp.align_length))}%)</span></li>
    </ul>
    <span><div class="alignment">
      <p><span class="label">Query (${hsp.query_start}-${hsp.query_end})</span><span class="sequence">${pprint_seq(hsp.query, False)}</span></p>
      <p><span class="label">&nbsp;</span><span class="sequence">${hsp.match}</span></p>
      <p><span class="label">Sbjct (${hsp.sbjct_start}-${hsp.sbjct_end})</span><span class="sequence">${pprint_seq(hsp.sbjct, False)}</span></p>
    </div></span>
    """
    
@templet.stringfunction
def render_blast_alignment(alignment, position, query_length):
    """
    <div class="blast_result">
      <h3 onclick="toggle_visible('inner$position')"><div class="overlap_bars"><div></div>
        ${[overlap_bar(h, query_length) for h in alignment.hsps]}</div>
        <tt>${alignment.hit_id}</tt> ${alignment.hit_def} (&gt;gb|AE000511.1|</tt> Helicobacter pylori 26695, complete genome (${pprint_int(alignment.length)}bp)
      </h3>
      <div id="inner$position" class="hidden" onclick="toggle_visible('inner$position')">
        ${[render_hsp(h, query_length) for h in alignment.hsps]}
      </div>
    </div>
    """

def render_blast(blast_result):
    txt = ""
    for i,a in enumerate(blast_result.alignments):
        txt += render_blast_alignment(a, i, blast_result.query_length)
    return txt

@templet.stringfunction
def blast_css():
    """
    div.blast_result h3 { font-size: 100%; margin: 0; padding: 0; font-family: "Times New Roman", serif; white-space: nowrap; }
    tt { font-size: 140%; }
    ul.stats { display: block; width: 100%; list-style: none; margin: 0.25em; padding: 0; font-size: 1em; max-width: 60em; }
    ul.stats li { display: inline-block; width: 30%; }
    ul.stats span.label { display: inline-block; width: 34%; text-align: right; font-weight: bold; margin-right: 2%; background-color: #eee; }
    ul.stats span.value { display: inline-block; width: 62%; text-align: left; text-align: left; }

    div.overlap_bars { display: inline-block; width: 15%; height: 1em; margin-right: 1em; background-color: #bbb; }
    div.overlap_bars div { display: block; float: left; font-size: 0.9em; line-height: 1.11; vertical-align: middle; height: 100%; text-align: center; color: #fff; }
    div.alignment { white-space: nowrap; overflow-x: scroll; overflow-y: hidden; }
    div.alignment span.label { display: block; width: 10em; float: left; text-align: right; margin-right: 0.5em; background-color: #eee; }
    div.alignment span.sequence { font-family: monospace; font-size: 1.5em; }
    div.alignment p { margin: 0; padding: 0; line-height: 1; }
    div.hidden { display: none; }
    div.shown { display: block; margin-bottom: 1em; margin: 0.25em; }
    a { text-decoration: inherit; color: inherit; }
    """

@templet.stringfunction
def blast_javascript():
    """
    function toggle_visible(tgt_id) {
        var t = document.getElementById(tgt_id);
        t.className = t.className=='hidden' ? 'shown' : 'hidden';
    }
    """


def generate_report(lookup_fun, assembled_render, strandwise_render, post_generate_fun=lambda x: None):
    def f((workup, read1path, read2path)):
        read1 = ab1.read(read1path)
        read2 = ab1.read(read2path)
        assembly = contig.contig(read1['sequence'], read1['confidences'],
                                 tracks.revcomp(read2['sequence']), tracks.revcomp(read2['confidences']))
        if assembly['reference'] != None:
            v = lookup_fun(assembly['reference'][1], save_path=workup.path)
            body = assembled_render(workup, read1, read2, assembly, v)
            post_generate_fun(workup)
            return ('assembled', body)
        else:
            v1 = lookup_fun(read1['sequence'], save_path=workup.path)
            v2 = lookup_fun(read2['sequence'], save_path=workup.path)
            body = strandwise_render(workup, read1, read2, v1, v2)
            post_generate_fun(workup)
            return ('strandwise', body)
    return f

@templet.stringfunction
def assembly_tab(assembly, read1, read2):
    """
    <h2>Assembly aligned to reads</h2>
    ${render_alignment(assembly, read1, read2)}
    <h2>Assembled sequence</h2>
    ${pprint_seq(assembly['reference'][1])}
    """

def render_assembled(workup, read1, read2, assembly, blast_result):
    title = "%s %s (%s)" % (workup.workup, workup.pat_name, workup.amp_name)
    tabs =  collections.OrderedDict([('Assembly', assembly_tab(assembly, read1, read2)),
                                     ('BLAST', render_blast(blast_result))])

    return tabbed_page(title, alignment_css() + pprint_seq_css() + blast_css(), blast_javascript(), tabs)

@templet.stringfunction
def strandwise_tab(read1, read2):
    """
    <h2>Strand 1</h2>
    ${render_ab1(read1)}
    ${pprint_seq(read1['sequence'])}
    <h2>Strand 2</h2>
    ${render_ab1(read2)}
    ${pprint_seq(read2['sequence'])}
    """

def render_strandwise(workup, read1, read2, blast_result1, blast_result2):
    title = "%s %s (%s)" % (workup.workup, workup.pat_name, workup.amp_name)
    tabs =  collections.OrderedDict([('Assembly', strandwise_tab(read1, read2)),
                                     ('Strand 1 BLAST', render_blast(blast_result1)),
                                     ('Strand 2 BLAST', render_blast(blast_result2))])
    return tabbed_page(title, alignment_css() + pprint_seq_css() + blast_css(), blast_javascript(), tabs)
    
