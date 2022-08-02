# -*- coding: UTF-8 -*-
from rdflib import Graph
from rdflib import URIRef, Literal
from rdflib.plugins.sparql import prepareQuery
import os
import json
from qgis.core import Qgis,QgsTask, QgsMessageLog
import sys

from ..layerutils import LayerUtils
from ..sparqlutils import SPARQLUtils

startscripts = """var namespaces={"rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","xsd":"http://www.w3.org/2001/XMLSchema#","geo":"http://www.opengis.net/ont/geosparql#","rdfs":"http://www.w3.org/2000/01/rdf-schema#","owl":"http://www.w3.org/2002/07/owl#","dc":"http://purl.org/dc/terms/","skos":"http://www.w3.org/2004/02/skos/core#"}
var annotationnamespaces=["http://www.w3.org/2004/02/skos/core#","http://www.w3.org/2000/01/rdf-schema#","http://purl.org/dc/terms/"]
var geoproperties={
                   "http://www.opengis.net/ont/geosparql#asWKT":"DatatypeProperty",
                   "http://www.opengis.net/ont/geosparql#asGML": "DatatypeProperty",
                   "http://www.opengis.net/ont/geosparql#asKML": "DatatypeProperty",
                   "http://www.opengis.net/ont/geosparql#asGeoJSON": "DatatypeProperty",
                   "http://www.opengis.net/ont/geosparql#hasGeometry": "ObjectProperty",
                   "http://www.opengis.net/ont/geosparql#hasDefaultGeometry": "ObjectProperty",
                   "http://www.w3.org/2003/01/geo/wgs84_pos#geometry": "ObjectProperty",
                   "http://www.georss.org/georss/point": "DatatypeProperty",
                   "http://www.w3.org/2006/vcard/ns#hasGeo": "ObjectProperty",
                   "http://www.w3.org/2003/01/geo/wgs84_pos#lat":"DatatypeProperty",
                   "http://www.w3.org/2003/01/geo/wgs84_pos#long": "DatatypeProperty",
                   "http://www.semanticweb.org/ontologies/2015/1/EPNet-ONTOP_Ontology#hasLatitude": "DatatypeProperty",
                   "http://www.semanticweb.org/ontologies/2015/1/EPNet-ONTOP_Ontology#hasLongitude": "DatatypeProperty",
                   "http://schema.org/geo": "ObjectProperty",
                   "http://schema.org/polygon": "DatatypeProperty",
                   "https://schema.org/geo": "ObjectProperty",
                   "https://schema.org/polygon": "DatatypeProperty",
                   "http://geovocab.org/geometry#geometry": "ObjectProperty",
                   "http://www.w3.org/ns/locn#geometry": "ObjectProperty",
                   "http://rdfs.co/juso/geometry": "ObjectProperty",
                   "http://www.wikidata.org/prop/direct/P625":"DatatypeProperty",
                   "https://database.factgrid.de/prop/direct/P48": "DatatypeProperty",
                   "http://database.factgrid.de/prop/direct/P48":"DatatypeProperty",
                   "http://www.wikidata.org/prop/direct/P3896": "DatatypeProperty"
}

  var baseurl="{{baseurl}}"
  $( function() {
    var availableTags = Object.keys(search)
    $( "#search" ).autocomplete({
      source: availableTags
    });
    console.log(availableTags)
    setupJSTree()
  } );

function openNav() {
  document.getElementById("mySidenav").style.width = "400px";
}

function closeNav() {
  document.getElementById("mySidenav").style.width = "0";
}

function rewriteLink(thelink){
    console.log(thelink)
    if(thelink==null){
        rest=search[document.getElementById('search').value].replace(baseurl,"")
    }else{
        rest=thelink.replace(baseurl,"")
    }
    console.log(rest)
    count=0
    if(!indexpage){
        count=rest.split("/").length
    }
    console.log(count)
    counter=0
    while(counter<count){
        rest="../"+rest
        counter+=1
    }
    rest+="/index.html"
    console.log(rest)
    return rest
}

function followLink(thelink=null){
    rest=rewriteLink(thelink)
    location.href=rest
}

function changeDefLink(){
	$('#formatlink').attr('href',definitionlinks[$('#format').val()]);
}

function changeDefLink2(){
	$('#formatlink2').attr('href',definitionlinks[$('#format2').val()]);
}

var definitionlinks={
"covjson":"https://covjson.org",
"csv":"https://tools.ietf.org/html/rfc4180",
"cipher":"https://neo4j.com/docs/cypher-manual/current/",
"esrijson":"https://doc.arcgis.com/de/iot/ingest/esrijson.htm",
"geohash":"http://geohash.org",
"json":"https://geojson.org",
"gdf":"https://www.cs.nmsu.edu/~joemsong/software/ChiNet/GDF.pdf",
"geojsonld":"http://geojson.org/geojson-ld/",
"geojsonseq":"https://tools.ietf.org/html/rfc8142",
"geouri":"https://tools.ietf.org/html/rfc5870",
"gexf":"https://gephi.org/gexf/format/",
"gml":"https://www.ogc.org/standards/gml",
"gml2":"https://gephi.org/users/supported-graph-formats/gml-format/",
"gpx":"https://www.topografix.com/gpx.asp",
"graphml":"http://graphml.graphdrawing.org",
"gxl":"http://www.gupro.de/GXL/Introduction/intro.html",
"hdt":"https://www.w3.org/Submission/2011/03/",
"hextuples":"https://github.com/ontola/hextuples",
"html":"https://html.spec.whatwg.org",
"jsonld":"https://json-ld.org",
"jsonn":"",
"jsonp":"http://jsonp.eu",
"jsonseq":"https://tools.ietf.org/html/rfc7464",
"kml":"https://www.ogc.org/standards/kml",
"latlon":"",
"mapml":"https://maps4html.org/MapML/spec/",
"mvt":"https://docs.mapbox.com/vector-tiles/reference/",
"n3":"https://www.w3.org/TeamSubmission/n3/",
"nq":"https://www.w3.org/TR/n-quads/",
"nt":"https://www.w3.org/TR/n-triples/",
"olc":"https://github.com/google/open-location-code/blob/master/docs/specification.md",
"osm":"https://wiki.openstreetmap.org/wiki/OSM_XML",
"osmlink":"",
"rdfxml":"https://www.w3.org/TR/rdf-syntax-grammar/",
"rdfjson":"https://www.w3.org/TR/rdf-json/",
"rt":"https://afs.github.io/rdf-thrift/rdf-binary-thrift.html",
"svg":"https://www.w3.org/TR/SVG11/",
"tgf":"https://docs.yworks.com/yfiles/doc/developers-guide/tgf.html",
"tlp":"https://tulip.labri.fr/TulipDrupal/?q=tlp-file-format",
"trig":"https://www.w3.org/TR/trig/",
"trix":"https://www.hpl.hp.com/techreports/2004/HPL-2004-56.html",
"ttl":"https://www.w3.org/TR/turtle/",
"wkb":"https://www.iso.org/standard/40114.html",
"wkt":"https://www.iso.org/standard/40114.html",
"xls":"http://www.openoffice.org/sc/excelfileformat.pdf",
"xlsx":"http://www.openoffice.org/sc/excelfileformat.pdf",
"xyz":"https://gdal.org/drivers/raster/xyz.html",
"yaml":"https://yaml.org"
}

function shortenURI(uri){
	prefix=""
	if(typeof(uri)!="undefined"){
		for(namespace in namespaces){
			if(uri.includes(namespaces[namespace])){
				prefix=namespace+":"
				break
			}
		}
	}
	if(typeof(uri)!= "undefined" && uri.includes("#")){
		return prefix+uri.substring(uri.lastIndexOf('#')+1)
	}
	if(typeof(uri)!= "undefined" && uri.includes("/")){
		return prefix+uri.substring(uri.lastIndexOf("/")+1)
	}
	return uri
}

function labelFromURI(uri,label){
        if(uri.includes("#")){
        	prefix=uri.substring(0,uri.lastIndexOf('#')-1)
        	if(label!=null){
        		return label+" ("+prefix.substring(prefix.lastIndexOf("/")+1)+":"+uri.substring(uri.lastIndexOf('#')+1)+")"
        	
        	}else{
				return uri.substring(uri.lastIndexOf('#')+1)+" ("+prefix.substring(uri.lastIndexOf("/")+1)+":"+uri.substring(uri.lastIndexOf('#')+1)+")"        	
        	}
       	}
        if(uri.includes("/")){
            prefix=uri.substring(0,uri.lastIndexOf('/')-1)
            if(label!=null){
            	return label+" ("+prefix.substring(prefix.lastIndexOf("/")+1)+":"+uri.substring(uri.lastIndexOf('/')+1)+")" 
            }else{
        		return uri.substring(uri.lastIndexOf('/')+1)+" ("+prefix.substring(uri.lastIndexOf("/")+1)+":"+uri.substring(uri.lastIndexOf('/')+1)+")"
            }
       	}
        return uri
}

function formatHTMLTableForResult(result,nodeicon){
    dialogcontent=""
    dialogcontent="<h3><img src=\\""+nodeicon+"\\" height=\\"25\\" width=\\"25\\" alt=\\"Instance\\"/><a href=\\""+nodeid.replace('/index.json','/index.html')+"\\" target=\\"_blank\\"> "+nodelabel+"</a></h3><table border=1 id=dataschematable><thead><tr><th>Type</th><th>Relation</th><th>Value</th></tr></thead><tbody>"
    for(res in result){
        dialogcontent+="<tr>"
        if(res in geoproperties && geoproperties[res]=="ObjectProperty"){
            dialogcontent+="<td><img src=\\"https://raw.githubusercontent.com/i3mainz/geopubby/master/public/icons/geoobjectproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Geo Object Property\\"/>Geo Object Property</td>"
        }else if((result[res][0]+"").startsWith("http")){
            dialogcontent+="<td><img src=\\"https://raw.githubusercontent.com/i3mainz/geopubby/master/public/icons/objectproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Object Property\\"/>Object Property</td>"
        }else{
            finished=false
            for(ns in annotationnamespaces){
                if(res.includes(annotationnamespaces[ns])){
                    dialogcontent+="<td><img src=\\"https://raw.githubusercontent.com/i3mainz/geopubby/master/public/icons/annotationproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Annotation Property\\"/>Annotation Property</td>"
                    finished=true
                }
            }
            if(!finished && res in geoproperties && geoproperties[res]=="DatatypeProperty"){
                dialogcontent+="<td><img src=\\"https://raw.githubusercontent.com/i3mainz/geopubby/master/public/icons/geodatatypeproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Datatype Property\\"/>Geo Datatype Property</td>"
            }else if(!finished){
                dialogcontent+="<td><img src=\\"https://raw.githubusercontent.com/i3mainz/geopubby/master/public/icons/datatypeproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Datatype Property\\"/>Datatype Property</td>"
            }
        }    
        dialogcontent+="<td><a href=\\""+res+"\\" target=\\"_blank\\">"+shortenURI(res)+"</a></td>"
        if(Array.isArray(result[res]) && result[res].length>1){
            dialogcontent+="<td><ul>"
            for(resitem of result[res]){
                if((resitem+"").startsWith("http")){
                    dialogcontent+="<li><a href=\\""+rewriteLink(resitem)+"\\" target=\\"_blank\\">"+shortenURI(resitem)+"</a></li>"
                }else{
                    dialogcontent+="<li>"+resitem+"</li>"
                }
            }
            dialogcontent+="</ul></td>"
        }else if((result[res][0]+"").startsWith("http")){
            dialogcontent+="<td><a href=\\""+rewriteLink(result[res]+"")+"\\" target=\\"_blank\\">"+shortenURI(result[res]+"")+"</a></td>"
        }else{
            dialogcontent+="<td>"+result[res]+"</td>"
        }
        dialogcontent+="</tr>"
    }
    dialogcontent+="</tbody></table>"
    dialogcontent+="<button id=\\"closebutton\\" onclick='document.getElementById(\\"dataschemadialog\\").close()'>Close</button>"
    return dialogcontent
}

function getDataSchemaDialog(node){
     nodeid=rewriteLink(node.id).replace(".html",".json")
     nodelabel=node.text
     nodetype=node.type
     nodeicon=node.icon
     props={}
     if("data" in node){
        props=node.data
     }
     console.log(nodetype)
     if(nodetype=="class" || nodetype=="geoclass"){
        console.log(props)
        dialogcontent=formatHTMLTableForResult(props,nodeicon)
        document.getElementById("dataschemadialog").innerHTML=dialogcontent
        $('#dataschematable').DataTable();
        document.getElementById("dataschemadialog").showModal();
     }else{
         $.getJSON(nodeid, function(result){
            dialogcontent=formatHTMLTableForResult(result,nodeicon)
            document.getElementById("dataschemadialog").innerHTML=dialogcontent
            $('#dataschematable').DataTable();
            document.getElementById("dataschemadialog").showModal();
          });
    }
}

function setupJSTree(){
    console.log("setupJSTree")
    tree["contextmenu"]={}
    tree["core"]["check_callback"]=true
    tree["sort"]=function(a, b) {
        a1 = this.get_node(a);
        b1 = this.get_node(b);
        if (a1.icon == b1.icon){
            return (a1.text > b1.text) ? 1 : -1;
        } else {
            return (a1.icon > b1.icon) ? 1 : -1;
        }
    }
    tree["contextmenu"]["items"]=function (node) {
        return {
            "lookupdefinition": {
                "separator_before": false,
                "separator_after": false,
                "label": "Lookup definition",
                "icon": "https://github.com/i3mainz/geopubby/raw/master/public/icons/searchclass.png",
                "action": function (obj) {
                    newlink=rewriteLink(node.id)
                    var win = window.open(newlink, '_blank');
                    win.focus();
                }
            }, 
            "copyuriclipboard":{
                "separator_before": false,
                "separator_after": false,
                "label": "Copy URI to clipboard",
                "icon": "https://github.com/i3mainz/geopubby/raw/master/public/icons/classlink.png",
                "action":function(obj){
                    copyText=node.id
                    navigator.clipboard.writeText(copyText);
                }    
            },
            "loaddataschema": {
                "separator_before": false,
                "separator_after": false,
                "icon":"https://github.com/i3mainz/geopubby/raw/master/public/icons/classschema.png",
                "label": "Load dataschema for class",
                "action": function (obj) {
                    console.log(node)
                    console.log(node.id)
                    console.log(baseurl)
                    if(node.id.includes(baseurl)){
                        getDataSchemaDialog(node) 
                    }else if(node.type=="class" || node.type=="geoclass"){
                        getDataSchemaDialog(node) 
                    }                                         
                }
            }
        };
    }
    $('#jstree').jstree(tree);
    $('#jstree').bind("dblclick.jstree", function (event) {
        var node = $(event.target).closest("li");
        var data = node[0].id
        if(data.includes(baseurl)){
            followLink(data)
        }else{
            window.open(data, '_blank');
        }
    });
    var to = false;
	$('#classsearch').keyup(function () {
        if(to) { clearTimeout(to); }
        to = setTimeout(function () {
            var v = $('#classsearch').val();
            $('#jstree').jstree(true).search(v,false,true);
        });
    });
}
"""

stylesheet = """
html { margin: 0; padding: 0; }
body { font-family: sans-serif; font-size: 80%; margin: 0; padding: 1.2em 2em; }
#rdficon { float: right; position: relative; top: -28px; }
#header { border-bottom: 2px solid #696; margin: 0 0 1.2em; padding: 0 0 0.3em; }
#footer { border-top: 2px solid #696; margin: 1.2em 0 0; padding: 0.3em 0 0; }
#homelink { display: inline; }
#homelink, #homelink a { color: #666; }
#homelink a { font-weight: bold; text-decoration: none; }
#homelink a:hover { color: red; text-decoration: underline; }
h1 { display: inline; font-weight: normal; font-size: 200%; margin: 0; text-align: left; }
h2 { font-weight: normal; font-size: 124%; margin: 1.2em 0 0.2em; }
.page-resource-uri { font-size: 116%; margin: 0.2em 0; }
.page-resource-uri a { color: #666; text-decoration: none; }
.page-resource-uri a:hover { color: red; text-decoration: underline; }
img { border: none; }
table.description { border-collapse: collapse; clear: left; font-size: 100%; margin: 0 0 1em; width: 100%; }
table.description th { background: white; text-align: left; }
table.description td, table.description th { line-height: 1.2em; padding: 0.3em 0.5em; vertical-align: top; }
table.description ul { margin: 0; padding-left: 1.4em; }
table.description li { list-style-position: outside; list-style-type: square; margin-left: 0; padding-left: 0; }
table.description .property-column { width: 13em; }
.ui-autocomplete {
    max-height: 100px;
    overflow-y: auto;
    /* prevent horizontal scrollbar */
    overflow-x: hidden;
  }
.uri { white-space: nowrap; }
.uri a, a.uri { text-decoration: none; }
.unbound { color: #888; }
table.description a small, .metadata-table a small  { font-size: 100%; color: #55a; }
table.description small, .metadata-table a small  { font-size: 100%; color: #666; }
table.description .property { white-space: nowrap; padding-right: 1.5em; }
h1, h2 { color: #810; }
body { background: #cec; }
table.description .container > td { background: #c0e2c0; padding: 0.2em 0.8em; }
table.description .even td { background: #d4f6d4; }
table.description .odd td { background: #f0fcf0; }
.image { background: white; float: left; margin: 0 1.5em 1.5em 0; padding: 2px; }
a.expander { text-decoration: none; }

.metadata-label {
	font-size: 100%;
	background: #f0fcf0;
	padding: 3px;
}

.metadata-table {
	font-size: 100%;
	border-left: 3px solid #f0fcf0;
	border-bottom: 3px solid #f0fcf0;
	border-right: 3px solid #f0fcf0;
	background: #d4f6d4;
	border-top: 0px solid none;
	margin: 0px;
}

.metadata-table td {
	padding: 3px;
}
body {
  font-family: "Lato", sans-serif;
}

.sidenav {
  height: 100%;
  width: 0;
  position: fixed;
  z-index: 1;
  top: 0;
  right: 0;
  background-color: #FFF;
  overflow-x: hidden;
  transition: 0.5s;
}

.sidenav a {
  text-decoration: none;
  font-size: 12px;
  color: #818181;
  transition: 0.3s;
}

.sidenav .closebtn {
  position: absolute;
  top: 0;
  right: 25px;
  font-size: 36px;
  margin-left: 50px;
}

#jstree {
	font-size: 12px;
	background-color:white;
	z-index: 2;
}

.jstree-contextmenu {
z-index: 10;
}

@media screen and (max-height: 450px) {
  .sidenav {padding-top: 15px;}
  .sidenav a {font-size: 18px;}
}"""

htmltemplate = """<html about=\"{{subject}}\"><head><title>{{toptitle}}</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.5.1/dist/leaflet.css" integrity="sha512-xwE/Az9zrjBIphAcBb3F6JVqxf46+CDLwfLMHloNu6KEQCAWi6HcDUbeOfBIptF7tcCzusKFjFw2yuvEpDL9wQ==" crossorigin="">
<link href='https://api.mapbox.com/mapbox.js/plugins/leaflet-fullscreen/v1.0.1/leaflet.fullscreen.css' rel='stylesheet' />
<link rel="stylesheet" type="text/css" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css"/>
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.12.1/css/jquery.dataTables.min.css"/>
<link rel="stylesheet" type="text/css" href="https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"/>
<link rel="stylesheet" href="https://code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.1.1/themes/default/style.min.css" />
<link rel="stylesheet" type="text/css" href="{{stylepath}}"/>
<script src="https://code.jquery.com/jquery-1.12.4.min.js"></script><script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
<script src="https://cdn.datatables.net/1.12.1/js/jquery.dataTables.min.js"></script>
<script src="{{scriptfolderpath}}"></script><script src="{{classtreefolderpath}}"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.3.12/jstree.min.js"></script>
<script type="text/javascript" src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.bundle.min.js"></script>
<script src="{{startscriptpath}}"></script></head>
<div id="mySidenav" class="sidenav" style="overflow:auto;">
  <a href="javascript:void(0)" class="closebtn" onclick="closeNav()">&times;</a>
  GeoClasses: <input type="checkbox" id="geoclasses"/><br/>
  Search:<input type="text" id="classsearch"><br/><div id="jstree"></div>
</div><script>var indexpage={{indexpage}}</script>
<body><div id="header"><h1 id="title">{{title}}</h1></div><div class="page-resource-uri"><a href="{{baseurl}}">{{baseurl}}</a> <b>powered by Static GeoPubby</b> generated using the <a style="color:blue;font-weight:bold" target="_blank" href="https://github.com/sparqlunicorn/sparqlunicornGoesGIS">SPARQLing Unicorn QGIS Plugin</a></div>
</div><div id="rdficon"><span style="font-size:30px;cursor:pointer" onclick="openNav()">&#9776;</span></div> <div class="search"><div class="ui-widget">Search: <input id="search" size="50"><button id="gotosearch" onclick="followLink()">Go</button><b>Download Options:</b>&nbsp;Format:<select id="format" onchange="changeDefLink()">	
{{exports}}
</select><a id="formatlink" href="#" target="_blank"><svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-info-circle-fill" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412l-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM8 5.5a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"/></svg></a>&nbsp;
<button id="downloadButton" onclick="download()">Download</button><br/></div></div><dialog id="dataschemadialog" width="500" height="500" modal="true"></dialog>
<div class="container-fluid"><div class="row-fluid" id="main-wrapper">
"""

imagestemplate="""
<div class="image">
<img src="{{image}}" style="max-width:500px;max-height:500px" alt="Depiction of $resource.label" title="Depiction of {{title}}" />
</div>
"""

nongeoexports="""
<option value="csv">Comma Separated Values (CSV)</option>
<option value="cipher">Cypher Neo4J (Cypher)</option>
<option value="exijson">EXI4JSON</option>
<option value="gdf">Graph Definition File (GDF)</option>
<option value="geojson">(Geo)JSON</option>
<option value="gexf">Graph Exchange XML Format (GEXF)</option>
<option value="gml2">Graph Modeling Language (GML)</option>
<option value="graphml">Graph Markup Language (GraphML)</option>
<option value="gxl">Graph Exchange Language (GXL)</option>
<option value="json">JSON-LD</option>
<option value="jsonp">JSONP</option>
<option value="hextuples">HexTuples RDF</option>
<option value="n3">Notation3 (N3)</option>
<option value="nq">NQuads (NQ)</option>
<option value="nt">NTriples (NT)</option>
<option value="rdfexi">RDF/EXI (EXI)</option>
<option value="rdfjson">RDF/JSON</option>
<option value="rt">RDF/Thrift (RT)</option>
<option value="xml">RDF/XML</option>
<option value="tgf">Trivial Graph Format (TGF)</option>
<option value="tlp">Tulip File Format (TLP)</option>
<option value="ttl">Turtle (TTL)</option>
<option value="trig">RDF TriG</option>
<option value="trix">Triples in XML (TriX)</option>
<option value="xls">MS Excel (XLS)</option>
<option value="xlsx">Excel Spreadsheet (XLSX)</option>
<option value="yaml">YAML Ain't Markup Language (YAML)</option>
"""

geoexports="""
<option value="covjson">CoverageJSON (COVJSON)</option>
<option value="csv">Comma Separated Values (CSV)</option>
<option value="cipher">Cypher Neo4J (Cypher)</option>
<option value="esrijson">ESRIJSON</option>
<option value="exijson">EXI4JSON</option>
<option value="gdf">Graph Definition File (GDF)</option>
<option value="geohash">GeoHash</option>
<option value="geojson">(Geo)JSON</option>
<option value="geojsonld">GeoJSON-LD</option>
<option value="geouri">GeoURI</option> 
<option value="gexf">Graph Exchange XML Format (GEXF)</option>
<option value="gml">Geography Markup Language (GML)</option>
<option value="gml2">Graph Modeling Language (GML)</option>
<option value="googlemapslink">Google Maps Link</option>
<option value="gpx">GPS Exchange Format (GPX)</option>
<option value="graphml">Graph Markup Language (GraphML)</option>
<option value="grass">GRASS Vector ASCII Format (GRASS)</option>
<option value="gxl">Graph Exchange Language (GXL)</option>
<option value="json">JSON-LD</option>
<option value="jsonp">JSONP</option>
<option value="hextuples">HexTuples RDF</option>
<option value="kml">Keyhole Markup Language (KML)</option>
<option value="latlontext">LatLonText</option>
<option value="mapml">Map Markup Language (MapML)</option>
<option value="n3">Notation3 (N3)</option>
<option value="nq">NQuads (NQ)</option>
<option value="nt">NTriples (NT)</option>
<option value="olc">Open Location Code (OLC)</option>
<option value="osmlink">OSM Link</option>
<option value="osm">OSM/XML (OSM)</option>
<option value="rdfexi">RDF/EXI (EXI)</option>
<option value="rdfjson">RDF/JSON</option>
<option value="rt">RDF/Thrift (RT)</option>
<option value="xml">RDF/XML</option>
<option value="svg">Scalable Vector Graphics (SVG)</option>
<option value="tgf">Trivial Graph Format (TGF)</option>
<option value="tlp">Tulip File Format (TLP)</option>
<option value="topojson">TopoJSON</option>
<option value="ttl">Turtle (TTL)</option>
<option value="trig">RDF TriG</option>
<option value="trix">Triples in XML (TriX)</option>
<option value="twkb">Tiny Well-Known-Binary (TWKB)</option>
<option value="wkb">Well-Known-Binary (WKB)</option>
<option value="wkt">Well-Known-Text (WKT)</option>
<option value="ewkt">Extended Well-Known-Text (EWKT)</option>
<option value="x3d">X3D Format (X3D)</option>
<option value="xls">MS Excel (XLS)</option>
<option value="xlsx">Excel Spreadsheet (XLSX)</option>
<option value="xyz">XYZ ASCII Format (XYZ)</option>
<option value="yaml">YAML Ain't Markup Language (YAML)</option>
"""

maptemplate="""
<script src="https://unpkg.com/leaflet@1.6.0/dist/leaflet.js"></script>
<script src="https://api.mapbox.com/mapbox.js/plugins/leaflet-fullscreen/v1.0.1/Leaflet.fullscreen.min.js"></script>
<script>
/*** Leaflet.geojsonCSS
 * @author Alexander Burtsev, http://burtsev.me, 2014
 * @license MIT*/
!function(a){a.L&&L.GeoJSON&&(L.GeoJSON.CSS=L.GeoJSON.extend({initialize:function(a,b){var c=L.extend({},b,{onEachFeature:function(a,c){b&&b.onEachFeature&&b.onEachFeature(a,c);var d=a.style,e=a.popupTemplate;d&&(c instanceof L.Marker?d.icon&&c.setIcon(L.icon(d.icon)):c.setStyle(d)),e&&a.properties&&c.bindPopup(L.Util.template(e,a.properties))}});L.setOptions(this,c),this._layers={},a&&this.addData(a)}}),L.geoJson.css=function(a,b){return new L.GeoJSON.CSS(a,b)})}(window,document);
</script>
<div id="map" style="height:500px;z-index: 0;"></div>
<script>
var overlayMaps={}
var map = L.map('map',{fullscreenControl: true,fullscreenControlOptions: {position: 'topleft'}}).setView([51.505, -0.09], 13);
	var layer=L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
	});
	var baseMaps = {
        "OSM": layer
	};
baseMaps["OSM"].addTo(map);
	L.control.scale({
	position: 'bottomright',
	imperial: false
	}).addTo(map);
	layercontrol=L.control.layers(baseMaps,overlayMaps).addTo(map);
	var bounds = L.latLngBounds([]);
	props={}
	var feature = {{myfeature}};
	layerr=L.geoJSON.css(feature,{
	pointToLayer: function(feature, latlng){
                  var greenIcon = new L.Icon({
                    iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-black.png',
                    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41],
                    popupAnchor: [1, -34],
                    shadowSize: [41, 41]
                });
                return L.marker(latlng, {icon: greenIcon});
    },onEachFeature: function (feature, layer) {
    var popup="<b>"
    if("label" in feature && feature.label!=""){
        popup+="<a href=\\""+feature.id+"\\" class=\\"footeruri\\" target=\\"_blank\\">"+feature.label+"</a></b><br/><ul>"
    }else{
        popup+="<a href=\\""+feature.id+"\\" class=\\"footeruri\\" target=\\"_blank\\">"+feature.id.substring(feature.id.lastIndexOf('/')+1)+"</a></b><br/><ul>"
    }
    for(prop in feature.properties){
        popup+="<li>"
        if(prop.startsWith("http")){
            popup+="<a href=\\""+prop+"\\" target=\\"_blank\\">"+prop.substring(prop.lastIndexOf('/')+1)+"</a>"
        }else{
            popup+=prop
        }
        popup+=" : "
        if(feature.properties[prop].length>1){
            popup+="<ul>"
            for(item of feature.properties[prop]){
                popup+="<li>"
                if((item+"").startsWith("http")){
                    popup+="<a href=\\""+item+"\\" target=\\"_blank\\">"+item.substring(item.lastIndexOf('/')+1)+"</a>"
                }else{
                    popup+=item
                }
                popup+="</li>"           
            }
            popup+="</ul>"
        }else if((feature.properties[prop][0]+"").startsWith("http")){
            popup+="<a href=\\""+rewriteLink(feature.properties[prop][0])+"\\" target=\\"_blank\\">"+feature.properties[prop][0].substring(feature.properties[prop][0].lastIndexOf('/')+1)+"</a>"
        }else{
            popup+=feature.properties[prop]
        }
        popup+="</li>"
    }
    popup+="</ul>"
    layer.bindPopup(popup)}})
	layerr.addTo(map)
    var layerBounds = layerr.getBounds();
    bounds.extend(layerBounds);
    map.fitBounds(bounds);
</script>
"""

htmlcommenttemplate="""<p class="comment"><b>Description:</b> {{comment}}</p>"""

htmltabletemplate="""
<table border=1 width=100% class=description><thead><tr><th>Property</th><th>Value</th></tr></thead><tbody>{{tablecontent}}</tbody></table>"""

htmlfooter="""<div id="footer"><div class="container-fluid"><b>Download Options:</b>&nbsp;Format:<select id="format" onchange="changeDefLink()">	
{{exports}}
</select><a id="formatlink2" href="#" target="_blank"><svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-info-circle-fill" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412l-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM8 5.5a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"/></svg></a>&nbsp;
<button id="downloadButton" onclick="download()">Download</button>{{license}}</div></div></body></html>"""

licensetemplate=""""""

classtreequery="""PREFIX owl: <http://www.w3.org/2002/07/owl#>\n
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n
        SELECT DISTINCT ?subject ?label ?supertype\n
        WHERE {\n
           { ?individual rdf:type ?subject . } UNION { ?subject rdf:type owl:Class . } .\n
           OPTIONAL { ?subject rdfs:subClassOf ?supertype } .\n
           OPTIONAL { ?subject rdfs:label ?label. filter(langMatches(lang(?label),\"en\")) }
           OPTIONAL { ?subject rdfs:label ?label }.\n
            FILTER (\n
                (\n
                ?subject != owl:Class &&\n
                ?subject != rdf:List &&\n
                ?subject != rdf:Property &&\n
                ?subject != rdfs:Class &&\n
                ?subject != rdfs:Datatype &&\n
                ?subject != rdfs:ContainerMembershipProperty &&\n
                ?subject != owl:DatatypeProperty &&\n
                ?subject != owl:AnnotationProperty &&\n
                ?subject != owl:Restriction &&\n
                ?subject != owl:ObjectProperty &&\n
                ?subject != owl:NamedIndividual &&\n
                ?subject != owl:Ontology) )\n
        }"""

class OntDocGeneration:

    def __init__(self, prefixes,prefixnamespace,prefixnsshort,license,labellang,outpath,graph):
        self.prefixes=prefixes
        self.prefixnamespace = prefixnamespace
        self.namespaceshort = prefixnsshort.replace("/","")
        self.outpath=outpath
        self.license=license
        self.licenseuri=None
        self.labellang=labellang
        self.graph=graph
        self.preparedclassquery=prepareQuery(classtreequery)
        if prefixnamespace==None or prefixnsshort==None or prefixnamespace=="" or prefixnsshort=="":
            self.namespaceshort = "suni"
            self.prefixnamespace = "http://purl.org/suni/"
        if outpath==None:
            self.outpath = "suni_htmls/"
        else:
            self.outpath = self.outpath.replace("\\", "/")
            if not outpath.endswith("/"):
                self.outpath += "/"
        #prefixes["reversed"]["http://purl.org/suni/"] = "suni"

    def processLicense(self):
        if self.license==None or self.license=="" or self.license=="No License Statement":
            return ""
        if self.license.startswith("CC"):
            spl=self.license.split(" ")
            res= """<span style="float:right;margin-left:auto;margin-right:0px;text-align:right">This work is released under <a rel="license" target="_blank" href="http://creativecommons.org/licenses/"""+str(spl[1]).lower()+"/"+str(spl[2])+"""/">
            <img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/"""+str(spl[1]).lower()+"""/"""+str(spl[2])+"""/80x15.png"/></a></span>"""
            self.licenseuri="http://creativecommons.org/licenses/"+str(spl[1]).lower()+"/"+str(spl[2])
            return res
        else:
            return """All rights reserved."""

    def generateOntDocForNameSpace(self, prefixnamespace,dataformat="HTML"):
        outpath=self.outpath
        corpusid=self.namespaceshort
        if not os.path.isdir(outpath):
            os.mkdir(outpath)
        labeltouri = {}
        uritolabel = {}
        uritotreeitem={}
        curlicense=self.processLicense()
        subjectstorender = set()
        for sub in self.graph.subjects():
            if prefixnamespace in sub:
                subjectstorender.add(sub)
                for obj in self.graph.objects(sub, URIRef("http://www.w3.org/2000/01/rdf-schema#label")):
                    labeltouri[str(obj)] = str(sub)
                    uritolabel[str(sub)] = {"label":str(obj)}
        if os.path.exists(outpath + corpusid + '_search.js'):
            try:
                with open(outpath + corpusid + '_search.js', 'r', encoding='utf-8') as f:
                    data = json.loads(f.read().replace("var search=",""))
                    for key in data:
                        labeltouri[key]=data[key]
            except Exception as e:
                QgsMessageLog.logMessage("Exception occured " + str(e), "OntdocGeneration", Qgis.Info)
        with open(outpath + corpusid + '_search.js', 'w', encoding='utf-8') as f:
            f.write("var search=" + json.dumps(labeltouri, indent=2, sort_keys=True))
            f.close()
        prevtree=[]
        if os.path.exists(outpath + corpusid + '_classtree.js'):
            try:
                with open(outpath + corpusid + '_classtree.js', 'r', encoding='utf-8') as f:
                    prevtree = json.loads(f.read().replace("var tree=",""))["core"]["data"]
            except Exception as e:
                QgsMessageLog.logMessage("Exception occured " + str(e), "OntdocGeneration", Qgis.Info)
        classidset=set()
        tree=self.getClassTree(self.graph, uritolabel,classidset,uritotreeitem)
        for tr in prevtree:
            if tr["id"] not in classidset:
                tree["core"]["data"].append(tr)
        with open(outpath + "style.css", 'w', encoding='utf-8') as f:
            f.write(stylesheet)
            f.close()
        with open(outpath + "startscripts.js", 'w', encoding='utf-8') as f:
            f.write(startscripts.replace("{{baseurl}}",prefixnamespace))
            f.close()
        pathmap = {}
        paths = {}
        subtorenderlen = len(subjectstorender)
        subtorencounter = 0
        for subj in subjectstorender:
            path = subj.replace(prefixnamespace, "")
            #try:
            if "/" in path:
                addpath = ""
                for pathelem in path.split("/"):
                    addpath += pathelem + "/"
                    if not os.path.isdir(outpath + addpath):
                        os.mkdir(outpath + addpath)
                if outpath + path[0:path.rfind('/')] + "/" not in paths:
                    paths[outpath + path[0:path.rfind('/')] + "/"] = []
                paths[outpath + path[0:path.rfind('/')] + "/"].append(addpath[0:addpath.rfind('/')])
            else:
                if not os.path.isdir(outpath + path):
                    os.mkdir(outpath + path)
                if outpath not in paths:
                    paths[outpath] = []
                paths[outpath].append(path + "/index.html")
            self.createHTML(outpath + path, self.graph.predicate_objects(subj), subj, prefixnamespace, self.graph.subject_predicates(subj),
                       self.graph,str(corpusid) + "_search.js", str(corpusid) + "_classtree.js",uritotreeitem,curlicense)
            subtorencounter += 1
            print(str(subtorencounter) + "/" + str(subtorenderlen) + " " + str(outpath + path))
            #except Exception as e:
            #    print(e)
            #    QgsMessageLog.logMessage("Exception occured " + str(e), "OntdocGeneration", Qgis.Info)
        # print(paths)
        self.assignGeoClassesToTree(tree)
        with open(outpath + corpusid + "_classtree.js", 'w', encoding='utf-8') as f:
            f.write("var tree=" + json.dumps(tree, indent=2))
            f.close()
        QgsMessageLog.logMessage("BaseURL " + str(uritotreeitem), "OntdocGeneration", Qgis.Info)
        for path in paths:
            indexhtml = htmltemplate.replace("{{toptitle}}","Index page for " + str(prefixnamespace)).replace("{{title}}","Index page for " + str(prefixnamespace)).replace(
                    "{{startscriptpath}}", "startscripts.js").replace("{{stylepath}}", "style.css").replace("{{classtreefolderpath}}", outpath + corpusid + "_classtree.js").replace(
                    "{{baseurl}}", prefixnamespace).replace(
                    "{{scriptfolderpath}}", outpath + corpusid + '_search.js').replace("{{indexpage}}","true")
            indexhtml+="<p>This page shows information about linked data resources in HTML. Choose the classtree navigation or search to browse the data</p>"
            indexhtml+="<table class=\"description\" style =\"height: 100%; overflow: auto\" border=1><thead><tr><th>Class</th><th>Number of instances</th></tr></thead><tbody>"
            for item in tree["core"]["data"]:
                if (item["type"]=="geoclass" or item["type"]=="class" or item["type"]=="featurecollection" or item["type"]=="geocollection") and "instancecount" in item and item["instancecount"]>0:
                    indexhtml+="<tr><td><img src=\""+tree["types"][item["type"]]["icon"]+"\" height=\"25\" width=\"25\" alt=\""+item["type"]+"\"/><a href=\""+str(item["id"])+"\" target=\"_blank\">"+str(item["text"])+"</a></td>"
                    indexhtml+="<td>"+str(item["instancecount"])+"</td></tr>"
            indexhtml += "</tbody></table>"
            indexhtml+=htmlfooter.replace("{{license}}",curlicense)
            print(path)
            with open(path + "index.html", 'w', encoding='utf-8') as f:
                f.write(indexhtml)
                f.close()


    def getClassTree(self,graph, uritolabel,classidset,uritotreeitem):
        results = graph.query(self.preparedclassquery)
        tree = {"plugins": ["search", "sort", "state", "types", "contextmenu"], "search": {}, "types": {
            "class": {"icon": "https://raw.githubusercontent.com/i3mainz/geopubby/master/public/icons/class.png"},
            "geoclass": {"icon": "https://raw.githubusercontent.com/i3mainz/geopubby/master/public/icons/geoclass.png"},
            "halfgeoclass": {"icon": "https://raw.githubusercontent.com/i3mainz/geopubby/master/public/icons/halfgeoclass.png"},
            "geocollection": {"icon": "https://raw.githubusercontent.com/i3mainz/geopubby/master/public/icons/geometrycollection.png"},
            "featurecollection": {"icon": "https://raw.githubusercontent.com/i3mainz/geopubby/master/public/icons/featurecollection.png"},
            "instance": {"icon": "https://raw.githubusercontent.com/i3mainz/geopubby/master/public/icons/instance.png"},
            "geoinstance": {"icon": "https://raw.githubusercontent.com/i3mainz/geopubby/master/public/icons/geoinstance.png"}
        },
        "core": {"check_callback": True, "data": []}}
        result = []
        ress = {}
        for res in results:
            print(res)
            if "_:" not in str(res["subject"]) and str(res["subject"]).startswith("http"):
                ress[str(res["subject"])] = {"super": res["supertype"], "label": res["label"]}
        print(ress)
        for cls in ress:
            for obj in graph.subjects(URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), URIRef(cls)):
                if str(obj) in uritolabel:
                    result.append({"id": str(obj), "parent": cls,
                                   "type": "instance",
                                   "text": uritolabel[str(obj)]["label"] + " (" + str(obj)[str(obj).rfind('/') + 1:] + ")", "data":{}})
                else:
                    result.append({"id": str(obj), "parent": cls,
                                   "type": "instance",
                                   "text": str(obj)[str(obj).rfind('/') + 1:],"data":{}})
                uritotreeitem[str(obj)] = result[-1]
                classidset.add(str(obj))
            if ress[cls]["super"] == None:
                result.append({"id": cls, "parent": "#",
                               "type": "class",
                               "text": cls[cls.rfind('/') + 1:],"data":{}})
            else:
                if "label" in cls and cls["label"] != None:
                    result.append({"id": cls, "parent": ress[cls]["super"],
                                   "type": "class",
                                   "text": ress[cls]["label"] + " (" + cls[cls.rfind('/') + 1:] + ")","data":{}})
                else:
                    result.append({"id": cls, "parent": ress[cls]["super"],
                                   "type": "class",
                                   "text": cls[cls.rfind('/') + 1:],"data":{}})
                uritotreeitem[str(cls)] = result[-1]
            classidset.add(str(cls))
        tree["core"]["data"] = result
        return tree

    def assignGeoClassesToTree(self,tree):
        classlist={}
        for item in tree["core"]["data"]:
            if item["type"]=="class":
                classlist[item["id"]]={"items":0,"geoitems":0,"item":item}
        for item in tree["core"]["data"]:
            if item["type"]=="instance" and item["parent"] in classlist:
                classlist[item["parent"]]["items"]+=1
            elif (item["type"] == "geoinstance" or item["type"]=="featurecollection" or item["type"]=="geocollection") and item["parent"] in classlist:
                classlist[item["parent"]]["items"]+=1
                classlist[item["parent"]]["geoitems"]+=1
        for item in classlist:
            if classlist[item]["items"]>0:
                classlist[item]["item"]["text"]=classlist[item]["item"]["text"]+" ["+str(classlist[item]["items"])+"]"
            if classlist[item]["items"]==classlist[item]["geoitems"] and classlist[item]["items"]>0 and classlist[item]["geoitems"]>0:
                classlist[item]["item"]["type"]="geoclass"
            elif classlist[item]["items"]>classlist[item]["geoitems"] and classlist[item]["geoitems"]>0:
                classlist[item]["item"]["type"]="halfgeoclass"
            else:
                classlist[item]["item"]["type"] = "class"


    def replaceNameSpacesInLabel(self,uri):
        for ns in self.prefixes["reversed"]:
            if ns in uri:
                return {"uri": str(self.prefixes["reversed"][ns]) + ":" + str(uri.replace(ns, "")),
                        "ns": self.prefixes["reversed"][ns]}
        return None

    def createHTMLTableValueEntry(self,subject,pred,object,ttlf,tablecontents,graph,baseurl,checkdepth,geojsonrep):
        if str(object).startswith("http"):
            if ttlf != None:
                ttlf.write("<" + str(subject) + "> <" + str(pred) + "> <" + str(object) + "> .\n")
            if str(pred) in SPARQLUtils.geopointerproperties:
                for geotup in graph.predicate_objects(object):
                    if str(geotup[0]) in SPARQLUtils.geoproperties and isinstance(geotup[1],Literal):
                        geojsonrep = LayerUtils.processLiteral(str(geotup[1]), geotup[1].datatype, "")
            label = str(str(object)[str(object).rfind('/') + 1:])
            for obj in graph.objects(object, URIRef("http://www.w3.org/2000/01/rdf-schema#label")):
                label = str(obj)
            if baseurl in str(object):
                rellink = str(object).replace(baseurl, "")
                for i in range(0, checkdepth):
                    rellink = "../" + rellink
                rellink += "/index.html"
                tablecontents += "<span><a property=\"" + str(pred) + "\" resource=\"" + str(object) + "\" href=\"" + rellink + "\">" + label + " <span style=\"color: #666;\">(" + self.namespaceshort + ":" + str(
                    str(str(object)[str(object).rfind('/') + 1:])) + ")</span></a></span>"
            else:
                res = self.replaceNameSpacesInLabel(str(object))
                if res != None:
                    tablecontents += "<span><a property=\"" + str(pred) + "\" resource=\"" + str(
                        object) + "\" target=\"_blank\" href=\"" + str(
                        object) + "\">" + label + " <span style=\"color: #666;\">(" + res[
                                         "uri"] + ")</span></a></span>"
                else:
                    tablecontents += "<span><a property=\"" + str(pred) + "\" resource=\"" + str(
                        object) + "\" target=\"_blank\" href=\"" + str(
                        object) + "\">" + label + "</a></span>"
        else:
            if isinstance(object, Literal) and object.datatype != None:
                if ttlf!=None:
                    ttlf.write("<" + str(subject) + "> <" + str(pred) + "> \"" + str(object) + "\"^^<" + str(
                    object.datatype) + "> .\n")
                tablecontents += "<span property=\"" + str(pred) + "\" content=\"" + str(
                    object) + "\" datatype=\"" + str(object.datatype) + "\">" + str(
                    object) + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"" + str(
                    object.datatype) + "\">" + str(
                    object.datatype[object.datatype.rfind('/') + 1:]) + "</a>)</small></span>"
                if str(pred) in SPARQLUtils.geoproperties and isinstance(object,Literal):
                    geojsonrep = LayerUtils.processLiteral(str(object), object.datatype, "")
            else:
                if ttlf!=None:
                    ttlf.write("<" + str(subject) + "> <" + str(pred) + "> \"" + str(object) + "\" .\n")
                tablecontents += "<span property=\"" + str(pred) + "\" content=\"" + str(
                    object) + "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\">" + str(object) + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#string\">xsd:string</a>)</small></span>"
        return {"html":tablecontents,"geojson":geojsonrep}

    def createHTML(self,savepath, predobjs, subject, baseurl, subpreds, graph, searchfilename, classtreename,uritotreeitem,curlicense):
        tablecontents = ""
        isodd = False
        geojsonrep=None
        foundimages=[]
        savepath = savepath.replace("\\", "/")
        #QgsMessageLog.logMessage("BaseURL " + str(baseurl), "OntdocGeneration", Qgis.Info)
        #QgsMessageLog.logMessage("SavePath " + str(savepath), "OntdocGeneration", Qgis.Info)
        if savepath.endswith("/"):
            savepath+="/"
        if savepath.endswith("/"):
            checkdepth = subject.replace(baseurl, "").count("/")
        else:
            checkdepth = subject.replace(baseurl, "").count("/")
        #QgsMessageLog.logMessage("Checkdepth: " + str(checkdepth), "OntdocGeneration", Qgis.Info)
        checkdepth+=1
        print("Checkdepth: " + str(checkdepth))
        foundlabel = ""
        predobjmap={}
        isgeocollection=False
        comment=None
        parentclass=None
        if str(subject) in uritotreeitem and uritotreeitem[str(subject)]["parent"].startswith("http"):
            parentclass=str(uritotreeitem[str(subject)]["parent"])
            uritotreeitem[parentclass]["instancecount"]=0
        ttlf = open(savepath + "/index.ttl", "w", encoding="utf-8")
        for tup in sorted(predobjs,key=lambda tup: tup[0]):
            if str(tup[0]) not in predobjmap:
                predobjmap[str(tup[0])]=[]
            predobjmap[str(tup[0])].append(tup[1])
            if parentclass!=None and str(tup[0]) not in uritotreeitem[parentclass]["data"]:
                uritotreeitem[parentclass]["data"][str(tup[0])]=0
            if parentclass!=None:
                uritotreeitem[parentclass]["data"][str(tup[0])]+=1
                uritotreeitem[parentclass]["instancecount"]+=1
        for tup in sorted(predobjmap):
            if isodd:
                tablecontents += "<tr class=\"odd\">"
            else:
                tablecontents += "<tr class=\"even\">"
            if str(tup)=="http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and URIRef("http://www.opengis.net/ont/geosparql#FeatureCollection") in predobjmap[tup]:
                isgeocollection=True
                uritotreeitem["http://www.opengis.net/ont/geosparql#FeatureCollection"]["instancecount"] += 1
            elif str(tup)=="http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and URIRef("http://www.opengis.net/ont/geosparql#GeometryCollection") in predobjmap[tup]:
                isgeocollection=True
                uritotreeitem["http://www.opengis.net/ont/geosparql#GeometryCollection"]["instancecount"] += 1
            if baseurl in str(tup):
                rellink = str(tup).replace(baseurl, "")
                for i in range(0, checkdepth):
                    rellink = "../" + rellink
                rellink += "/index.html"
                label = rellink.replace("/index.html", "")
                tablecontents += "<td class=\"property\"><span class=\"property-name\"><a class=\"uri\" target=\"_blank\" href=\"" + rellink + "\">" + label + "</a></span></td>"
            else:
                res = self.replaceNameSpacesInLabel(tup)
                if res != None:
                    tablecontents += "<td class=\"property\"><span class=\"property-name\"><a class=\"uri\" target=\"_blank\" href=\"" + str(
                        tup) + "\">" + str(tup[tup.rfind('/') + 1:]) + " <span style=\"color: #666;\">(" + res[
                                         "uri"] + ")</span></a></span></td>"
                else:
                    tablecontents += "<td class=\"property\"><span class=\"property-name\"><a class=\"uri\" target=\"_blank\" href=\"" + str(
                        tup[0]) + "\">" + str(tup[tup.rfind('/') + 1:]) + "</a></span></td>"
            if str(tup) == "http://www.w3.org/2000/01/rdf-schema#label":
                foundlabel = str(predobjmap[tup][0])
            if str(tup) in SPARQLUtils.commentproperties:
                comment = str(predobjmap[tup][0])
            if list(filter(str(tup).endswith, SPARQLUtils.imageextensions)) != []:
                foundimages.append(str(predobjmap[tup][0]))
            if len(predobjmap[tup]) > 0:
                if len(predobjmap[tup])>1:
                    tablecontents+="<td class=\"wrapword\"><ul>"
                    for item in predobjmap[tup]:
                        tablecontents+="<li>"
                        res=self.createHTMLTableValueEntry(subject, tup, item, ttlf, tablecontents, graph,
                                              baseurl, checkdepth,geojsonrep)
                        tablecontents = res["html"]
                        geojsonrep = res["geojson"]
                        tablecontents += "</li>"
                    tablecontents+="</ul></td>"
                else:
                    tablecontents+="<td class=\"wrapword\">"
                    res=self.createHTMLTableValueEntry(subject, tup, predobjmap[tup][0], ttlf, tablecontents, graph,
                                              baseurl, checkdepth,geojsonrep)
                    tablecontents=res["html"]
                    geojsonrep=res["geojson"]
                    tablecontents+="</td>"
            else:
                tablecontents += "<td class=\"wrapword\"></td>"
            tablecontents += "</tr>"
            isodd = not isodd
        subpredsmap={}
        for tup in sorted(subpreds,key=lambda tup: tup[0]):
            if str(tup[1]) not in subpredsmap:
                subpredsmap[str(tup[1])]=[]
            subpredsmap[str(tup[1])].append(tup[0])
        for tup in subpredsmap:
            if isodd:
                tablecontents += "<tr class=\"odd\">"
            else:
                tablecontents += "<tr class=\"even\">"
            if baseurl in str(tup):
                rellink = str(tup).replace(baseurl, "")
                for i in range(0, checkdepth):
                    rellink = "../" + rellink
                rellink += "/index.html"
                label = rellink.replace("/index.html", "")
                tablecontents += "<td class=\"property\">Is <span class=\"property-name\"><a class=\"uri\" target=\"_blank\" href=\"" + rellink + "\">" + label + " <span style=\"color: #666;\">(" + self.namespaceshort + ":" + str(
                    str(tup[tup.rfind('/') + 1:])) + ")</span></a></span> of</td>"
            else:
                res = self.replaceNameSpacesInLabel(tup)
                if res != None:
                    tablecontents += "<td class=\"property\">Is <span class=\"property-name\"><a class=\"uri\" target=\"_blank\" href=\"" + str(
                        tup) + "\">" + str(tup[tup.rfind('/') + 1:]) + " <span style=\"color: #666;\">(" + res[
                                         "uri"] + ")</span></a></span> of</td>"
                else:
                    tablecontents += "<td class=\"property\">Is <span class=\"property-name\"><a class=\"uri\" target=\"_blank\" href=\"" + str(
                        tup) + "\">" + str(tup[tup.rfind('/') + 1:]) + "</a></span> of</td>"
            if len(subpredsmap[tup]) > 0:
                if len(subpredsmap[tup]) > 1:
                    tablecontents += "<td class=\"wrapword\"><ul>"
                    for item in subpredsmap[tup]:
                        tablecontents += "<li>"
                        res = self.createHTMLTableValueEntry(subject, tup, item, None, tablecontents, graph,
                                                             baseurl, checkdepth, geojsonrep)
                        tablecontents = res["html"]
                        tablecontents += "</li>"
                    tablecontents += "</ul></td>"
                else:
                    tablecontents += "<td class=\"wrapword\">"
                    res = self.createHTMLTableValueEntry(subject, tup, subpredsmap[tup][0], None, tablecontents, graph,
                                                         baseurl, checkdepth, geojsonrep)
                    tablecontents = res["html"]
                    tablecontents += "</td>"
            else:
                tablecontents += "<td class=\"wrapword\"></td>"
            tablecontents += "</tr>"
            isodd = not isodd
        if self.licenseuri!=None:
            ttlf.write("<"+str(subject)+"> <http://purl.org/dc/elements/1.1/license> <"+self.licenseuri+"> .\n")
        ttlf.close()
        with open(savepath + "/index.json", 'w', encoding='utf-8') as f:
            f.write(json.dumps(predobjmap))
            f.close()
        with open(savepath + "/index.html", 'w', encoding='utf-8') as f:
            rellink = searchfilename
            for i in range(0, checkdepth):
                rellink = "../" + rellink
            rellink2 = classtreename
            for i in range(0, checkdepth):
                rellink2 = "../" + rellink2
            rellink3 = "style.css"
            for i in range(0, checkdepth):
                rellink3 = "../" + rellink3
            rellink4 = "startscripts.js"
            for i in range(0, checkdepth):
                rellink4 = "../" + rellink4
            if geojsonrep != None:
                myexports=geoexports
            else:
                myexports=nongeoexports
            if foundlabel != "":
                f.write(htmltemplate.replace("{{prefixpath}}", self.prefixnamespace).replace("{{toptitle}}", foundlabel).replace(
                    "{{startscriptpath}}", rellink4).replace("{{stylepath}}", rellink3).replace("{{indexpage}}","false").replace("{{title}}",
                                                                                                "<a href=\"" + str(
                                                                                                    subject) + "\">" + str(
                                                                                                    foundlabel) + "</a>").replace(
                    "{{baseurl}}", baseurl).replace("{{tablecontent}}", tablecontents).replace("{{description}}",
                                                                                               "").replace(
                    "{{scriptfolderpath}}", rellink).replace("{{classtreefolderpath}}", rellink2).replace("{{exports}}",myexports).replace("{{subject}}",str(subject)))
            else:
                f.write(htmltemplate.replace("{{prefixpath}}", self.prefixnamespace).replace("{{indexpage}}","false").replace("{{toptitle}}", str(subject[
                                                                                                            subject.rfind(
                                                                                                                "/") + 1:])).replace(
                    "{{startscriptpath}}", rellink4).replace("{{stylepath}}", rellink3).replace("{{title}}",
                                                                                                "<a href=\"" + str(
                                                                                                    subject) + "\">" + str(
                                                                                                    subject[
                                                                                                    subject.rfind(
                                                                                                        "/") + 1:]) + "</a>").replace(
                    "{{baseurl}}", baseurl).replace("{{description}}",
                                                                                               "").replace(
                    "{{scriptfolderpath}}", rellink).replace("{{classtreefolderpath}}", rellink2).replace("{{exports}}",myexports).replace("{{subject}}",str(subject)))
            for image in foundimages:
                f.write(imagestemplate.replace("{{image}}",image))
            if comment!=None:
                f.write(htmlcommenttemplate.replace("{{comment}}",comment))
            if geojsonrep!=None and not isgeocollection:
                if str(subject) in uritotreeitem:
                    uritotreeitem[str(subject)]["type"]="geoinstance"
                jsonfeat={"type": "Feature", 'id':str(subject),'label':foundlabel, 'properties': predobjmap, "geometry": geojsonrep}
                f.write(maptemplate.replace("{{myfeature}}",json.dumps(jsonfeat)))
            elif isgeocollection:
                featcoll={"type":"FeatureCollection", "id":subject, "features":[]}
                for memberid in graph.objects(subject,URIRef("http://www.w3.org/2000/01/rdf-schema#member")):
                    for geoinstance in graph.predicate_objects(memberid):
                        geojsonrep=None
                        if str(geoinstance[0]) in SPARQLUtils.geoproperties and isinstance(geoinstance[1],Literal):
                            geojsonrep = LayerUtils.processLiteral(str(geoinstance[1]), geoinstance[1].datatype, "")
                            uritotreeitem[str(subject)]["type"] = "geocollection"
                        elif str(geoinstance[0]) in SPARQLUtils.geopointerproperties:
                            uritotreeitem[str(subject)]["type"] = "featurecollection"
                            for geotup in graph.predicate_objects(geoinstance[1]):
                                if str(geotup[0]) in SPARQLUtils.geoproperties and isinstance(geotup[1],Literal):
                                    geojsonrep = LayerUtils.processLiteral(str(geotup[1]), geotup[1].datatype, "")
                        if geojsonrep!=None:
                            featcoll["features"].append({"type": "Feature", 'id':str(memberid), 'properties': {}, "geometry": geojsonrep})
                f.write(maptemplate.replace("{{myfeature}}",json.dumps(featcoll)))
            f.write(htmltabletemplate.replace("{{tablecontent}}", tablecontents))
            f.write(htmlfooter.replace("{{exports}}",myexports).replace("{{license}}",curlicense))
            f.close()

