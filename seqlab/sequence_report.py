import templet
import json
import os
import re
import time
import locale
import math
import collections
import Bio.Blast.NCBIWWW
import Bio.Blast.NCBIXML

import assembly
import ab1
import contig

def blast_seq(seq, save_path, ncbi_db='nr', json_path=None, json_limit=None):
    """Submit *seq* to NCBI BLAST.

    *seq* should be a string or SeqRecord object. *ncbi_db* is the
    database to BLAST against. *save_path* is a path to save the XML
    returned by NCBI to.
    """
    h = Bio.Blast.NCBIWWW.qblast("blastn", ncbi_db, seq, alignments=700, descriptions=700)
    res = h.read()
    h.close()
    with open(save_path, 'w') as xh:
        xh.write(res)
    with open(save_path, 'r') as xh:
        records = list(Bio.Blast.NCBIXML.parse(xh))
        hits = records[0]
        query_length = hits.query_length
        hits_for_json = [{'hit_id': h.hit_id,
                          'hit_def': h.hit_def,
                          'length': h.length,
                          'query_length': query_length,
                          'hsps': [{'score': hs.score,
                                    'expect': hs.expect,
                                    'align_length': hs.align_length,
                                    'identities': hs.identities,
                                    'gaps': hs.gaps,
                                    'query_start': hs.query_start,
                                    'query_end': hs.query_end,
                                    'sbjct_start': hs.sbjct_start,
                                    'sbjct_end': hs.sbjct_end,
                                    'query': hs.query,
                                    'sbjct': hs.sbjct,
                                    'match': hs.match}
                                   for hs in h.hsps]}
                         for h in hits.alignments]
        if json_path:
            with open(json_path, 'w') as jsonout:
                json.dump(hits_for_json[:json_limit], jsonout)
        return hits_for_json


# Pattern to filter out ill classified BLAST results
unclassified_regex = re.compile(r'' + r'|'.join(['-like',
                                              'Taxon',
                                              'saltmarsh',
                                              'acidophile',
                                              'actinobacterium',
                                              'aerobic',
                                              'cyanobacterium',
                                              'Chloroplast',
                                              'clone',
                                              'Cloning',
                                              'epibiont',
                                              'eubacterium',
                                              r'\b[Gg]roup\b',
                                              'halophilic',
                                              'hydrothermal',
                                              'isolate',
                                              'marine',
                                              'methanotroph',
                                              'microorganism',
                                              'mollicute',
                                              'pathogen',
                                              'phytoplasma',
                                              'Phytoplasma',
                                              'proteobacterium',
                                              'putative',
                                              'species',
                                              'strain',
                                              'symbiont',
                                              'unicellular',
                                              'unidentified',
                                              'unknown',
                                              'vector\b',
                                              'vent',
                                              r'\b[Bb]acteri(um|a)',
                                              r'sp\.',
                                              r'str\.']))


def is_unclassified(s):
    """Is string *s* containining and organism description ill posed?"""
    return re.search(unclassified_regex, s) and True or False


# workup should be a dictionary with the keys "accession", "workup",
# "pat_name", "amp_name", "seq_key", as selected directly from the
# workups view of the database. In production, it will be found in a
# JSON file written in the directory.
def generate_report(lookup_fun, assembled_render, strandwise_render):
    def f((workup, read1path, read2path), omit_blast=False):
        read1 = ab1.read(read1path)
        read2 = ab1.read(read2path)
        assembly = contig.assemble(read1['sequence'], read1['confidences'], read1['traces'],
                                   read2['sequence'], read2['confidences'], read2['traces'])
        if 'contig' in assembly:
            if not omit_blast:
                v = lookup_fun(''.join(assembly['contig'].values), save_path=os.path.join(workup['path'], 'blast.xml'),
                               save_json=os.path.join(workup['path'], 'blast.json'))
                body = assembled_render(workup, assembly, v, omit_blast=False)
            else:
                body = assembled_render(workup, assembly, None, omit_blast=True)
            return ('assembled', body)
        else:
            if not omit_blast:
                v1 = lookup_fun(''.join(assembly['bases 1'].values), save_path=workup['path'],
                                save_json=os.path.join(workup['path'], 'blast.json'))
                v2 = lookup_fun(''.join(assembly['bases 2'].values), save_path=workup['path'],
                                save_json=os.path.join(workup['path'], 'blast.json'))
                body = strandwise_render(workup, assembly, v1, v2, omit_blast=False)
            else:
                body = strandwise_render(workup, assembly, None, None, omit_blast=True)
            return ('strandwise', body)
    return f

@templet.stringfunction
def tab_li(i, text):
    """<li id="tab$i"><a href="javascript:show_tab('tab$i')">$text</a></li>"""

@templet.stringfunction
def pane_div(i, text):
    """<div class="hiddentab" id="tab$i">$text</div>"""

def description(metadata):
    description = ""
    if metadata['specimen_description']:
        description += " on %s, ordered tests:" % metadata['specimen_description']
        if metadata['specimen_category']:
            description += " (%s)" % metadata['specimen_category']
        description += ":"
    description += "<ul>"
    description += "".join(["<li>%s%s</li>" % (y if y is not None else "",
                                               " (%s)" % x if x is not None else "?")
                            for x,y in metadata['tests']])
    description += "</ul>"
    return description

def title(workup):
    return "%s %s (%s)" % (workup['accession'], workup['pat_name'], workup['amp_name'])


@templet.stringfunction
def tabbed_page(metadata, additional_css, additional_javascript, tabs):
    """
    <!DOCTYPE html>
    <html><head>
    <title>${title(metadata)}</title>
    <style>
    $additional_css
    * { margin: 0; padding: 0; }
    div.tab { display: none; }
    li { margin-left: 1em; padding-left: 0.5em; list-style: dot; }
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
    <h1>${title(metadata)}</h1>

    <p><b>${metadata['date']}</b>: ${description(metadata)}</p>

    <ul id="tab_container">${[tab_li(i,k) for i,k in enumerate(tabs.keys())]}</ul>
    <div id="pane_container">${[pane_div(i,v) for i,v in enumerate(tabs.values())]}</div>
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
    </body></html>
    """


def alignment_css():
    return assembly.css

def pprint_seq(seq, container=True, matches=None):
    if not(matches):
        matches = [True for x in seq]
    body = ""
    for x,m in zip(seq,matches):
        if not(m):
            wrapper = """<span class="mismatch">%s</span>"""
        else:
            wrapper = """<span class="match">%s</span>"""
        if x == ' ':
            bclass = 'gap'
            btxt = '&nbsp'
        elif x == '|':
            bclass = 'pipe'
            btxt = '|'
        else:
            bclass = x
            btxt = x
        body += wrapper % ("""<span class="%s">%s</span>""" % (bclass, btxt),)
    txt = (container and """<div class="pprint_seq">\n%s\n</div>""" or "%s") % body
    return txt

@templet.stringfunction
def pprint_seq_css():
    """
    div.pprint_seq {
    margin: 1em 3em;
    border: 1px solid black;
    word-wrap: break-word;
    padding: 0.25em;
    }
    span.mismatch { background-color: #ffaaaa; }
    span.match { background-color: #fff; }

    span.A { color: green; }
    span.T { color: red; }
    span.G { color: black; }
    span.C { color: blue; }
    """

@templet.stringfunction
def pprint_seq_javascript():
    """
updateCSS = function(selector, styles) {
  var rule, sheet, style, value, _i, _len, _ref, _results;
  _ref = document.styleSheets;
  _results = [];
  for (_i = 0, _len = _ref.length; _i < _len; _i++) {
    sheet = _ref[_i];
    _results.push((function() {
      var _j, _len2, _ref2, _results2;
      _ref2 = sheet.cssRules || sheet.rules || [];
      _results2 = [];
      for (_j = 0, _len2 = _ref2.length; _j < _len2; _j++) {
        rule = _ref2[_j];
        if (rule.selectorText === selector) {
          _results2.push((function() {
            var _results3;
            _results3 = [];
            for (style in styles) {
              value = styles[style];
              _results3.push(rule.style[style] = value);
            }
            return _results3;
          })());
        } else {
          _results2.push(void 0);
        }
      }
      return _results2;
    })());
  }
  return _results;
};

    function match_display_from_checkbox(checkbox_id) {
        checkbox = document.getElementById(checkbox_id);
        updateCSS('span.match', {'display': checkbox.checked ? "none" : "inline"});
    }
"""


# NCBI BLAST returns a closed interval for start and end, not a half open one, so end-start = length-1
def overlap_bar(hsp, query_length):
    template = """<div style="background-color: %s; width: %s%%; margin-left: %s%%;">%s</div>"""
    if hsp['score'] >= 200:
        color = "#f00"
    elif hsp['score'] >= 80 and hsp['score'] < 200:
        color = "#f0f"
    elif hsp['score'] >= 50 and hsp['score'] < 80:
        color = "#0f0"
    elif hsp['score'] >= 40 and hsp['score'] < 50:
        color = "#00f"
    else: # hsp['score'] < 40:
        color = "#000"
    percid = hsp['identities'] / float(hsp['align_length'])
    # NCBI BLAST returns a closed interval for start and end, not a
    # half open one, so end-start = length-1
    sbjct_right = hsp['query_end']
    sbjct_left = hsp['query_start']
    width = 100*(sbjct_right - sbjct_left + 1)/float(query_length) # in percent
    offset = 100*sbjct_left / float(query_length)
    return template % (color, width, offset, pprint_percent(percid))

def pprint_int(n):
    locale.setlocale(locale.LC_ALL, '')
    return locale.format("%d", n, grouping=True)

def pprint_sci(x):
    if x == 0:
        return "0"
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
      <li><span class="label">Score</span><span class="value">${str(hsp['score'])} (E=${pprint_sci(hsp['expect'])})</span></li>
      <li><span class="label">Coverage</span><span class="value">${str(hsp['align_length'])}/${str(query_length)} query bases</span></li>
      <li><span class="label">Identities</span><span class="value">${str(hsp['identities'])}/${str(hsp['align_length'])} (${pprint_percent(hsp['identities']/float(hsp['align_length']))}%)</span></li>
      <li><span class="label">Gaps</span><span class="value">${hsp['gaps']}/${hsp['align_length']} (${pprint_percent(hsp['gaps']/float(hsp['align_length']))}%)</span></li>
    </ul>
    <span><div class="alignment">
      <p><span class="label">Query (${hsp['query_start']}-${hsp['query_end']})</span>
         <span class="sequence">${pprint_seq(hsp['query'], False, 
                                             [x==y for x,y in zip(hsp['query'], hsp['sbjct'])])}</span></p>
      <p><span class="label">&nbsp;</span>
         <span class="sequence">${pprint_seq(hsp['match'], False,
                                             [x==y for x,y in zip(hsp['query'],hsp['sbjct'])])}</span></p>
      <p><span class="label">Sbjct (${hsp['sbjct_start']}-${hsp['sbjct_end']})</span>
         <span class="sequence">${pprint_seq(hsp['sbjct'], False, 
                                             [x==y for x,y in zip(hsp['query'],hsp['sbjct'])])}</span></p>
    </div></span>
    """
    
@templet.stringfunction
def render_blast_alignment(alignment, hsp_idx, position, query_length, hidden=True):
    """
    ${is_unclassified(alignment['hit_def']) and '<div class="ill-annotated">' or ''}
    <div class="blast_result">
      <h3 onclick="toggle_visible('inner$position-$hsp_idx')"><div class="overlap_bars"><div></div>
        ${overlap_bar(alignment['hsps'][hsp_idx], alignment['query_length'])}</div>
        <tt>${alignment['hit_id']}</tt> ${alignment['hit_def']} (${pprint_int(alignment['length'])}bp)
      </h3>
      <div id="inner$position-$hsp_idx" class="${"hidden" if hidden else ""}" onclick="toggle_visible('inner$position-$hsp_idx')">
        ${render_hsp(alignment['hsps'][hsp_idx], alignment['query_length'])}
      </div>
    </div>
    ${is_unclassified(alignment['hit_def']) and '</div>' or ''}
    """

@templet.stringfunction
def control_bar(keyname):
    """
    <div class="controlbar">
      <input type="checkbox" id="ill_annotated_${keyname}_checkbox" onClick="toggle_ill_annotated('${keyname}')" /><label for="ill_annotated_${keyname}_checkbox">Show ill annotated hits</label>
      <input type="checkbox" id="hide_matches_$keyname" onClick="match_display_from_checkbox('hide_matches_$keyname')" />
      <label for="hide_matches_$keyname">Show only mismatches in alignments</label>
    </div>
    """
    
def render_blast(blast_result, keyname):
    txt = control_bar(keyname)
    txt += """<div id="%s" class="blast_tab">""" % (keyname,)
    for i,a in enumerate(blast_result):
        # Only showing top HSP instead of all
        txt += render_blast_alignment(a, 0, i, a['query_length'])
        # for j,h in enumerate(a.hsps):
        #     txt += render_blast_alignment(a, j, i, blast_result.query_length)
    txt += "\n</div>"
    return txt

@templet.stringfunction
def blast_css():
    """
    div.blast_result { cursor: pointer; background-color: white; } 
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
    .hidden { display: none !important; }
    div.shown { display: block; margin-bottom: 1em; margin: 0.25em; }
    a { text-decoration: inherit; color: inherit; }
    div.ill-annotated { display: none; }
    div.visible-ill-annotated { display: block; }
    div.controlbar { position: fixed; bottom: 0; left: 0; width: 100%; height: 2em; color: #fff; background-color: #444; padding: 0.5em; }
    div.blast_tab { margin-bottom: 2em; }
    """

@templet.stringfunction
def blast_javascript():
    """
    function toggle_visible(tgt_id) {
        var t = document.getElementById(tgt_id);
        t.className = t.className=='hidden' ? 'shown' : 'hidden';
    }
    function toggle_ill_annotated(tgt_id) {
        var checkbox = document.getElementById('ill_annotated_' + tgt_id + '_checkbox');
        var oldclass = checkbox.checked ? "ill-annotated" : "visible-ill-annotated";
        var newclass = checkbox.checked ? "visible-ill-annotated" : "ill-annotated";
        map_children(function(n) {
                         if (n.className == oldclass) {
                             n.className = newclass;
                         }
                     }, tgt_id);
    }
    """



@templet.stringfunction
def assembly_tab(assem):
    """
    <h2>Assembly aligned to reads</h2>
    ${assembly.renderassembly(assem)}
    <h2>Assembled sequence</h2>
    ${pprint_seq(''.join([x for x in assem['contig']]))}
    """

def render_assembled(workup, assembly, blast_result, omit_blast=False):
    if omit_blast:
        tabs =  collections.OrderedDict([('Assembly', assembly_tab(assembly))])
    else:
        tabs =  collections.OrderedDict([('Assembly', assembly_tab(assembly)),
                                         ('BLAST', render_blast(blast_result, 'assembled'))])
    return tabbed_page(workup, alignment_css() + pprint_seq_css() + ("" if omit_blast else blast_css()),
                       pprint_seq_javascript() + ("" if omit_blast else blast_javascript()), tabs)

@templet.stringfunction
def strandwise_tab(assem):
    """
    <h2>Unassembled strands</h2>
    ${assembly.renderassembly(assem)}
    <h2>Strand 1</h2>
    ${pprint_seq(''.join([x for x in assem['bases 1']]))}
    <h2> Strand 2</h2>
    ${pprint_seq(''.join([x for x in assem['bases 2']]))}
    """

def render_strandwise(workup, assembly, blast_result1, blast_result2, omit_blast=False):
    if not omit_blast:
        tabs =  collections.OrderedDict([('Assembly', strandwise_tab(assembly)),
                                         ('Strand 1 BLAST', render_blast(blast_result1, 'strand1')),
                                         ('Strand 2 BLAST', render_blast(blast_result2, 'strand2'))])
    else:
        tabs =  collections.OrderedDict([('Assembly', strandwise_tab(assembly))])
    return tabbed_page(workup, alignment_css() + pprint_seq_css() + (blast_css() if render_blast else ""),
                       pprint_seq_javascript() + (blast_javascript() if render_blast else ""), tabs)
    

sequence_report = generate_report(blast_seq, render_assembled, render_strandwise)

