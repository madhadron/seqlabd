import templet
import os
import time

@templet.stringfunction
def tab_li(i, text):
    """<li id="tab$i"><a href="javascript:show_tab('tab$i')">$text</a></li>"""

@templet.stringfunction
def pane_div(i, text):
    """<div class="tab" id="tab$i">$text</div>"""

@templet.stringfunction
def tabbed_page(title, additional_css, tabs):
    """
    <html><head>
    <title>$title</title>
    <script type="text/javascript">
    function map_children(fn,tgt){
        var arr=document.getElementById(tgt).getElementsByTagName('*');
        var l=arr.length;
        for(var i=0;i<l;i++){fn(arr[i]);}
    }
    function show_tab(to_show) {
        map_children(function(n) {
                         n.style.display = n.id==to_show ? "block" : "none";
                     }, "pane_container");
        map_children(function(n) {
                         n.className = n.id==to_show ? "active" : "";
                     }, "tab_container");
    }
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

