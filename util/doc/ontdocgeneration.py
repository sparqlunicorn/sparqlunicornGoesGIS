# -*- coding: UTF-8 -*-
from rdflib import Graph
from rdflib import URIRef, Literal, BNode
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

function exportGeoJSON(){
    if(typeof(feature) !== "undefined"){
        saveTextAsFile(JSON.stringify(feature),"geojson")
    }
}

function parseWKTStringToJSON(wktstring){	
    wktstring=wktstring.substring(wktstring.lastIndexOf('(')+1,wktstring.lastIndexOf(')')-1)	
    resjson=[]	
    for(coordset of wktstring.split(",")){	
        curobject={}	
        coords=coordset.split(" ")	
        if(coords.length==3){	
            resjson.append({"x":coords[0],"y":coords[1],"z":coords[2]})	
        }else{	
            resjson.append({"x":coords[0],"y":coords[1]})	
        }	
    }	
    return resjson	
}

function exportCSV(){	
    rescsv=""	
    if(typeof(feature)!=="undefined"){	
        if("features" in feature){	
           for(feat of feature["features"]){	
                rescsv+="\\""+feat["geometry"]["type"].toUpperCase()+"("	
                feat["geometry"].coordinates.forEach(function(p,i){	
                //	console.log(p)	
                    if(i<feat["geometry"].coordinates.length-1)rescsv =  rescsv + p[0] + ' ' + p[1] + ', ';	
                    else rescsv =  rescsv + p[0] + ' ' + p[1] + ')';	
                })	
                rescsv+=")\\","	
                if("properties" in feat){	
                    if(gottitle==false){	
                       rescsvtitle="\\"the_geom\\","	
                       for(prop in feat["properties"]){	
                          rescsvtitle+="\\""+prop+"\\","	
                       }	
                       rescsvtitle+="\\n"	
                       rescsv=rescsvtitle+rescsv	
                       gottitle=true	
                    }	
                    for(prop in feat["properties"]){	
                        rescsv+="\\""+feat["properties"][prop]+"\\","	
                    }	
                }	
                rescsv+="\\n"	
           }	
        }else{	
            gottitle=false	
            rescsv+="\\""+feature["geometry"]["type"].toUpperCase()+"("	
            feature["geometry"].coordinates.forEach(function(p,i){	
            //	console.log(p)	
                if(i<feature["geometry"].coordinates.length-1)rescsv =  rescsv + p[0] + ' ' + p[1] + ', ';	
                else rescsv =  rescsv + p[0] + ' ' + p[1] + ')';	
            })	
            rescsv+=")\\","	
            if("properties" in feature){	
                if(gottitle==false){	
                   rescsvtitle=""	
                   for(prop in feature["properties"]){	
                      rescsvtitle+="\\""+prop+"\\","	
                   }	
                   rescsvtitle+="\\n"	
                   rescsv=rescsvtitle+rescsv	
                   gottitle=true	
                }	
                for(prop in feature["properties"]){	
                    rescsv+="\\""+feature["properties"][prop]+"\\","	
                }	
            }	
        }	
        saveTextAsFile(rescsv,".csv")	
    }else if(typeof(nongeofeature)!=="undefined"){	
        if("features" in nongeofeature){	
           for(feat of nongeofeature["features"]){	
                if("properties" in feat){	
                    if(gottitle==false){	
                       rescsvtitle="\\"the_geom\\","	
                       for(prop in feat["properties"]){	
                          rescsvtitle+="\\""+prop+"\\","	
                       }	
                       rescsvtitle+="\\n"	
                       rescsv=rescsvtitle+rescsv	
                       gottitle=true	
                    }	
                    for(prop in feat["properties"]){	
                        rescsv+="\\""+feat["properties"][prop]+"\\","	
                    }	
                }	
                rescsv+="\\n"	
           }	
        }else{	
            gottitle=false	
            if("properties" in nongeofeature){	
                if(gottitle==false){	
                   rescsvtitle=""	
                   for(prop in nongeofeature["properties"]){	
                      rescsvtitle+="\\""+prop+"\\","	
                   }	
                   rescsvtitle+="\\n"	
                   rescsv=rescsvtitle+rescsv	
                   gottitle=true	
                }	
                for(prop in nongeofeature["properties"]){	
                    rescsv+="\\""+nongeofeature["properties"][prop]+"\\","	
                }	
            }	
        }	
        saveTextAsFile(rescsv,".csv")	
    }	
}

function setSVGDimensions(){ 
    $('.svgview').each(function(i, obj) {
        console.log(obj)
        console.log($(obj).children().first()[0])
        maxx=Number.MIN_VALUE
        maxy=Number.MIN_VALUE
        minx=Number.MAX_VALUE
        miny=Number.MAX_VALUE
        $(obj).children().each(function(i){
            svgbbox=$(this)[0].getBBox()
            console.log(svgbbox)
            if(svgbbox.x+svgbbox.width>maxx){
                maxx=svgbbox.x+svgbbox.width
            }
            if(svgbbox.y+svgbbox.height>maxy){
                maxy=svgbbox.y+svgbbox.height
            }
            if(svgbbox.y<miny){
                miny=svgbbox.y
            }
            if(svgbbox.x<minx){
                minx=svgbbox.x
            }
        });
        console.log(""+(minx)+" "+(miny-(maxy-miny))+" "+((maxx-minx)+25)+" "+((maxy-miny)+25))
        newviewport=""+((minx))+" "+(miny)+" "+((maxx-minx)+25)+" "+((maxy-miny)+25)
        $(obj).attr("viewBox",newviewport)
        $(obj).attr("width",((maxx-minx))+10)
        $(obj).attr("height",((maxy-miny)+10))
        console.log($(obj).hasClass("svgoverlay"))
        if($(obj).hasClass("svgoverlay")){
            naturalWidth=$(obj).prev()[0].naturalWidth
            naturalHeight=$(obj).prev()[0].naturalHeight
            currentWidth=$(obj).prev()[0].width
            currentHeight=$(obj).prev()[0].height
            overlayposX = (currentWidth/naturalWidth) * minx;
            overlayposY = (currentHeight/naturalHeight) * miny;
            overlayposWidth = ((currentWidth/naturalWidth) * maxx)-overlayposX;
            overlayposHeight = ((currentHeight/naturalHeight) * maxy)-overlayposY;
            $(obj).css({top: overlayposY+"px", left:overlayposX+"px", position:"absolute"})
            $(obj).attr("height",overlayposHeight)
            $(obj).attr("width",overlayposWidth)
        }
    });
}



function exportWKT(){	
    if(typeof(feature)!=="undefined"){	
        reswkt=""	
        if("features" in feature){	
            for(feat of feature["features"]){	
                reswkt+=feat["geometry"]["type"].toUpperCase()+"("	
                feat["geometry"].coordinates.forEach(function(p,i){	
                //	console.log(p)	
                    if(i<feat["geometry"].coordinates.length-1)reswkt =  reswkt + p[0] + ' ' + p[1] + ', ';	
                    else reswkt =  reswkt + p[0] + ' ' + p[1] + ')';	
                })	
                reswkt+=")\\n"	
            }	
        }else{	
                reswkt+=feature["geometry"]["type"].toUpperCase()+"("	
                feature["geometry"].coordinates.forEach(function(p,i){	
                    if(i<feature["geometry"].coordinates.length-1)reswkt =  reswkt + p[0] + ' ' + p[1] + ', ';	
                    else reswkt =  reswkt + p[0] + ' ' + p[1] + ')';	
                })	
                reswkt+=")\\n"	
        }	
        saveTextAsFile(reswkt,".wkt")	
    }	
}

function downloadFile(filePath){
    var link=document.createElement('a');
    link.href = filePath;
    link.download = filePath.substr(filePath.lastIndexOf('/') + 1);
    link.click();
}

function saveTextAsFile(tosave,fileext){
    var a = document.createElement('a');
    a.style = "display: none";  
    var blob= new Blob([tosave], {type:'text/plain'});
    var url = window.URL.createObjectURL(blob);
    var filename = "res."+fileext;
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(function(){
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);  
    }, 1000);
}

function download(){
    format=$('#format').val()
    if(format=="geojson"){
        exportGeoJSON()
    }else if(format=="ttl"){
        downloadFile("index.ttl")
    }else if(format=="json"){
        downloadFile("index.json")
    }else if(format=="wkt"){	
        exportWKT()	
    }else if(format=="csv"){
        exportCSV()
    }
}

function rewriteLink(thelink){
    if(thelink==null){
        rest=search[document.getElementById('search').value].replace(baseurl,"")
    }else{
        curlocpath=window.location.href.replace(baseurl,"")
        rest=thelink.replace(baseurl,"")
    }
    if(!(rest.endsWith("/"))){
        rest+="/"
    }
    count=0
    if(!indexpage){
        count=rest.split("/").length-1
    }
    console.log(count)
    counter=0
    if (typeof relativedepth !== 'undefined'){
        while(counter<relativedepth){
            rest="../"+rest
            counter+=1
        }
    }else{
        while(counter<count){
            rest="../"+rest
            counter+=1
        }   
    }
    rest+="index.html"
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

var presenter = null;
function setup3dhop(meshurl,meshformat) { 
  presenter = new Presenter("draw-canvas");  
  presenter.setScene({
    meshes: {
			"mesh_1" : { url: meshurl}
		},
		modelInstances : {
			"model_1" : { 
				mesh  : "mesh_1",
				color : [0.8, 0.7, 0.75]
			}
		}
  });
}

function start3dhop(meshurl,meshformat){
    init3dhop();
	setup3dhop(meshurl,meshformat);
	resizeCanvas(640,480);
  	moveToolbar(20,20);  
}


let camera, scene, renderer,controls;

function viewGeometry(geometry) {
  const material = new THREE.MeshPhongMaterial({
    color: 0xffffff,
    flatShading: true,
    vertexColors: THREE.VertexColors,
    wireframe: false
  });
  const mesh = new THREE.Mesh(geometry, material);
  scene.add(mesh);
}

function initThreeJS(domelement,verts,meshurls) {
    scene = new THREE.Scene();
    minz=Number.MAX_VALUE
    maxz=Number.MIN_VALUE
    miny=Number.MAX_VALUE
    maxy=Number.MIN_VALUE
    minx=Number.MAX_VALUE
    maxx=Number.MIN_VALUE
	vertarray=[]
    console.log(verts)
    var svgShape = new THREE.Shape();
    first=true
    for(vert of verts){
        if(first){
            svgShape.moveTo(vert["x"], vert["y"]);
           first=false
        }else{
            svgShape.lineTo(vert["x"], vert["y"]);
        }
        vertarray.push(vert["x"])
        vertarray.push(vert["y"])
        vertarray.push(vert["z"])
        if(vert["z"]>maxz){
            maxz=vert["z"]
        }
        if(vert["z"]<minz){
            minz=vert["z"]
        }
        if(vert["y"]>maxy){
            maxy=vert["y"]
        }
        if(vert["y"]<miny){
            miny=vert["y"]
        }
        if(vert["x"]>maxx){
            maxy=vert["x"]
        }
        if(vert["x"]<minx){
            miny=vert["x"]
        }
    }
    if(meshurls.length>0){
        var loader = new THREE.PLYLoader();
        loader.load(meshurls[0], viewGeometry);
    }
    camera = new THREE.PerspectiveCamera(90,window.innerWidth / window.innerHeight, 0.1, 150 );
    scene.add(new THREE.AmbientLight(0x222222));
    var light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(20, 20, 0);
    scene.add(light);
    var axesHelper = new THREE.AxesHelper( Math.max(maxx, maxy, maxz)*4 );
    scene.add( axesHelper );
    console.log("Depth: "+(maxz-minz))
    var extrudedGeometry = new THREE.ExtrudeGeometry(svgShape, {depth: maxz-minz, bevelEnabled: false});
    extrudedGeometry.computeBoundingBox()
    centervec=new THREE.Vector3()
    extrudedGeometry.boundingBox.getCenter(centervec)
    console.log(centervec)
    const material = new THREE.MeshBasicMaterial( { color: 0xFFFFFF, wireframe:true } );
    const mesh = new THREE.Mesh( extrudedGeometry, material );
    scene.add( mesh );
    renderer = new THREE.WebGLRenderer( { antialias: false } );
	renderer.setPixelRatio( window.devicePixelRatio );
    renderer.setSize( 480, 500 );
    document.getElementById(domelement).appendChild( renderer.domElement );
	controls = new THREE.OrbitControls( camera, renderer.domElement );
    controls.target.set( centervec.x,centervec.y,centervec.z );
    camera.position.x= centervec.x
    camera.position.y= centervec.y
    camera.position.z = centervec.z+10;
    controls.maxDistance= Math.max(maxx, maxy, maxz)*5
    controls.update();
    animate()
}

function animate() {
    requestAnimationFrame( animate );
    controls.update();
    renderer.render( scene, camera );
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

function formatHTMLTableForClassRelations(result,nodeicon,nodelabel,nodeid){
    dialogcontent=""
    if(nodelabel.includes("[")){
        nodelabel=nodelabel.substring(0,nodelabel.lastIndexOf("[")-1)
    }
    dialogcontent="<h3><img src=\\""+nodeicon+"\\" height=\\"25\\" width=\\"25\\" alt=\\"Instance\\"/><a href=\\""+nodeid.replace('/index.json','/index.html')+"\\" target=\\"_blank\\"> "+nodelabel+"</a></h3><table border=1 id=classrelationstable><thead><tr><th>Incoming Concept</th><th>Incoming Relation</th><th>Concept</th><th>Outgoing Relation</th><th>Outgoing Concept</th></tr></thead><tbody>"
    for(res in result["from"]){
        for(instance in result["from"][res]){
            if(instance=="instancecount"){
                continue;
            }
            dialogcontent+="<tr><td><img src=\\"https://raw.githubusercontent.com/i3mainz/geopubby/master/public/icons/class.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Class\\"/><a href=\\""+instance+"\\" target=\\"_blank\\">"+shortenURI(instance)+"</a></td>"
            dialogcontent+="<td><a href=\\""+res+"\\" target=\\"_blank\\">"
            finished=false
            for(ns in annotationnamespaces){
                if(res.includes(annotationnamespaces[ns])){
                    dialogcontent+="<img src=\\"https://raw.githubusercontent.com/i3mainz/geopubby/master/public/icons/annotationproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Annotation Property\\"/>"
                    finished=true
                }
            }
            if(!finished && res in geoproperties && geoproperties[res]=="ObjectProperty"){
                dialogcontent+="<img src=\\"https://raw.githubusercontent.com/i3mainz/geopubby/master/public/icons/geoobjectproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Datatype Property\\"/>"
            }else if(!finished){
                dialogcontent+="<img src=\\"https://raw.githubusercontent.com/i3mainz/geopubby/master/public/icons/objectproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Datatype Property\\"/>"
            }
            dialogcontent+=shortenURI(res)+"</a></td>"
            dialogcontent+="<td><img src=\\""+nodeicon+"\\" height=\\"25\\" width=\\"25\\" alt=\\"Instance\\"/><a href=\\""+nodeid+"\\" target=\\"_blank\\">"+nodelabel+"</a></td><td></td><td></td></tr>"
        }
    }
    for(res in result["to"]){
        for(instance in result["to"][res]){
            if(instance=="instancecount"){
                continue;
            }
            dialogcontent+="<tr><td></td><td></td><td><img src=\\""+nodeicon+"\\" height=\\"25\\" width=\\"25\\" alt=\\"Instance\\"/><a href=\\""+nodeid+"\\" target=\\"_blank\\">"+nodelabel+"</a></td>"
            dialogcontent+="<td><a href=\\""+res+"\\" target=\\"_blank\\">"
            finished=false
            for(ns in annotationnamespaces){
                if(res.includes(annotationnamespaces[ns])){
                    dialogcontent+="<img src=\\"https://raw.githubusercontent.com/i3mainz/geopubby/master/public/icons/annotationproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Annotation Property\\"/>"
                    finished=true
                }
            }
            if(!finished && res in geoproperties && geoproperties[res]=="ObjectProperty"){
                dialogcontent+="<img src=\\"https://raw.githubusercontent.com/i3mainz/geopubby/master/public/icons/geoobjectproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Datatype Property\\"/>"
            }else if(!finished){
                dialogcontent+="<img src=\\"https://raw.githubusercontent.com/i3mainz/geopubby/master/public/icons/objectproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Datatype Property\\"/>"
            }
            dialogcontent+=shortenURI(res)+"</a></td>"
            dialogcontent+="<td><img src=\\"https://raw.githubusercontent.com/i3mainz/geopubby/master/public/icons/class.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Class\\"/><a href=\\""+instance+"\\" target=\\"_blank\\">"+shortenURI(instance)+"</a></td></tr>"
        }
    }
    dialogcontent+="</tbody></table>"
    dialogcontent+="<button style=\\"float:right\\" id=\\"closebutton\\" onclick='document.getElementById(\\"classrelationdialog\\").close()'>Close</button>"
    return dialogcontent
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
            dialogcontent+="<td><a href=\\""+rewriteLink(result[res][0]+"")+"\\" target=\\"_blank\\">"+shortenURI(result[res][0]+"")+"</a></td>"
        }else{
            dialogcontent+="<td>"+result[res][0]+"</td>"
        }
        dialogcontent+="</tr>"
    }
    dialogcontent+="</tbody></table>"
    dialogcontent+="<button style=\\"float:right\\" id=\\"closebutton\\" onclick='document.getElementById(\\"dataschemadialog\\").close()'>Close</button>"
    return dialogcontent
}

function getClassRelationDialog(node){
     nodeid=rewriteLink(node.id).replace(".html",".json")
     nodelabel=node.text
     nodetype=node.type
     nodeicon=node.icon
     props={}
     if("data" in node){
        props=node.data
     }
     console.log(nodetype)
     if(nodetype=="class" || nodetype=="geoclass" || node.type=="collectionclass"){
        console.log(props)
        dialogcontent=formatHTMLTableForClassRelations(props,nodeicon,nodelabel,nodeid)
        document.getElementById("classrelationdialog").innerHTML=dialogcontent
        $('#classrelationstable').DataTable();
        document.getElementById("classrelationdialog").showModal();
     }
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
     if(nodetype=="class" || nodetype=="geoclass" || node.type=="collectionclass"){
        console.log(props)
        dialogcontent=formatHTMLTableForResult(props["to"],nodeicon)
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
        nodetype=node.type
        thelinkpart="class"
        if(nodetype=="instance" || nodetype=="geoinstance"){
            thelinkpart="instance"
        }    
        contextmenu={
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
                "icon": "https://github.com/i3mainz/geopubby/raw/master/public/icons/"+thelinkpart+"link.png",
                "action":function(obj){
                    copyText=node.id
                    navigator.clipboard.writeText(copyText);
                }    
            },
            "discoverrelations":{
                "separator_before": false,
                "separator_after": false,
                "label": "Discover "+node.type+" relations",
                "icon": "https://github.com/i3mainz/geopubby/raw/master/public/icons/"+thelinkpart+"link.png",
                "action":function(obj){
                    console.log("class relations")
                    if(node.type=="class" || node.type=="geoclass" || node.type=="collectionclass"){
                        getClassRelationDialog(node)
                    }
                }    
            },
            "loaddataschema": {
                "separator_before": false,
                "separator_after": false,
                "icon":"https://github.com/i3mainz/geopubby/raw/master/public/icons/"+node.type+"schema.png",
                "label": "Load dataschema for "+node.type,
                "action": function (obj) {
                    console.log(node)
                    console.log(node.id)
                    console.log(baseurl)
                    if(node.id.includes(baseurl)){
                        getDataSchemaDialog(node) 
                    }else if(node.type=="class" || node.type=="geoclass" || node.type=="collectionclass"){
                        getDataSchemaDialog(node) 
                    }                                         
                }
            }                
        }
        return contextmenu
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
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
<script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
<script src="https://cdn.datatables.net/1.12.1/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three/build/three.min.js"></script>	
<script src="https://cdn.jsdelivr.net/npm/three/examples/js/controls/TrackballControls.js"></script>	
<script src="https://cdn.jsdelivr.net/npm/three/examples/js/controls/OrbitControls.js"></script>	
<script src="https://cdn.jsdelivr.net/npm/three/examples/js/loaders/PLYLoader.js"></script>
<script src="{{scriptfolderpath}}"></script><script src="{{classtreefolderpath}}"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.3.12/jstree.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/rdflib@2.2.19/dist/rdflib.min.js"></script>
<script type="text/javascript" src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.bundle.min.js"></script>
<script src="{{startscriptpath}}"></script></head>
<div id="mySidenav" class="sidenav" style="overflow:auto;">
  <a href="javascript:void(0)" class="closebtn" onclick="closeNav()">&times;</a>
  GeoClasses: <input type="checkbox" id="geoclasses"/><br/>
  Search:<input type="text" id="classsearch"><br/><div id="jstree"></div>
</div><script>var indexpage={{indexpage}}
var relativedepth={{relativedepth}}</script>
<body><div id="header"><h1 id="title">{{title}}</h1></div><div class="page-resource-uri"><a href="{{baseurl}}">{{baseurl}}</a> <b>powered by Static GeoPubby</b> generated using the <a style="color:blue;font-weight:bold" target="_blank" href="https://github.com/sparqlunicorn/sparqlunicornGoesGIS">SPARQLing Unicorn QGIS Plugin</a></div>
</div><div id="rdficon"><span style="font-size:30px;cursor:pointer" onclick="openNav()">&#9776;</span></div> <div class="search"><div class="ui-widget">Search: <input id="search" size="50"><button id="gotosearch" onclick="followLink()">Go</button><b>Download Options:</b>&nbsp;Format:<select id="format" onchange="changeDefLink()">	
{{exports}}
</select><a id="formatlink" href="#" target="_blank"><svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-info-circle-fill" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412l-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM8 5.5a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"/></svg></a>&nbsp;
<button id="downloadButton" onclick="download()">Download</button><br/></div></div><dialog id="classrelationdialog" width="500" height="500" modal="true"></dialog><dialog id="dataschemadialog" width="500" height="500" modal="true"></dialog>
<div class="container-fluid"><div class="row-fluid" id="main-wrapper">
"""

imagecarouselheader="""<div id="imagecarousel" class="carousel slide" data-ride="carousel"><div class="carousel-inner">"""

imagecarouselfooter="""</div> <a class="carousel-control-prev" href="#carouselExampleControls" role="button" data-slide="prev">
    <span class="carousel-control-prev-icon" aria-hidden="true"></span>
    <span class="sr-only">Previous</span>
  </a>
  <a class="carousel-control-next" href="#carouselExampleControls" role="button" data-slide="next">
    <span class="carousel-control-next-icon" aria-hidden="true"></span>
    <span class="sr-only">Next</span>
  </a></div>"""

imagestemplate="""<div class="{{carousel}}">
<a href="{{image}}" target=\"_blank\"><img src="{{image}}" style="max-width:485px;max-height:500px" alt="{{image}}" title="{{imagetitle}}" /></a>
</div>
"""

imageswithannotemplate="""<div class="{{carousel}}">
<a href=\"{{image}}\" target=\"_blank\"><img src="{{image}}" style="max-width:485px;max-height:500px" alt="{{image}}" title="{{imagetitle}}" /></a>
{{svganno}}
</div>
"""

videotemplate="""
<div class="video">
<video width="320" height="240" controls>
  <source src="{{video}}">
Your browser does not support the video tag.
</video>
</div>
"""

audiotemplate="""
<div class="audio">
<audio controls>
  <source src="{{audio}}">
Your browser does not support the audio element.
</audio>
</div>
"""

imagestemplatesvg="""<div class="{{carousel}}" style="max-width:485px;max-height:500px">
{{image}}
</div>
"""

threejstemplate="""	
<div id="threejs" class="threejscontainer" style="max-width:485px;max-height:500px">	
</div>	
<script>$(document).ready(function(){initThreeJS('threejs',parseWKTStringToJSON("{{wktstring}}"),{{meshurls}})})</script>	
"""

image3dtemplate="""<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/stylesheet/3dhop.css"/>
<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/js/spidergl.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/js/corto.em.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/js/corto.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/js/presenter.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/js/nexus.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/js/ply.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/js/trackball_sphere.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/js/trackball_turntable.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/js/trackball_turntable_pan.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/js/trackball_pantilt.js"></script>
<script type="text/javascript" src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/js/init.js"></script>
<div id="3dhop" class="tdhop" onmousedown="if (event.preventDefault) event.preventDefault()"><div id="tdhlg"></div>
<div id="toolbar"><img id="home"     title="Home"                  src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/skins/dark/home.png"            /><br/>
<img id="zoomin"   title="Zoom In"               src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/skins/dark/zoomin.png"          /><br/>
<img id="zoomout"  title="Zoom Out"              src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/skins/dark/zoomout.png"         /><br/>
<img id="light_on" title="Disable Light Control" src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/skins/dark/lightcontrol_on.png" style="position:absolute; visibility:hidden;"/>
<img id="light"    title="Enable Light Control"  src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/skins/dark/lightcontrol.png"    /><br/>
<img id="full_on"  title="Exit Full Screen"      src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/skins/dark/full_on.png"         style="position:absolute; visibility:hidden;"/>
<img id="full"     title="Full Screen"           src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/skins/dark/full.png"            />
</div><canvas id="draw-canvas" style="background-color:white"></canvas></div><script>$(document).ready(function(){	
start3dhop("{{meshurl}}","{{meshformat}}")});</script>"""

nongeoexports="""
<option value="csv">Comma Separated Values (CSV)</option>
<option value="geojson">(Geo)JSON</option>
<option value="json">JSON-LD</option>
<option value="ttl" selected>Turtle (TTL)</option>
"""

geoexports="""
<option value="csv">Comma Separated Values (CSV)</option>
<option value="geojson">(Geo)JSON</option>
<!--<option value="geojsonld">GeoJSON-LD</option>
<option value="geouri">GeoURI</option> 
<option value="json">JSON-LD</option>
<option value="kml">Keyhole Markup Language (KML)</option>
<option value="latlontext">LatLonText</option>
<option value="mapml">Map Markup Language (MapML)</option>
<option value="osmlink">OSM Link</option>-->
<option value="ttl" selected>Turtle (TTL)</option>
<option value="wkt">Well-Known-Text (WKT)</option>
"""

maptemplate="""<script src="https://unpkg.com/leaflet@1.6.0/dist/leaflet.js"></script>
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
	var feature = {{myfeature}}
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

nonmaptemplate="""<script>var nongeofeature = {{myfeature}}</script>"""

htmlcommenttemplate="""<p class="comment"><b>Description:</b> {{comment}}</p>"""

htmltabletemplate="""
<table border=1 width=100% class=description><thead><tr><th>Property</th><th>Value</th></tr></thead><tbody>{{tablecontent}}</tbody></table>"""

htmlfooter="""<div id="footer"><div class="container-fluid"><b>Download Options:</b>&nbsp;Format:<select id="format" onchange="changeDefLink()">	
{{exports}}
</select><a id="formatlink2" href="#" target="_blank"><svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-info-circle-fill" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412l-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM8 5.5a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"/></svg></a>&nbsp;
<button id="downloadButton" onclick="download()">Download</button>{{license}}</div></div><script>$(document).ready(function(){setSVGDimensions()})</script></body></html>"""

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

    def __init__(self, prefixes,prefixnamespace,prefixnsshort,license,labellang,outpath,graph,progress):
        self.prefixes=prefixes
        self.prefixnamespace = prefixnamespace
        self.namespaceshort = prefixnsshort.replace("/","")
        self.outpath=outpath
        self.progress=progress
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

    def updateProgressBar(self,currentsubject,allsubjects):
        newtext = "\n".join(self.progress.labelText().split("\n")[0:-1])
        self.progress.setLabelText(newtext + "\n Processed: "+str(currentsubject)+" of "+str(allsubjects)+" URIs... ("+str(round(((currentsubject/allsubjects)*100),0))+"%)")

    def processSubjectPath(self,outpath,paths,path):
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
        if os.path.exists(outpath + path + "/index.ttl"):
            try:
                self.graph.parse(outpath + path + "/index.ttl")
            except Exception as e:
                print(e)
        return paths

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
            if prefixnamespace in sub or isinstance(sub,BNode):
                subjectstorender.add(sub)
                for tup in self.graph.predicate_objects(sub):
                    if str(tup[0]) in SPARQLUtils.labelproperties:
                        labeltouri[str(tup[1])] = str(sub)
                        uritolabel[str(sub)] = {"label":str(tup[1])}
                        break
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
        postprocessing=Graph()
        subtorenderlen = len(subjectstorender)
        subtorencounter = 0
        for subj in subjectstorender:
            path = subj.replace(prefixnamespace, "")
            paths=self.processSubjectPath(outpath,paths,path)
            if os.path.exists(outpath + path+"/index.ttl"):
                try:
                    self.graph.parse(outpath + path+"/index.ttl")
                except Exception as e:
                    print(e)
            postprocessing=self.createHTML(outpath + path, self.graph.predicate_objects(subj), subj, prefixnamespace, self.graph.subject_predicates(subj),
                       self.graph,str(corpusid) + "_search.js", str(corpusid) + "_classtree.js",uritotreeitem,curlicense,subjectstorender,postprocessing)
            subtorencounter += 1
            if subtorencounter%500==0:
                subtorenderlen=len(subjectstorender)+len(postprocessing)
                self.updateProgressBar(subtorencounter,subtorenderlen)
            print(str(subtorencounter) + "/" + str(subtorenderlen) + " " + str(outpath + path))
            #except Exception as e:
            #    print(e)
            #    QgsMessageLog.logMessage("Exception occured " + str(e), "OntdocGeneration", Qgis.Info)
        QgsMessageLog.logMessage("Postprocessing " + str(postprocessing.subjects()), "OntdocGeneration", Qgis.Info)
        for subj in postprocessing.subjects():
            path = str(subj).replace(prefixnamespace, "")
            paths=self.processSubjectPath(outpath,paths,path)
            if os.path.exists(outpath + path+"/index.ttl"):
                try:
                    self.graph.parse(outpath + path+"/index.ttl")
                except Exception as e:
                    print(e)
            self.createHTML(outpath + path, self.graph.predicate_objects(subj), subj, prefixnamespace, self.graph.subject_predicates(subj),
                       self.graph,str(corpusid) + "_search.js", str(corpusid) + "_classtree.js",uritotreeitem,curlicense,subjectstorender,postprocessing)
            subtorencounter += 1
            if subtorencounter%500==0:
                subtorenderlen=len(subjectstorender)+len(postprocessing)
                self.updateProgressBar(subtorencounter,subtorenderlen)
            print(str(subtorencounter) + "/" + str(subtorenderlen) + " " + str(outpath + path))
        self.assignGeoClassesToTree(tree)
        with open(outpath + corpusid + "_classtree.js", 'w', encoding='utf-8') as f:
            f.write("var tree=" + json.dumps(tree, indent=2))
            f.close()
        for path in paths:
            ttlf = open(path + "index.ttl", "w", encoding="utf-8")
            QgsMessageLog.logMessage("BaseURL " + str(outpath)+" "+str(path)+" "+outpath + corpusid + '_search.js', "OntdocGeneration", Qgis.Info)
            checkdepth = self.checkDepthFromPath(path, outpath, path)-1
            sfilelink=self.generateRelativeLinkFromGivenDepth(prefixnamespace,checkdepth,corpusid + '_search.js',False)
            classtreelink = self.generateRelativeLinkFromGivenDepth(prefixnamespace,checkdepth,corpusid + "_classtree.js",False)
            stylelink =self.generateRelativeLinkFromGivenDepth(prefixnamespace,checkdepth,"style.css",False)
            scriptlink = self.generateRelativeLinkFromGivenDepth(prefixnamespace, checkdepth, "startscripts.js", False)
            nslink=prefixnamespace+str(self.getAccessFromBaseURL(str(outpath),str(path)))
            for sub in self.graph.subjects():
                if nslink in sub:
                    for tup in self.graph.predicate_objects(sub):
                        if isinstance(tup[1],Literal):
                            if tup[1].datatype!=None:
                                ttlf.write("<" + str(sub) + "> <" + str(tup[0]) + "> \"" + str(tup[1]) + "\"^^<"+str(tup[1].datatype)+"> .\n")
                            else:
                                ttlf.write("<" + str(sub) + "> <" + str(tup[0]) + "> \"" + str(tup[1]) + "\" .\n")
                        elif isinstance(tup[1],URIRef):
                            ttlf.write("<"+str(sub)+"> <"+str(tup[0])+"> <"+str(tup[1])+"> .\n")
            ttlf.close()
            QgsMessageLog.logMessage("BaseURL " + nslink,"OntdocGeneration", Qgis.Info)
            indexhtml = htmltemplate.replace("{{baseurl}}", prefixnamespace).replace("{{toptitle}}","Index page for " + nslink).replace("{{title}}","Index page for " + nslink).replace("{{startscriptpath}}", scriptlink).replace("{{stylepath}}", stylelink)\
                .replace("{{classtreefolderpath}}",classtreelink).replace("{{baseurlhtml}}", nslink).replace("{{scriptfolderpath}}", sfilelink).replace("{{exports}}",nongeoexports)
            if nslink==prefixnamespace:
                indexhtml=indexhtml.replace("{{indexpage}}","true")
            else:
                indexhtml = indexhtml.replace("{{indexpage}}", "false")
            indexhtml+="<p>This page shows information about linked data resources in HTML. Choose the classtree navigation or search to browse the data</p>"
            indexhtml+="<table class=\"description\" style =\"height: 100%; overflow: auto\" border=1 id=indextable><thead><tr><th>Class</th><th>Number of instances</th><th>Instance Example</th></tr></thead><tbody>"
            for item in tree["core"]["data"]:
                if (item["type"]=="geoclass" or item["type"]=="class" or item["type"]=="featurecollection" or item["type"]=="geocollection") and "instancecount" in item and item["instancecount"]>0:
                    exitem=None
                    for item2 in tree["core"]["data"]:
                        if item2["parent"]==item["id"] and (item2["type"]=="instance" or item2["type"]=="geoinstance") and nslink in item2["id"]:
                            checkdepth = self.checkDepthFromPath(path, prefixnamespace, item2["id"])-1
                            exitem="<td><img src=\""+tree["types"][item2["type"]]["icon"]+"\" height=\"25\" width=\"25\" alt=\""+item2["type"]+"\"/><a href=\""+self.generateRelativeLinkFromGivenDepth(prefixnamespace,checkdepth,str(item2["id"]),True)+"\">"+str(item2["text"])+"</a></td>"
                            break
                    if exitem!=None:
                        indexhtml+="<tr><td><img src=\""+tree["types"][item["type"]]["icon"]+"\" height=\"25\" width=\"25\" alt=\""+item["type"]+"\"/><a href=\""+str(item["id"])+"\" target=\"_blank\">"+str(item["text"])+"</a></td>"
                        indexhtml+="<td>"+str(item["instancecount"])+"</td>"+exitem+"</tr>"
            indexhtml += "</tbody></table><script>$('#indextable').DataTable();</script>"
            indexhtml+=htmlfooter.replace("{{license}}",curlicense).replace("{{exports}}",nongeoexports)
            print(path)
            with open(path + "index.html", 'w', encoding='utf-8') as f:
                f.write(indexhtml)
                f.close()


    def getClassTree(self,graph, uritolabel,classidset,uritotreeitem):
        results = graph.query(self.preparedclassquery)
        tree = {"plugins": ["search", "sort", "state", "types", "contextmenu"], "search": {"show_only_matches":True}, "types": {
            "class": {"icon": "https://raw.githubusercontent.com/i3mainz/geopubby/master/public/icons/class.png"},
            "geoclass": {"icon": "https://raw.githubusercontent.com/i3mainz/geopubby/master/public/icons/geoclass.png"},
            "halfgeoclass": {"icon": "https://raw.githubusercontent.com/i3mainz/geopubby/master/public/icons/halfgeoclass.png"},
            "collectionclass": {"icon": "https://raw.githubusercontent.com/i3mainz/geopubby/master/public/icons/collectionclass.png"},
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
                res = self.replaceNameSpacesInLabel(str(obj))
                if str(obj) in uritolabel:
                    restext= uritolabel[str(obj)]["label"] + " (" + self.shortenURI(str(obj)) + ")"
                    if res!=None:
                        restext=uritolabel[str(obj)]["label"] + " (" + res["uri"] + ")"
                    result.append({"id": str(obj), "parent": cls,
                                   "type": "instance",
                                   "text": restext, "data":{}})
                else:
                    restext= self.shortenURI(str(obj))
                    if res!=None:
                        restext+= " (" + res["uri"] + ")"
                    result.append({"id": str(obj), "parent": cls,
                                   "type": "instance",
                                   "text": restext,"data":{}})
                uritotreeitem[str(obj)] = result[-1]
                classidset.add(str(obj))
            res = self.replaceNameSpacesInLabel(str(cls))
            if ress[cls]["super"] == None:
                restext = self.shortenURI(str(cls))
                if res != None:
                    restext += " (" + res["uri"] + ")"
                result.append({"id": cls, "parent": "#",
                               "type": "class",
                               "text": restext,"data":{}})
            else:
                if "label" in cls and cls["label"] != None:
                    restext = ress[cls]["label"] + " (" + self.shortenURI(str(cls)) + ")"
                    if res != None:
                        restext = ress[cls]["label"] + " (" + res["uri"] + ")"
                    result.append({"id": cls, "parent": ress[cls]["super"],
                                   "type": "class",
                                   "text": restext + ")","data":{}})
                else:
                    restext = self.shortenURI(str(cls))
                    if res != None:
                        restext += " (" + res["uri"] + ")"
                    result.append({"id": cls, "parent": ress[cls]["super"],
                                   "type": "class",
                                   "text": restext,"data":{}})
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
                if classlist[item]["item"]["text"].endswith("]"):
                    classlist[item]["item"]["text"]=classlist[item]["item"]["text"][0:classlist[item]["item"]["text"].rfind("[")-1]+" ["+str(classlist[item]["items"])+"]"
                else:
                    classlist[item]["item"]["text"]=classlist[item]["item"]["text"]+" ["+str(classlist[item]["items"])+"]"
            if item in SPARQLUtils.collectionclasses:
                classlist[item]["item"]["type"] = "collectionclass"
            elif classlist[item]["items"]==classlist[item]["geoitems"] and classlist[item]["items"]>0 and classlist[item]["geoitems"]>0:
                classlist[item]["item"]["type"]="geoclass"
            elif classlist[item]["items"]>classlist[item]["geoitems"] and classlist[item]["geoitems"]>0:
                classlist[item]["item"]["type"]="halfgeoclass"
            else:
                classlist[item]["item"]["type"] = "class"
    def shortenURI(self,uri):
        if uri!=None and "#" in uri:
            return uri[uri.rfind('#')+1:]
        if uri!=None and "/" in uri:
            return uri[uri.rfind('/')+1:]
        return uri

    def replaceNameSpacesInLabel(self,uri):
        for ns in self.prefixes["reversed"]:
            if ns in uri:
                return {"uri": str(self.prefixes["reversed"][ns]) + ":" + str(uri.replace(ns, "")),
                        "ns": self.prefixes["reversed"][ns]}
        return None

    def generateRelativeLinkFromGivenDepth(self,baseurl,checkdepth,item,withindex):
        rellink = str(item).replace(baseurl, "")
        for i in range(0, checkdepth):
            rellink = "../" + rellink
        if withindex:
            rellink += "/index.html"
        #QgsMessageLog.logMessage("Relative Link from Given Depth: " + rellink,"OntdocGeneration", Qgis.Info)
        return rellink

    def searchObjectConnectionsForAggregateData(self,graph,object,pred,geojsonrep,foundmedia,imageannos,image3dannos,label,unitlabel):
        geoprop=False
        incollection=False
        if pred in SPARQLUtils.geopointerproperties:
            geoprop=True
        if pred in SPARQLUtils.collectionrelationproperties:
            incollection=True
        foundval=None
        foundunit=None
        for tup in graph.predicate_objects(object):
            if str(tup[0]) in SPARQLUtils.labelproperties:
                label=str(tup[1])
            if pred=="http://www.w3.org/ns/oa#hasSelector" and tup[0]==URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type") and (tup[1]==URIRef("http://www.w3.org/ns/oa#SvgSelector") or tup[1]==URIRef("http://www.w3.org/ns/oa#WKTSelector")):
                for svglit in graph.objects(object,URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#value")):
                    if "<svg" in str(svglit):
                        imageannos.add(str(svglit))
                    elif ("POINT" in str(svglit).upper() or "POLYGON" in str(svglit).upper() or "LINESTRING" in str(svglit).upper()):
                        image3dannos.add(str(svglit))
            if isinstance(tup[1], Literal) and (str(tup[0]) in SPARQLUtils.geoproperties or str(tup[1].datatype) in SPARQLUtils.geoliteraltypes):
                geojsonrep = LayerUtils.processLiteral(str(tup[1]), tup[1].datatype, "",None,None,True)
            if incollection and "<svg" in str(tup[1]):
                 foundmedia["image"].add(str(tup[1]))
            elif incollection and "http" in str(tup[1]):
                ext="."+''.join(filter(str.isalpha,str(tup[1]).split(".")[-1]))
                if ext in SPARQLUtils.fileextensionmap:
                    foundmedia[SPARQLUtils.fileextensionmap[ext]].add(str(tup[1]))
            if str(tup[0]) in SPARQLUtils.valueproperties and isinstance(tup[1],Literal):
                foundval=tup[1]
            if str(tup[0]) in SPARQLUtils.unitproperties and isinstance(tup[1],URIRef):
                foundunit=str(tup[1])
        if foundunit!=None and foundval!=None and label!=None:
            res=self.replaceNameSpacesInLabel(str(foundunit))
            if res!=None:
                unitlabel=str(foundval)+" <a href=\""+str(foundunit)+"\" target=\"_blank\">"+res["uri"]+"</a>"
            else:
                unitlabel=str(foundval)+" <a href=\""+str(foundunit)+"\" target=\"_blank\">"+str(self.shortenURI(foundunit))+"</a>"
        return {"geojsonrep":geojsonrep,"label":label,"unitlabel":unitlabel,"foundmedia":foundmedia,"imageannos":imageannos,"image3dannos":image3dannos}


    def createHTMLTableValueEntry(self,subject,pred,object,ttlf,graph,baseurl,checkdepth,geojsonrep,foundmedia,imageannos,image3dannos):
        tablecontents=""
        label=""
        if isinstance(object,URIRef) or isinstance(object,BNode):
            if ttlf != None:
                ttlf.write("<" + str(subject) + "> <" + str(pred) + "> <" + str(object) + "> .\n")
            label = str(self.shortenURI(str(object)))
            unitlabel=""
            mydata=self.searchObjectConnectionsForAggregateData(graph,object,pred,geojsonrep,foundmedia,imageannos,image3dannos,label,unitlabel)
            label=mydata["label"]
            geojsonrep=mydata["geojsonrep"]
            foundmedia=mydata["foundmedia"]
            imageannos=mydata["imageannos"]
            image3dannos=mydata["image3dannos"]
            unitlabel=mydata["unitlabel"]
            if baseurl in str(object) or isinstance(object,BNode):
                rellink = self.generateRelativeLinkFromGivenDepth(baseurl,checkdepth,str(object),True)
                tablecontents += "<span><a property=\"" + str(pred) + "\" resource=\"" + str(object) + "\" href=\"" + rellink + "\">"+ label + " <span style=\"color: #666;\">(" + self.namespaceshort + ":" + str(self.shortenURI(str(object))) + ")</span></a>"
            else:
                res = self.replaceNameSpacesInLabel(str(object))
                if res != None:
                    tablecontents += "<span><a property=\"" + str(pred) + "\" resource=\"" + str(
                        object) + "\" target=\"_blank\" href=\"" + str(
                        object) + "\">" + label + " <span style=\"color: #666;\">(" + res[
                                         "uri"] + ")</span></a>"
                else:
                    tablecontents += "<span><a property=\"" + str(pred) + "\" resource=\"" + str(
                        object) + "\" target=\"_blank\" href=\"" + str(
                        object) + "\">" + label + "</a>"
            if unitlabel!="":
                tablecontents+=" <span style=\"font-weight:bold\">["+str(unitlabel)+"]</span>"
            tablecontents+="</span>"
        else:
            label=str(object)
            if isinstance(object, Literal) and object.datatype != None:
                res = self.replaceNameSpacesInLabel(str(object.datatype))
                if ttlf!=None:
                    ttlf.write("<" + str(subject) + "> <" + str(pred) + "> \"" + str(object) + "\"^^<" + str(
                    object.datatype) + "> .\n")
                objstring=str(object).replace("<", "&lt").replace(">", "&gt;")
                if str(object.datatype)=="http://www.w3.org/2001/XMLSchema#anyURI":
                    objstring="<a href=\""+str(object)+"\">"+str(object)+"</a>"
                if res != None:
                    tablecontents += "<span property=\"" + str(pred) + "\" content=\"" + str(
                        object).replace("<", "&lt").replace(">", "&gt;").replace("\"", "'") + "\" datatype=\"" + str(
                        object.datatype) + "\">" + objstring + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"" + str(
                        object.datatype) + "\">" + res["uri"]+ "</a>)</small></span>"
                else:
                    tablecontents += "<span property=\"" + str(pred) + "\" content=\"" + str(
                        object).replace("<", "&lt").replace(">", "&gt;").replace("\"", "'") + "\" datatype=\"" + str(
                        object.datatype) + "\">" + objstring + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"" + str(
                        object.datatype) + "\">" + self.shortenURI(str(object.datatype)) + "</a>)</small></span>"
                if isinstance(object, Literal) and (str(pred) in SPARQLUtils.geoproperties or str(object.datatype) in SPARQLUtils.geoliteraltypes):
                    geojsonrep = LayerUtils.processLiteral(str(object), object.datatype, "",None,None,True)
            else:
                if object.language != None:
                    if ttlf!=None:
                        ttlf.write("<" + str(subject) + "> <" + str(pred) + "> \"" + str(object) + "\"@"+str(object.language)+" .\n")
                    tablecontents += "<span property=\"" + str(pred) + "\" content=\"" + str(
                        object).replace("<", "&lt").replace(">", "&gt;").replace("\"","'") + "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\" xml:lang=\"" + str(object.language) + "\">" + str(object).replace("<", "&lt").replace(">", "&gt;") + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#langString\">rdf:langString</a>) (<a href=\"http://www.lexvo.org/page/iso639-1/"+str(object.language)+"\" target=\"_blank\">iso6391:" + str(object.language) + "</a>)</small></span>"
                else:
                    if ttlf!=None:
                        ttlf.write("<" + str(subject) + "> <" + str(pred) + "> \"" + str(object) + "\" .\n")
                    tablecontents += "<span property=\"" + str(pred) + "\" content=\"" + str(
                        object).replace("<","&lt").replace(">","&gt;").replace("\"","'") + "\" datatype=\"http://www.w3.org/2001/XMLSchema#string\">" + str(object).replace("<","&lt").replace(">","&gt;") + " <small>(<a style=\"color: #666;\" target=\"_blank\" href=\"http://www.w3.org/2001/XMLSchema#string\">xsd:string</a>)</small></span>"
        return {"html":tablecontents,"geojson":geojsonrep,"foundmedia":foundmedia,"imageannos":imageannos,"image3dannos":image3dannos,"label":label}


    def formatPredicate(self,tup,baseurl,checkdepth,tablecontents,graph,reverse):
        label = self.shortenURI(str(tup))
        for obj in graph.predicate_objects(object):
            if str(obj[0]) in SPARQLUtils.labelproperties:
                label = str(obj[1])
                break
        tablecontents += "<td class=\"property\">"
        if reverse:
            tablecontents+="Is "
        if baseurl in str(tup):
            rellink = self.generateRelativeLinkFromGivenDepth(baseurl, checkdepth,str(tup),True)
            tablecontents += "<span class=\"property-name\"><a class=\"uri\" target=\"_blank\" href=\"" + rellink + "\">" + label + "</a></span>"
        else:
            res = self.replaceNameSpacesInLabel(tup)
            if res != None:
                tablecontents += "<span class=\"property-name\"><a class=\"uri\" target=\"_blank\" href=\"" + str(
                    tup) + "\">" + label + " <span style=\"color: #666;\">(" + res["uri"] + ")</span></a></span>"
            else:
                tablecontents += "<span class=\"property-name\"><a class=\"uri\" target=\"_blank\" href=\"" + str(
                    tup[0]) + "\">" + label + "</a></span>"
        if reverse:
            tablecontents+=" of"
        tablecontents += "</td>"
        return tablecontents

    def checkDepthFromPath(self,savepath,baseurl,subject):
        if savepath.endswith("/"):
            checkdepth = subject.replace(baseurl, "").count("/")
        else:
            checkdepth = subject.replace(baseurl, "").count("/")
        #QgsMessageLog.logMessage("Checkdepth: " + str(checkdepth), "OntdocGeneration", Qgis.Info)
        checkdepth+=1
        print("Checkdepth: " + str(checkdepth))
        return checkdepth

    def getAccessFromBaseURL(self,baseurl,savepath):
        QgsMessageLog.logMessage("Checkdepth: " + baseurl+" "+savepath.replace(baseurl, ""), "OntdocGeneration", Qgis.Info)
        return savepath.replace(baseurl, "")

    def createHTML(self,savepath, predobjs, subject, baseurl, subpreds, graph, searchfilename, classtreename,uritotreeitem,curlicense,subjectstorender,postprocessing):
        tablecontents = ""
        isodd = False
        geojsonrep=None
        foundmedia={"audio":set(),"video":set(),"image":set(),"mesh":set()}
        savepath = savepath.replace("\\", "/")
        checkdepth=self.checkDepthFromPath(savepath, baseurl, subject)
        foundlabel = ""
        imageannos=set()
        image3dannos=set()
        predobjmap={}
        isgeocollection=False
        comment=None
        parentclass=None
        inverse=False
        if str(subject) in uritotreeitem and uritotreeitem[str(subject)]["parent"].startswith("http"):
            parentclass=str(uritotreeitem[str(subject)]["parent"])
            if parentclass not in uritotreeitem:
                uritotreeitem[parentclass]={"id": parentclass, "parent": "#","type": "class","text": self.shortenURI(str(parentclass)),"data":{}}
            uritotreeitem[parentclass]["instancecount"]=0
        ttlf = open(savepath + "/index.ttl", "w", encoding="utf-8")
        if parentclass!=None:
            uritotreeitem[parentclass]["data"]["to"]={}
            uritotreeitem[parentclass]["data"]["from"]={}
        for tup in sorted(predobjs,key=lambda tup: tup[0]):
            if str(tup[0]) not in predobjmap:
                predobjmap[str(tup[0])]=[]
            predobjmap[str(tup[0])].append(tup[1])
            if parentclass!=None and str(tup[0]) not in uritotreeitem[parentclass]["data"]["to"]:
                uritotreeitem[parentclass]["data"]["to"][str(tup[0])]={}
                uritotreeitem[parentclass]["data"]["to"][str(tup[0])]["instancecount"] = 0
            if parentclass!=None:
                uritotreeitem[parentclass]["data"]["to"][str(tup[0])]["instancecount"]+=1
                uritotreeitem[parentclass]["instancecount"]+=1
            if isinstance(tup[1],URIRef):
                for item in graph.objects(tup[1],URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")):
                    if parentclass!=None:
                        if item not in uritotreeitem[parentclass]["data"]["to"][str(tup[0])]:
                            uritotreeitem[parentclass]["data"]["to"][str(tup[0])][item] = 0
                        uritotreeitem[parentclass]["data"]["to"][str(tup[0])][item]+=1
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
            tablecontents=self.formatPredicate(tup, baseurl, checkdepth, tablecontents, graph,inverse)
            if str(tup) in SPARQLUtils.labelproperties:
                foundlabel = str(predobjmap[tup][0])
            if str(tup) in SPARQLUtils.commentproperties:
                comment = str(predobjmap[tup][0])
            if len(predobjmap[tup]) > 0:
                if len(predobjmap[tup])>1:
                    tablecontents+="<td class=\"wrapword\"><ul>"
                    labelmap={}
                    for item in predobjmap[tup]:
                        if ("POINT" in str(item).upper() or "POLYGON" in str(item).upper() or "LINESTRING" in str(item).upper()) and tup in SPARQLUtils.valueproperties and "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" in predobjmap and URIRef("http://www.w3.org/ns/oa#WKTSelector") in predobjmap["http://www.w3.org/1999/02/22-rdf-syntax-ns#type"]:
                            image3dannos.add(str(item))
                        elif "<svg" in str(item):
                            foundmedia["image"].add(str(item))
                        elif "http" in str(item):
                            if isinstance(item,Literal):
                                ext = "." + ''.join(filter(str.isalpha, str(item.value).split(".")[-1]))
                            else:
                                ext = "." + ''.join(filter(str.isalpha, str(item).split(".")[-1]))
                            if ext in SPARQLUtils.fileextensionmap:
                                foundmedia[SPARQLUtils.fileextensionmap[ext]].add(str(item))
                        res=self.createHTMLTableValueEntry(subject, tup, item, ttlf, graph,
                                              baseurl, checkdepth,geojsonrep,foundmedia,imageannos,image3dannos)
                        geojsonrep = res["geojson"]
                        foundmedia = res["foundmedia"]
                        imageannos=res["imageannos"]
                        image3dannos=res["image3dannos"]
                        if res["label"] not in labelmap:
                            labelmap[res["label"]]=""
                        labelmap[res["label"]]+="<li>"+str(res["html"])+"</li>"
                    for lab in sorted(labelmap):
                        tablecontents+=str(labelmap[lab])
                    tablecontents+="</ul></td>"
                else:
                    tablecontents+="<td class=\"wrapword\">"
                    if ("POINT" in str(predobjmap[tup]).upper() or "POLYGON" in str(predobjmap[tup]).upper() or "LINESTRING" in str(predobjmap[tup]).upper()) and tup in SPARQLUtils.valueproperties and "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" in predobjmap and URIRef("http://www.w3.org/ns/oa#WKTSelector") in predobjmap["http://www.w3.org/1999/02/22-rdf-syntax-ns#type"]:
                        image3dannos.add(str(predobjmap[tup][0]))
                    elif "<svg" in str(predobjmap[tup]):
                        foundmedia["image"].add(str(predobjmap[tup][0]))
                    elif "http" in str(predobjmap[tup]):
                        if isinstance(predobjmap[tup],Literal):
                            ext = "." + ''.join(filter(str.isalpha, str(predobjmap[tup][0].value).split(".")[-1]))
                        else:
                            ext = "." + ''.join(filter(str.isalpha, str(predobjmap[tup][0]).split(".")[-1]))
                        if ext in SPARQLUtils.fileextensionmap:
                            foundmedia[SPARQLUtils.fileextensionmap[ext]].add(str(predobjmap[tup][0]))
                    res=self.createHTMLTableValueEntry(subject, tup, predobjmap[tup][0], ttlf, graph,
                                              baseurl, checkdepth,geojsonrep,foundmedia,imageannos,image3dannos)
                    tablecontents+=res["html"]
                    geojsonrep=res["geojson"]
                    foundmedia = res["foundmedia"]
                    imageannos=res["imageannos"]
                    image3dannos=res["image3dannos"]
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
            if parentclass!=None and str(tup[1]) not in uritotreeitem[parentclass]["data"]["from"]:
                uritotreeitem[parentclass]["data"]["from"][str(tup[1])]={}
                uritotreeitem[parentclass]["data"]["from"][str(tup[1])]["instancecount"] = 0
            if isinstance(tup[0],URIRef):
                for item in graph.objects(tup[0],URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")):
                    if parentclass!=None:
                        if item not in uritotreeitem[parentclass]["data"]["from"][str(tup[1])]:
                            uritotreeitem[parentclass]["data"]["from"][str(tup[1])][item] = 0
                        uritotreeitem[parentclass]["data"]["from"][str(tup[1])][item]+=1
        for tup in subpredsmap:
            if isodd:
                tablecontents += "<tr class=\"odd\">"
            else:
                tablecontents += "<tr class=\"even\">"
            tablecontents=self.formatPredicate(tup, baseurl, checkdepth, tablecontents, graph,True)
            if len(subpredsmap[tup]) > 0:
                if len(subpredsmap[tup]) > 1:
                    tablecontents += "<td class=\"wrapword\"><ul>"
                    labelmap={}
                    for item in subpredsmap[tup]:
                        if item not in subjectstorender and baseurl in str(item):
                            print("Postprocessing: " + str(item)+" - "+str(tup)+" - "+str(subject))
                            postprocessing.add((item,URIRef(tup),subject))
                        res = self.createHTMLTableValueEntry(subject, tup, item, None, graph,
                                                             baseurl, checkdepth, geojsonrep,foundmedia,imageannos,image3dannos)
                        foundmedia = res["foundmedia"]
                        imageannos=res["imageannos"]
                        image3dannos=res["image3dannos"]
                        if res["label"] not in labelmap:
                            labelmap[res["label"]]=""
                        labelmap[res["label"]]+="<li>"+str(res["html"])+"</li>"
                    for lab in sorted(labelmap):
                        tablecontents+=str(labelmap[lab])
                    tablecontents += "</ul></td>"
                else:
                    tablecontents += "<td class=\"wrapword\">"
                    if subpredsmap[tup][0] not in subjectstorender and baseurl in str(subpredsmap[tup][0]):
                        print("Postprocessing: " + str(subpredsmap[tup][0]) + " - " + str(tup) + " - " + str(subject))
                        postprocessing.add((subpredsmap[tup][0], URIRef(tup), subject))
                    res = self.createHTMLTableValueEntry(subject, tup, subpredsmap[tup][0], None, graph,
                                                         baseurl, checkdepth, geojsonrep,foundmedia,imageannos,image3dannos)
                    tablecontents += res["html"]
                    foundmedia = res["foundmedia"]
                    imageannos=res["imageannos"]
                    image3dannos=res["image3dannos"]
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
            rellink=self.generateRelativeLinkFromGivenDepth(baseurl,checkdepth,searchfilename,False)
            rellink2 = self.generateRelativeLinkFromGivenDepth(baseurl,checkdepth,classtreename,False)
            rellink3 =self.generateRelativeLinkFromGivenDepth(baseurl,checkdepth,"style.css",False)
            rellink4 = self.generateRelativeLinkFromGivenDepth(baseurl, checkdepth, "startscripts.js", False)
            if geojsonrep != None:
                myexports=geoexports
            else:
                myexports=nongeoexports
            if foundlabel != "":
                f.write(htmltemplate.replace("{{baseurl}}",baseurl).replace("{{relativedepth}}",str(checkdepth)).replace("{{prefixpath}}", self.prefixnamespace).replace("{{toptitle}}", foundlabel).replace(
                    "{{startscriptpath}}", rellink4).replace("{{stylepath}}", rellink3).replace("{{indexpage}}","false").replace("{{title}}",
                                                                                                "<a href=\"" + str(
                                                                                                    subject) + "\">" + str(
                                                                                                    foundlabel) + "</a>").replace(
                    "{{baseurl}}", baseurl).replace("{{tablecontent}}", tablecontents).replace("{{description}}",
                                                                                               "").replace(
                    "{{scriptfolderpath}}", rellink).replace("{{classtreefolderpath}}", rellink2).replace("{{exports}}",myexports).replace("{{subject}}",str(subject)))
            else:
                f.write(htmltemplate.replace("{{baseurl}}",baseurl).replace("{{relativedepth}}",str(checkdepth)).replace("{{prefixpath}}", self.prefixnamespace).replace("{{indexpage}}","false").replace("{{toptitle}}", self.shortenURI(str(subject))).replace(
                    "{{startscriptpath}}", rellink4).replace("{{stylepath}}", rellink3).replace("{{title}}","<a href=\"" + str(subject) + "\">" + self.shortenURI(str(subject)) + "</a>").replace(
                    "{{baseurl}}", baseurl).replace("{{description}}",
                                                                                               "").replace(
                    "{{scriptfolderpath}}", rellink).replace("{{classtreefolderpath}}", rellink2).replace("{{exports}}",myexports).replace("{{subject}}",str(subject)))
            if comment!=None:
                f.write(htmlcommenttemplate.replace("{{comment}}",comment))
            if len(foundmedia["mesh"])>0 and len(image3dannos)>0:
                for anno in image3dannos:
                    if ("POINT" in anno.upper() or "POLYGON" in anno.upper() or "LINESTRING" in anno.upper()):
                        f.write(threejstemplate.replace("{{wktstring}}",anno).replace("{{meshurls}}",str(list(foundmedia["mesh"]))))
            elif len(foundmedia["mesh"])>0 and len(image3dannos)==0:
                print("Found 3D Model: "+str(foundmedia["mesh"]))
                for curitem in foundmedia["mesh"]:
                    format="ply"
                    if ".nxs" in curitem or ".nxz" in curitem:
                        format="nexus"
                    f.write(image3dtemplate.replace("{{meshurl}}",curitem).replace("{{meshformat}}",format))
                    break
            elif len(foundmedia["mesh"])==0 and len(image3dannos)>0:
                for anno in image3dannos:
                    if ("POINT" in anno.upper() or "POLYGON" in anno.upper() or "LINESTRING" in anno.upper()):
                        f.write(threejstemplate.replace("{{wktstring}}",anno).replace("{{meshurls}}","[]"))
            carousel="image"
            if len(foundmedia["image"])>3:
                carousel="carousel-item active"
                f.write(imagecarouselheader)
            if len(imageannos)>0 and len(foundmedia["image"])>0:
                for image in foundmedia["image"]:
                    annostring=""
                    for anno in imageannos:
                        annostring+=anno.replace("<svg>","<svg style=\"position: absolute;top: 0;left: 0;\" class=\"svgview svgoverlay\" fill=\"#044B94\" fill-opacity=\"0.4\">")
                    f.write(imageswithannotemplate.replace("{{carousel}}",carousel+"\" style=\"position: relative;display: inline-block;").replace("{{image}}",str(image)).replace("{{svganno}}",annostring).replace("{{imagetitle}}",str(image)[0:str(image).rfind('.')]))
                    if len(foundmedia["image"])>3:
                        carousel="carousel-item"
            else:
                for image in foundmedia["image"]:
                    if image=="<svg width=":
                        continue
                    if "<svg" in image:
                        if "<svg>" in image:
                            f.write(imagestemplatesvg.replace("{{carousel}}",carousel).replace("{{image}}", str(image.replace("<svg>","<svg class=\"svgview\">"))))
                        else:
                            f.write(imagestemplatesvg.replace("{{carousel}}",carousel).replace("{{image}}",str(image)))
                    else:
                        f.write(imagestemplate.replace("{{carousel}}",carousel).replace("{{image}}",str(image)).replace("{{imagetitle}}",str(image)[0:str(image).rfind('.')]))
                    if len(foundmedia["image"])>3:
                        carousel="carousel-item"
            if len(foundmedia["image"])>3:
                f.write(imagecarouselfooter)
            for audio in foundmedia["audio"]:
                f.write(audiotemplate.replace("{{audio}}",str(audio)))
            for video in foundmedia["video"]:
                f.write(videotemplate.replace("{{video}}",str(video)))
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
                        if isinstance(geoinstance[1], Literal) and (str(geoinstance[0]) in SPARQLUtils.geoproperties or str(geoinstance[1].datatype) in SPARQLUtils.geoliteraltypes):
                            geojsonrep = LayerUtils.processLiteral(str(geoinstance[1]), geoinstance[1].datatype, "",None,None,True)
                            uritotreeitem[str(subject)]["type"] = "geocollection"
                        elif str(geoinstance[0]) in SPARQLUtils.geopointerproperties:
                            uritotreeitem[str(subject)]["type"] = "featurecollection"
                            for geotup in graph.predicate_objects(geoinstance[1]):
                                if isinstance(geotup[1], Literal) and (str(geotup[0]) in SPARQLUtils.geoproperties or str(geotup[1].datatype) in SPARQLUtils.geoliteraltypes):
                                    geojsonrep = LayerUtils.processLiteral(str(geotup[1]), geotup[1].datatype, "",None,None,True)
                        if geojsonrep!=None:
                            featcoll["features"].append({"type": "Feature", 'id':str(memberid), 'properties': {}, "geometry": geojsonrep})
                f.write(maptemplate.replace("{{myfeature}}",json.dumps(featcoll)))
            f.write(htmltabletemplate.replace("{{tablecontent}}", tablecontents))
            f.write(htmlfooter.replace("{{exports}}",myexports).replace("{{license}}",curlicense))
            f.close()
        return postprocessing
