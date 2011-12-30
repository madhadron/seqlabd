import templet

@templet.stringfunction
def tab_li(i, text):
    """<li id="tab$i"><a href="javascript:show_tab('tab$i')">$text</a></li>"""

@templet.stringfunction
def pane_div(i, text):
    """<div class="tab" id="tab$i">$text</div>"""

@templet.stringfunction
def tabbed_page(additional_css, tabs):
    """
    <html><head><script type="text/javascript">
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
    <h1>WA08223 Calvert, Samuel Jameson (16S)</h1>

    <ul id="tab_container">${[tab_li(i,k) for i,k in enumerate(tabs.keys())]}</ul>
    <div id="pane_container">${[pane_div(i,v) for i,v in enumerate(tabs.values())]}</div>
    </body></html>
    """

if __name__=='__main__':
    print tabbed_page('', {'Boris':'Boris!', 'Hilda':'Hi there!'})
