from ..export.pages.observationpage import ObservationPage
from ..export.pages.bibpage import BibPage
from ..export.pages.lexiconpage import LexiconPage
from ..export.pages.personpage import PersonPage


class DocDefaults:
    collectionclassToFunction = {
        "bibcollection": BibPage.generateCollectionWidget,
        "lexicon": LexiconPage.generateCollectionWidget,
        "observationcollection": ObservationPage.generateCollectionWidget,
        "personcollection": PersonPage.generateCollectionWidget
    }

    templates = {
        "epsgdefs": "var epsgdefs={}",
        "startscripts": """var namespaces={"rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#","xsd":"http://www.w3.org/2001/XMLSchema#","geo":"http://www.opengis.net/ont/geosparql#","rdfs":"http://www.w3.org/2000/01/rdf-schema#","owl":"http://www.w3.org/2002/07/owl#","dc":"http://purl.org/dc/terms/","skos":"http://www.w3.org/2004/02/skos/core#"}
    var annotationnamespaces=["http://www.w3.org/2004/02/skos/core#","http://www.w3.org/2000/01/rdf-schema#","http://purl.org/dc/terms/"]
    var indexpage=false
    var rangesByAttribute={}
    var overlayMaps={}
    var baseMaps = {}
    props={}
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

    commentproperties={
        "http://www.w3.org/2004/02/skos/core#definition":"DatatypeProperty",
        "http://www.w3.org/2004/02/skos/core#note": "DatatypeProperty",
        "http://www.w3.org/2004/02/skos/core#scopeNote": "DatatypeProperty",
        "http://www.w3.org/2004/02/skos/core#historyNote": "DatatypeProperty",
        "https://schema.org/description":"DatatypeProperty",
        "http://www.w3.org/2000/01/rdf-schema#comment": "DatatypeProperty",
        "http://purl.org/dc/terms/description": "DatatypeProperty",
        "http://purl.org/dc/elements/1.1/description": "DatatypeProperty"
    }

    labelproperties={
        "http://www.w3.org/2004/02/skos/core#prefLabel":"DatatypeProperty",
        "http://www.w3.org/2004/02/skos/core#prefSymbol": "DatatypeProperty",
        "http://www.w3.org/2004/02/skos/core#altLabel": "DatatypeProperty",
        "https://schema.org/name": "DatatypeProperty",
        "https://schema.org/alternateName": "DatatypeProperty",
        "http://purl.org/dc/terms/title": "DatatypeProperty",
        "http://purl.org/dc/elements/1.1/title":"DatatypeProperty",
        "http://www.w3.org/2004/02/skos/core#altSymbol": "DatatypeProperty",
        "http://www.w3.org/2004/02/skos/core#hiddenLabel": "DatatypeProperty",
        "http://www.w3.org/2000/01/rdf-schema#label": "DatatypeProperty"
    }

    var baseurl=""
      $( function() {
        var availableTags = Object.keys(search)
        $( "#search" ).autocomplete({
          source: availableTags,
          delay: 300
        });
        //console.log(availableTags)
        setupJSTree()
      } );

    function openNav() {
      document.getElementById("mySidenav").style.width = "400px";
    }

    function closeNav() {
      document.getElementById("mySidenav").style.width = "0";
    }

    function exportChartJS(){
        saveTextAsFile(JSON.stringify({"xValues":xValues,"yValues":yValues}),"json")
    }

    function exportGeoJSON(){
        if(typeof(feature) !== "undefined"){
            saveTextAsFile(JSON.stringify(feature),"geojson")
        }else if(window.location.href.includes("_nonns")){
            downloadFile(window.location.href.replace(".html",".geojson"))
        }
    }

    function parseWKTStringToJSON(wktstring){
        wktstring=wktstring.substring(wktstring.lastIndexOf('(')+1,wktstring.lastIndexOf(')')-1)
        resjson=[]
        for(coordset of wktstring.split(",")){
            curobject={}
            coords=coordset.trim().split(" ")
            console.log(coordset)
            console.log(coords)
            if(coords.length==3){
                resjson.push({"x":parseFloat(coords[0]),"y":parseFloat(coords[1]),"z":parseFloat(coords[2])})
            }else{
                resjson.push({"x":parseFloat(coords[0]),"y":parseFloat(coords[1])})
            }
        }
        console.log(resjson)
        return resjson
    }

    function testRDFLibParsing(cururl){
        var store = $rdf.graph()
        var timeout = 5000 // 5000 ms timeout
        var fetcher = new $rdf.Fetcher(store, timeout)

        fetcher.nowOrWhenFetched(cururl, function(ok, body, response) {
            if (!ok) {
                console.log("Oops, something happened and couldn't fetch data " + body);
            } else if (response.onErrorWasCalled || response.status !== 200) {
                console.log('    Non-HTTP error reloading data! onErrorWasCalled=' + response.onErrorWasCalled + ' status: ' + response.status)
            } else {
                console.log("---data loaded---")
            }
        })
        return store
    }

    function exportCSV(sepchar,filesuffix){
        rescsv=""
        if(typeof(feature)!=="undefined"){
            if("features" in feature){
               for(feat of feature["features"]){
                    rescsv+="\\""+feat["geometry"]["type"].toUpperCase()+"("
                    if(feature["geometry"]["type"].toUpperCase()=="POINT"){
                        rescsv =  rescsv + feature["geometry"].coordinates[0] + ' ' + feature["geometry"].coordinates[1]
                    }else{
                        feature["geometry"].coordinates.forEach(function(p,i){
                            if(i<feature["geometry"].coordinates.length-1) rescsv =  rescsv + p[0] + ' ' + p[1] + ', ';
                            else rescsv =  rescsv + p[0] + ' ' + p[1] + ')';
                        })
                    }
                    rescsv+=")\\""+sepchar
                    if("properties" in feat){
                        if(gottitle==false){
                           rescsvtitle="\\"the_geom\\","
                           for(prop in feat["properties"]){
                              rescsvtitle+="\\""+prop+"\\""+sepchar
                           }
                           rescsvtitle+="\\\\n"
                           rescsv=rescsvtitle+rescsv
                           gottitle=true
                        }
                        for(prop in feat["properties"]){
                            rescsv+="\\""+feat["properties"][prop]+"\\""+sepchar
                        }
                    }
                    rescsv+="\\\\n"
               }
            }else{
                gottitle=false
                rescsv+="\\""+feature["geometry"]["type"].toUpperCase()+"("
                if(feature["geometry"]["type"].toUpperCase()=="POINT"){
                    rescsv =  rescsv + feature["geometry"].coordinates[0] + ' ' + feature["geometry"].coordinates[1]
                }else{
                    feature["geometry"].coordinates.forEach(function(p,i){
                        if(i<feature["geometry"].coordinates.length-1) rescsv =  rescsv + p[0] + ' ' + p[1] + ', ';
                        else rescsv =  rescsv + p[0] + ' ' + p[1] + ')';
                    })
                }
                rescsv+=")\\""+sepchar
                if("properties" in feature){
                    if(gottitle==false){
                       rescsvtitle=""
                       for(prop in feature["properties"]){
                          rescsvtitle+="\\""+prop+"\\""+sepchar
                       }
                       rescsvtitle+="\\\\n"
                       rescsv=rescsvtitle+rescsv
                       gottitle=true
                    }
                    for(prop in feature["properties"]){
                        rescsv+="\\""+feature["properties"][prop]+"\\""+sepchar
                    }
                }
            }
            saveTextAsFile(rescsv,filesuffix)
        }else if(typeof(nongeofeature)!=="undefined"){
            if("features" in nongeofeature){
               for(feat of nongeofeature["features"]){
                    if("properties" in feat){
                        if(gottitle==false){
                           rescsvtitle="\\"the_geom\\","
                           for(prop in feat["properties"]){
                              rescsvtitle+="\\""+prop+"\\""+sepchar
                           }
                           rescsvtitle+="\\\\n"
                           rescsv=rescsvtitle+rescsv
                           gottitle=true
                        }
                        for(prop in feat["properties"]){
                            rescsv+="\\""+feat["properties"][prop]+"\\""+sepchar
                        }
                    }
                    rescsv+="\\\\n"
               }
            }else{
                gottitle=false
                if("properties" in nongeofeature){
                    if(gottitle==false){
                       rescsvtitle=""
                       for(prop in nongeofeature["properties"]){
                          rescsvtitle+="\\""+prop+"\\""+sepchar
                       }
                       rescsvtitle+="\\\\n"
                       rescsv=rescsvtitle+rescsv
                       gottitle=true
                    }
                    for(prop in nongeofeature["properties"]){
                        rescsv+="\\""+nongeofeature["properties"][prop]+"\\""+sepchar
                    }
                }
            }
            saveTextAsFile(rescsv,filesuffix)
        }
    }

    function exportGraphML(){
        resgml=`<?xml version="1.0" encoding="UTF-8"?>\\\\n<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:y="http://www.yworks.com/xml/graphml" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">\n`
        resgml+="<key for=\\"node\\" id=\\"nodekey\\" yfiles.type=\\"nodegraphics\\"></key><key for=\\"edge\\" id=\\"edgekey\\" yfiles.type=\\"edgegraphics\\"></key><graph id=\\"G\\" edgedefault=\\"directed\\">\\\\n"
        processedURIs={}
        literalcounter=1
        edgecounter=0
        if(typeof(featurecolls)!=="undefined"){
            for(feature of featurecolls){
                if("features" in feature){
                    for(feat of feature["features"]){
                        if(!(feat.id in processedURIs)){
                            resgml+="<node id=\\""+feat.id+"\\" uri=\\""+feat.id+"\\"><data key=\\"nodekey\\"><y:ShapeNode><y:Shape shape=\\"ellipse\\"></y:Shape><y:Fill color=\\"#800080\\" transparent=\\"false\\"></y:Fill><y:NodeLabel alignment=\\"center\\" fontSize=\\"12\\" fontStyle=\\"plain\\" hasText=\\"true\\" visible=\\"true\\" width=\\"4.0\\">"+feat.name+"</y:NodeLabel></y:ShapeNode></data></node>\\\\n"
                            processedURIs[feat.id]=true
                        }
                        if("properties" in feat){
                            for(prop in feat["properties"]){
                                thetarget=feat["properties"][prop]
                                if((feat["properties"][prop]+"").startsWith("http") && !(feat["properties"][prop] in processedURIs)){
                                    resgml+="<node id=\\""+feat["properties"][prop]+"\\" uri=\\""+feat["properties"][prop]+"\\"><data key=\\"nodekey\\"><y:ShapeNode><y:Shape shape=\\"ellipse\\"></y:Shape><y:Fill color=\\"#800080\\" transparent=\\"false\\"></y:Fill><y:NodeLabel alignment=\\"center\\" fontSize=\\"12\\" fontStyle=\\"plain\\" hasText=\\"true\\" visible=\\"true\\" width=\\"4.0\\">"+feat["properties"][prop]+"</y:NodeLabel></y:ShapeNode></data></node>\\\\n"
                                    processedURIs[feat["properties"][prop]]=true
                                }else{
                                    thetarget="literal"+literalcounter
                                    resgml+="<node id=\\""+thetarget+"\\" uri=\\""+thetarget+"\\"><data key=\\"nodekey\\"><y:ShapeNode><y:Shape shape=\\"ellipse\\"></y:Shape><y:Fill color=\\"#F08080\\" transparent=\\"false\\"></y:Fill><y:NodeLabel alignment=\\"center\\" fontSize=\\"12\\" fontStyle=\\"plain\\" hasText=\\"true\\" visible=\\"true\\" width=\\"4.0\\">"+feat["properties"][prop]+"</y:NodeLabel></y:ShapeNode></data></node>\\\\n"
                                    literalcounter+=1
                                }
                                resgml+="<edge id=\\"e"+edgecounter+"\\" uri=\\""+prop+"\\" source=\\""+feat.id+"\\" target=\\""+thetarget+"\\"><data key=\\"edgekey\\"><y:PolyLineEdge><y:EdgeLabel alignment=\\"center\\" configuration=\\"AutoFlippingLabel\\" fontSize=\\"12\\" fontStyle=\\"plain\\" hasText=\\"true\\" visible=\\"true\\" width=\\"4.0\\">"+shortenURI(prop)+"</y:EdgeLabel></y:PolyLineEdge></data></edge>\\\\n"
                                edgecounter+=1
                            }
                        }
                    }
                }else if("type" in feature && feature["type"]=="Feature"){
                    if(!(feature.id in processedURIs)){
                        resgml+="<node id=\\""+feature.id+"\\" uri=\\""+feature.id+"\\"><data key=\\"nodekey\\"><y:ShapeNode><y:Shape shape=\\"ellipse\\"></y:Shape><y:Fill color=\\"#800080\\" transparent=\\"false\\"></y:Fill><y:NodeLabel alignment=\\"center\\" fontSize=\\"12\\" fontStyle=\\"plain\\" hasText=\\"true\\" visible=\\"true\\" width=\\"4.0\\">"+feature.name+"</y:NodeLabel></y:ShapeNode></data></node>\\\\n"
                        processedURIs[feature.id]=true
                    }
                    if("properties" in feature){
                        for(prop in feature["properties"]){
                            thetarget=feature["properties"][prop]
                            if((feature["properties"][prop]+"").startsWith("http") && !(feature["properties"][prop] in processedURIs)){
                                resgml+="<node id=\\""+feature["properties"][prop]+"\\" uri=\\""+feature["properties"][prop]+"\\"><data key=\\"nodekey\\"><y:ShapeNode><y:Shape shape=\\"ellipse\\"></y:Shape><y:Fill color=\\"#800080\\" transparent=\\"false\\"></y:Fill><y:NodeLabel alignment=\\"center\\" fontSize=\\"12\\" fontStyle=\\"plain\\" hasText=\\"true\\" visible=\\"true\\" width=\\"4.0\\">"+feature["properties"][prop]+"</y:NodeLabel></y:ShapeNode></data></node>\\\\n"
                                processedURIs[feature["properties"][prop]]=true
                            }else{
                                thetarget="literal"+literalcounter
                                resgml+="<node id=\\""+thetarget+"\\" uri=\\""+thetarget+"\\"><data key=\\"nodekey\\"><y:ShapeNode><y:Shape shape=\\"ellipse\\"></y:Shape><y:Fill color=\\"#F08080\\" transparent=\\"false\\"></y:Fill><y:NodeLabel alignment=\\"center\\" fontSize=\\"12\\" fontStyle=\\"plain\\" hasText=\\"true\\" visible=\\"true\\" width=\\"4.0\\">"+feature["properties"][prop]+"</y:NodeLabel></y:ShapeNode></data></node>\\\\n"
                                literalcounter+=1
                            }
                            resgml+="<edge id=\\"e"+edgecounter+"\\" uri=\\""+prop+"\\" source=\\""+feature.id+"\\" target=\\""+thetarget+"\\"><data key=\\"edgekey\\"><y:PolyLineEdge><y:EdgeLabel alignment=\\"center\\" configuration=\\"AutoFlippingLabel\\" fontSize=\\"12\\" fontStyle=\\"plain\\" hasText=\\"true\\" visible=\\"true\\" width=\\"4.0\\">"+shortenURI(prop)+"</y:EdgeLabel></y:PolyLineEdge></data></edge>\\\\n"
                            edgecounter+=1
                        }
                    }
                }
            }
        }
        resgml+="</graph>\\\\n</graphml>\\\\n"
        saveTextAsFile(resgml,"graphml")
    }


    function convertDecimalToLatLonText(D, lng){
        dir=""
        if(D<0) {
            if(lng) {
                dir="W";
            }else {
                dir="S";
            }
        }else {
            if(lng) {
                dir="E";
            }else {
                dir="N";
            }
        }
        deg=D<0?-D:D;
        min=D%1*60;
        sec=(D*60%1*6000)/100;
        return deg+"°"+min+"'"+sec+"\\""+dir;
    }

    function exportLatLonText(){
        res=""
        for(point of centerpoints){
            res+=convertDecimalToLatLonText(point["lat"],false)+" "+convertDecimalToLatLonText(point["lng"],true)+"\\\\n"
        }
        saveTextAsFile(res,"txt")
    }

    function exportGML(){
        resgml=">\\\\n"
        resgmlhead="<?xml version=\\"1.0\\" encoding=\\"UTF-8\\"?>\\\\n<gml:FeatureCollection xmlns:gml=\\"http://www.opengis.net/gml\\" "
        nscounter=0
        nsmap={}
        if(typeof(featurecolls)!=="undefined"){
            for(feature of featurecolls){
                if("features" in feature){
                    for(feat of feature["features"]){
                        resgml+="<gml:featureMember>"
                        if("properties" in feat){
                            for(prop in feat["properties"]){
                                ns=shortenURI(prop,true)
                                nsprefix=""
                                if(ns in namespaces && !(ns in nsmap)){
                                    nsmap[ns]=namespaces[ns]
                                    resgmlhead+="xmlns:"+namespaces[ns]+"=\\""+ns+"\\" "
                                }
                                if(!(ns in nsmap)){
                                    nsmap[ns]="ns"+nscounter
                                    nsprefix="ns"+nscounter
                                    resgmlhead+="xmlns:"+nsprefix+"=\\""+ns+"\\" "
                                    nscounter+=1
                                }else{
                                    nsprefix=nsmap[ns]
                                }
                                if(Array.isArray(feat["properties"][prop])){
                                    for(arritem of feat["properties"][prop]){
                                        resgml+="<"+shortenURI(prop,false,nsprefix)+">"+arritem+"</"+shortenURI(prop,false,nsprefix)+">\\\\n"
                                    }
                                }else{
                                    resgml+="<"+shortenURI(prop,false,nsprefix)+">"+feat["properties"][prop]+"</"+shortenURI(prop,false,nsprefix)+">\\\\n"
                                }
                            }
                        }
                        if("geometry" in feat){
                            resgml+="<the_geom><gml:"+feat["geometry"]["type"]+">\\\\n"
                            resgml+="<gml:pos>\\\\n"
                            if(feat["geometry"]["type"].toUpperCase()=="POINT"){
                                resgml += feat["geometry"].coordinates[0] + ' ' + feat["geometry"].coordinates[1]+'\\\\n '
                            }else{
                                feat["geometry"].coordinates.forEach(function(p,i){
                                    resgml += p[0] + ', ' + p[1] + '\\\\n '
                                })
                            }
                            resgml+="</gml:pos>\\\\n"
                            resgml+="</gml:"+feat["geometry"]["type"]+"></the_geom>\\\\n"
                        }
                        resgml+="</gml:featureMember>"
                    }
                }else if("type" in feature && feature["type"]=="Feature"){
                    resgml+="<gml:featureMember>"
                    if("properties" in feature){
                        for(prop in feature["properties"]){
                            ns=shortenURI(prop,true)
                            nsprefix=""
                            if(ns in namespaces && !(ns in nsmap)){
                                nsmap[ns]=namespaces[ns]
                                resgmlhead+="xmlns:"+namespaces[ns]+"=\\""+ns+"\\" "
                            }
                            if(!(ns in nsmap)){
                                nsmap[ns]="ns"+nscounter
                                nsprefix="ns"+nscounter
                                resgmlhead+="xmlns:"+nsprefix+"=\\""+ns+"\\" "
                                nscounter+=1
                            }else{
                                nsprefix=nsmap[ns]
                            }
                            if(Array.isArray(feature["properties"][prop])){
                                for(arritem of feature["properties"][prop]){
                                    resgml+="<"+shortenURI(prop,false,nsprefix)+">"+arritem+"</"+shortenURI(prop,false,nsprefix)+">\\\\n"
                                }
                            }else{
                                resgml+="<"+shortenURI(prop,false,nsprefix)+">"+feature["properties"][prop]+"</"+shortenURI(prop,false,nsprefix)+">\\\\n"
                            }
                        }
                    }
                    if("geometry" in feature){
                        resgml+="<the_geom><gml:"+feature["geometry"]["type"]+">\\\\n"
                        resgml+="<gml:pos>\\\\n"
                        if(feature["geometry"]["type"].toUpperCase()=="POINT"){
                            resgml += feature["geometry"].coordinates[0] + ' ' + feature["geometry"].coordinates[1]+'\\\\n '
                        }else{
                            feature["geometry"].coordinates.forEach(function(p,i){
                                resgml += p[0] + ', ' + p[1] + '\\\\n '
                            })
                        }
                        resgml+="</gml:pos>\\\\n"
                        resgml+="</gml:"+feature["geometry"]["type"]+"></the_geom>\\\\n"
                    }
                    resgml+="</gml:featureMember>"
                }
            }
        }
        resgml+="</gml:FeatureCollection>"
        saveTextAsFile(resgmlhead+resgml,"gml")
    }

    function exportKML(){
        reskml="<?xml version=\\"1.0\\" ?>\\\\n<kml xmlns=\\"http://www.opengis.net/kml/2.2\\">\\\\n<Document>"
        reskml+="<Style></Style>\\\\n"
        if(typeof(featurecolls)!=="undefined"){
            for(feature of featurecolls){
                if("features" in feature){
                    for(feat of feature["features"]){
                        reskml+="<Placemark><name>"+feat.id+"</name>"
                        if("properties" in feat){
                            reskml+="<ExtendedData>"
                            for(prop in feat["properties"]){
                                if(Array.isArray(feat["properties"][prop])){
                                    for(arritem of feat["properties"][prop]){
                                        reskml+="<Data name=\\""+prop+"\\"><displayName>"+shortenURI(prop)+"</displayName><value>"+arritem+"</value></Data>\\\\n"
                                    }
                                }else{
                                    reskml+="<Data name=\\""+prop+"\\"><displayName>"+shortenURI(prop)+"</displayName><value>"+feat["properties"][prop]+"</value></Data>\\\\n"
                                }
                            }
                            reskml+="</ExtendedData>"
                        }
                        if("geometry" in feat){
                            reskml+="<"+feat["geometry"]["type"]+">\\\\n"
                            if(feat["geometry"]["type"]=="Polygon"){
                                reskml+="<outerBoundaryIs><LinearRing>"
                            }
                            reskml+="<coordinates>\\\\n"
                            if(feat["geometry"]["type"].toUpperCase()=="POINT"){
                                reskml += feat["geometry"].coordinates[0] + ' ' + feat["geometry"].coordinates[1]+'\\\\n '
                            }else{
                                feat["geometry"].coordinates.forEach(function(p,i){
                                    reskml += p[0] + ', ' + p[1] + '\\\\n '
                                })
                            }
                            reskml+="</coordinates>\\\\n"
                            if(feat["geometry"]["type"]=="Polygon"){
                                reskml+="</LinearRing></outerBoundaryIs>"
                            }
                            reskml+="</"+feat["geometry"]["type"]+">\\\\n"
                        }
                        reskml+="</Placemark>"
                    }
                }else if("type" in feature && feature["type"]=="Feature"){
                    reskml+="<Placemark><name>"+feature.id+"</name>"
                    if("properties" in feature){
                        reskml+="<ExtendedData>"
                        for(prop in feature["properties"]){
                            if(Array.isArray(feature["properties"][prop])){
                                for(arritem of feature["properties"][prop]){
                                    reskml+="<Data name=\\""+prop+"\\"><displayName>"+shortenURI(prop)+"</displayName><value>"+arritem+"</value></Data>\\\\n"
                                }
                            }else{
                                reskml+="<Data name=\\""+prop+"\\"><displayName>"+shortenURI(prop)+"</displayName><value>"+feature["properties"][prop]+"</value></Data>\\\\n"
                            }
                        }
                        reskml+="</ExtendedData>"
                    }
                    if("geometry" in feature){
                        reskml+="<"+feature["geometry"]["type"]+">\\\\n"
                        if(feature["geometry"]["type"]=="Polygon"){
                            reskml+="<outerBoundaryIs><LinearRing>"
                        }
                        reskml+="<coordinates>\\\\n"
                        if(feature["geometry"]["type"].toUpperCase()=="POINT"){
                            reskml += feature["geometry"].coordinates[0] + ' ' + feature["geometry"].coordinates[1]+'\\\\n '
                        }else{
                            feature["geometry"].coordinates.forEach(function(p,i){
                                reskml += p[0] + ', ' + p[1] + '\\\\n '
                            })
                        }
                        reskml+="</coordinates>\\\\n"
                        if(feature["geometry"]["type"]=="Polygon"){
                            reskml+="</LinearRing></outerBoundaryIs>"
                        }
                        reskml+="</"+feature["geometry"]["type"]+">\\\\n"
                    }
                    reskml+="</Placemark>"
                }
            }
        }
        reskml+="</Document></kml>"
        saveTextAsFile(reskml,"kml")
    }

    function exportTGFGDF(sepchar,format){
        resgdf=""
        if(format=="gdf")
            resgdf="nodedef>name VARCHAR,label VARCHAR"
        uritoNodeId={}
        nodecounter=0
        nodes=""
        edges=""
        if(typeof(featurecolls)!=="undefined"){
            for(feature of featurecolls){
                if("features" in feature){
                    for(feat of feature["features"]){
                        featid=nodecounter
                        uritoNodeId[feat["id"]]=nodecounter
                        nodes+=nodecounter+sepchar+feat["id"]+"\\\\n"
                        nodecounter+=1
                        if("properties" in feat){
                            for(prop in feat["properties"]){
                                if(Array.isArray(feat["properties"][prop])){
                                        for(arritem of feat["properties"][prop]){
                                                if(!(arritem in uritoNodeId)){
                                                    uritoNodeId[arritem]=nodecounter
                                                    nodes+=nodecounter+sepchar+arritem+"\\\\n"
                                                    nodecounter+=1
                                                }
                                                edges+=featid+sepchar+uritoNodeId[arritem]+sepchar+shortenURI(prop)+"\\\\n"
                                        }
                                }else{
                                     if(!(feat["properties"][prop] in uritoNodeId)){
                                        uritoNodeId[feat["properties"][prop]]=nodecounter
                                        nodecounter+=1
                                     }
                                     edges+=featid+sepchar+uritoNodeId[feat["properties"][prop]]+sepchar+shortenURI(prop)+"\\\\n"
                                }
                            }
                        }
                    }
                }else if("type" in feature && feature["type"]=="Feature"){
                        featid=nodecounter
                        feat=feature
                        uritoNodeId[feat["id"]]=nodecounter
                        nodes+=nodecounter+sepchar+feat["id"]+"\\\\n"
                        nodecounter+=1
                        if("properties" in feat){
                            for(prop in feat["properties"]){
                                if(Array.isArray(feat["properties"][prop])){
                                        for(arritem of feat["properties"][prop]){
                                                if(!(arritem in uritoNodeId)){
                                                    uritoNodeId[arritem]=nodecounter
                                                    nodes+=nodecounter+sepchar+arritem+"\\\\n"
                                                    nodecounter+=1
                                                }
                                                edges+=featid+sepchar+uritoNodeId[arritem]+sepchar+shortenURI(prop)+"\\\\n"
                                        }
                                }else{
                                     if(!(feat["properties"][prop] in uritoNodeId)){
                                        uritoNodeId[feat["properties"][prop]]=nodecounter
                                        nodecounter+=1
                                     }
                                     edges+=featid+sepchar+uritoNodeId[feat["properties"][prop]]+sepchar+shortenURI(prop)+"\\\\n"
                                }
                          }
                    }
                }
            }
        }
        resgdf+=nodes
        if(format=="tgf"){
            resgdf+="#\\\\n"
        }else{
            resgdf+="edgedef>node1 VARCHAR,node2 VARCHAR,label VARCHAR\\\\n"
        }
        resgdf+=edges
        saveTextAsFile(resgdf,format)
    }

    function setSVGDimensions(){
        $('svg').each(function(i, obj) {
            console.log(obj)
            console.log($(obj).children().first()[0])
            if($(obj).attr("viewBox") || $(obj).attr("width") || $(obj).attr("height")){
                return
            }
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
                naturalWidth=$(obj).prev().children('img')[0].naturalWidth
                naturalHeight=$(obj).prev().children('img')[0].naturalHeight
                currentWidth=$(obj).prev().children('img')[0].width
                currentHeight=$(obj).prev().children('img')[0].height
                console.log(naturalWidth+" - "+naturalHeight+" - "+currentWidth+" - "+currentHeight)
                overlayposX = (currentWidth/naturalWidth) * minx;
                overlayposY = (currentHeight/naturalHeight) * miny;
                overlayposWidth = ((currentWidth/naturalWidth) * maxx)-overlayposX;
                overlayposHeight = ((currentHeight/naturalHeight) * maxy)-overlayposY;
                console.log(overlayposX+" - "+overlayposY+" - "+overlayposHeight+" - "+overlayposWidth)
                $(obj).css({top: overlayposY+"px", left:overlayposX+"px", position:"absolute"})
                $(obj).attr("height",overlayposHeight)
                $(obj).attr("width",overlayposWidth)
            }
        });
    }

    function exportGeoURI(){
        resuri=""
        for(point of centerpoints){
            if(typeof(epsg)!=='undefined'){
                resuri+="geo:"+point["lng"]+","+point["lat"]+";crs="+epsg+"\\\\n"
            }else{
                resuri+="geo:"+point["lng"]+","+point["lat"]+";crs=EPSG:4326\\\\n"
            }
        }
        saveTextAsFile(resuri,"geouri")
    }


    function exportWKT(){
        if(typeof(featurecolls)!=="undefined"){
            reswkt=""
            for(feature of featurecolls){
                if("features" in feature){
                    for(feat of feature["features"]){
                        reswkt+=feat["geometry"]["type"].toUpperCase()+"("
                        if(feature["geometry"]["type"].toUpperCase()=="POINT"){
                            reswkt =  reswkt + feature["geometry"].coordinates[0] + ' ' + feature["geometry"].coordinates[1]
                        }else{
                            feature["geometry"].coordinates.forEach(function(p,i){
                                if(i<feature["geometry"].coordinates.length-1) reswkt =  reswkt + p[0] + ' ' + p[1] + ', ';
                                else reswkt =  reswkt + p[0] + ' ' + p[1] + ')';
                            })
                        }
                        reswkt+=")\\\\n"
                    }
                }else if("geometry" in feature){
                        reswkt+=feature["geometry"]["type"].toUpperCase()+"("
                        if(feature["geometry"]["type"].toUpperCase()=="POINT"){
                            reswkt =  reswkt + feature["geometry"].coordinates[0] + ' ' + feature["geometry"].coordinates[1]
                        }else{
                            feature["geometry"].coordinates.forEach(function(p,i){
                                if(i<feature["geometry"].coordinates.length-1) reswkt =  reswkt + p[0] + ' ' + p[1] + ', ';
                                else reswkt =  reswkt + p[0] + ' ' + p[1] + ')';
                            })
                        }
                        reswkt+=")\\\\n"
                }
                saveTextAsFile(reswkt,"wkt")
            }
        }
    }

    function exportXYZASCII(){
        if(typeof(featurecolls)!=="undefined"){
            reswkt=""
            for(feature of featurecolls){
                if("features" in feature){
                    for(feat of feature["features"]){
                        if(feature["geometry"]["type"].toUpperCase()=="POINT"){
                            reswkt =  reswkt + feature["geometry"].coordinates[0] + ' ' + feature["geometry"].coordinates[1] + '\\\\n';
                        }else{
                            feature["geometry"].coordinates.forEach(function(p,i){
                                console.log(p)
                                reswkt =  reswkt + p[0] + ' ' + p[1] + '\\\\n';
                            })
                        }
                        reswkt+="\\\\n"
                    }
                }else if("geometry" in feature){
                        if(feature["geometry"]["type"].toUpperCase()=="POINT"){
                            reswkt =  reswkt + feature["geometry"].coordinates[0] + ' ' + feature["geometry"].coordinates[1] + '\\\\n';
                        }else{
                            feature["geometry"].coordinates.forEach(function(p,i){
                                console.log(p)
                                reswkt =  reswkt + p[0] + ' ' + p[1] + '\\\\n';
                            })
                        }
                        reswkt+="\\\\n"
                }
                saveTextAsFile(reswkt,"xyz")
            }
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
        var title=$('#title').text()
        var filename = "res."+fileext;
        if(typeof(title)!=='undefined'){
            filename=title.trim()+"."+fileext
        }
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
            downloadFile(window.location.href.replace(".html",".ttl"))
        }else if(format=="json"){
            downloadFile(window.location.href.replace(".html",".json"))
        }else if(format=="wkt"){
            exportWKT()
        }else if(format=="gml"){
            exportGML()
        }else if(format=="kml"){
            exportKML()
        }else if(format=="csv"){
            exportCSV(",",format)
        }else if(format=="tsv"){
            exportCSV("\t",format)
        }else if(format=="gdf"){
            exportTGFGDF(",",format)
        }else if(format=="graphml"){
            exportGraphML()
        }else if(format=="geouri"){
            exportGeoURI()
        }else if(format=="tgf"){
            exportTGFGDF(" ",format)
        }else if(format=="xyz"){
            exportXYZASCII()
        }else if(format=="latlon"){
            exportLatLonText()
        }
    }

    function rewriteLink(thelink){
        if(thelink==null){
            rest=search[document.getElementById('search').value].replace(baseurl,"")
        }else{
            curlocpath=window.location.href.replace(baseurl,"")
            rest=thelink.replace(baseurl,"")
        }
        if(!(rest.endsWith("/")) && !(rest.endsWith(".html"))){
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
        //console.log(rest)
        //console.log(rest.endsWith("index.html"))
        if(!rest.includes("nonns_") && !rest.endsWith(".html")){
            rest+="index.html"
        }
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

    function shortenURI(uri,getns=false,nsprefix=""){
        prefix=""
        if(typeof(uri)!="undefined"){
            for(namespace in namespaces){
                if(uri.includes(namespaces[namespace])){
                    prefix=namespace+":"
                    break
                }
            }
            if(prefix=="" && nsprefix!=""){
                prefix==nsprefix
            }
        }
        if(typeof(uri)!= "undefined" && uri.includes("#") && !getns){
            return prefix+uri.substring(uri.lastIndexOf('#')+1)
        }
        if(typeof(uri)!= "undefined" && uri.includes("/") && !getns){
            return prefix+uri.substring(uri.lastIndexOf("/")+1)
        }
        if(typeof(uri)!= "undefined" && uri.includes("#") && getns){
            return prefix+uri.substring(0,uri.lastIndexOf('#'))
        }
        if(typeof(uri)!= "undefined" && uri.includes("/") && getns){
            return prefix+uri.substring(0,uri.lastIndexOf("/"))
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


    let camera, scene, renderer, controls, axesHelper;

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


    function addRotationControls(box,geometryF,objects){
        geometryF.close();

        const rotationFolder = geometryF.addFolder("Rotation");
        rotationFolder.add(objects.rotation, 'x', 0, Math.PI).name("X").onChange(
        function(){
            yourVar = this.getValue();
            scene.traverse(function(obj){
                if(obj.type === 'Mesh'){
                    obj.rotation.x = yourVar;
                }});
        });
        rotationFolder.add(objects.rotation, 'y', 0, Math.PI).name("Y").onChange(
        function(){
            yourVar = this.getValue();
            scene.traverse(function(obj){
                if(obj.type === 'Mesh'){
                    obj.rotation.y = yourVar;
                }});
        });
        rotationFolder.add(objects.rotation, 'z', 0, Math.PI).name("Z").onChange(
        function(){
            yourVar = this.getValue();
            scene.traverse(function(obj){
                if(obj.type === 'Mesh'){
                    obj.rotation.z = yourVar;
                }});
        });

        const scaleFolder = geometryF.addFolder("Scale");
        scaleFolder.add(objects.scale, 'x', 0, 2).name("X").onChange(
        function(){
            yourVar = this.getValue();
            scene.traverse(function(obj){
                if(obj.type === 'Mesh'){
                    obj.scale.x = yourVar;
                }});
        });
        scaleFolder.add(objects.scale, 'y', 0, 2).name("Y").onChange(
        function(){
            yourVar = this.getValue();
            scene.traverse(function(obj){
                if(obj.type === 'Mesh'){
                    obj.scale.y = yourVar;
                }});
        });
        scaleFolder.add(objects.scale, 'z', 0, 2).name("Z").onChange(
        function(){
            yourVar = this.getValue();
            scene.traverse(function(obj){
                if(obj.type === 'Mesh'){
                    obj.scale.z = yourVar;
                }});
        });
    }

    function prepareAnnotationFromJSON(verts,annotations){
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
        var extrudedGeometry = new THREE.ExtrudeGeometry(svgShape, {depth: Math.abs(maxz-minz), bevelEnabled: false});
        extrudedGeometry.computeBoundingBox()
        const material = new THREE.MeshBasicMaterial( { color: 0xFFFFFF, wireframe:true } );
        const mesh = new THREE.Mesh( extrudedGeometry, material );
        if(minz<0){
            mesh.position.z = minz;
        }
        annotations.add(mesh)
        return annotations
    }

    function fitCameraToSelection(camera, controls, selection, fitOffset = 1.2) {
      size = new THREE.Vector3();
      center = new THREE.Vector3();
      box = new THREE.Box3();
      box.makeEmpty();
      for(const object of selection) {
        box.expandByObject(object);
      }

      box.getSize(size);
      box.getCenter(center );

      const maxSize = Math.max(size.x, size.y, size.z);
      const fitHeightDistance = maxSize / (2 * Math.atan(Math.PI * camera.fov / 360));
      const fitWidthDistance = fitHeightDistance / camera.aspect;
      const distance = fitOffset * Math.max(fitHeightDistance, fitWidthDistance);

      const direction = controls.target.clone()
        .sub(camera.position)
        .normalize()
        .multiplyScalar(distance);

      controls.maxDistance = distance * 10;
      controls.target.copy(center);
      if(typeof(camera)!="undefined" && camera!=null){
          camera.near = distance / 100;
          camera.far = distance * 100;
          camera.updateProjectionMatrix();       
          camera.position.copy(controls.target).sub(direction);
      }
      controls.update();
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
        annotations=new THREE.Group();
        const objects=new THREE.Group();
        console.log(verts)
        var svgShape = new THREE.Shape();
        first=true
        height=500
        width=480
        annotations=prepareAnnotationFromJSON(verts,annotations)
        const gui = new dat.GUI({autoPlace: false})
        gui.domElement.id="gui"
        $("#threejsnav").append($(gui.domElement))
        const geometryFolder = gui.addFolder("Mesh");
        geometryFolder.open();
        const lightingFolder = geometryFolder.addFolder("Lighting");
        const geometryF = geometryFolder.addFolder("Geometry");
        geometryF.open();
        renderer = new THREE.WebGLRenderer( { antialias: false } );
        renderer.setPixelRatio( window.devicePixelRatio );
        renderer.setSize( width, height );
        document.getElementById(domelement).appendChild( renderer.domElement );
        if(meshurls.length>0){
            if(meshurls[0].includes(".ply")){
                var loader = new THREE.PLYLoader();
                loader.load(meshurls[0], function(object){
                    const material = new THREE.MeshPhongMaterial({
                        color: 0xffffff,
                        flatShading: true,
                        vertexColors: THREE.VertexColors,
                        wireframe: false
                    });
                    const mesh = new THREE.Mesh(object, material);
                    objects.add(mesh);
                    scene.add(objects);
                    addRotationControls(object,geometryF,objects)
                    if(objects.children.length>0 && typeof(camera)!=="undefined" && camera!=null){
                        camera.lookAt( objects.children[0].position );
                    }
                    fitCameraToSelection(camera, controls, objects.children)
                });
            }else if(meshurls[0].includes(".obj")){
                var loader= new THREE.OBJLoader();
                loader.load(meshurls[0],function ( object ) {objects.add(object);scene.add(objects);addRotationControls(object,geometryF,objects);if(objects.children.length>0){camera.lookAt( objects.children[0].position );}fitCameraToSelection(camera, controls, objects.children)})
            }else if(meshurls[0].includes(".nxs") || meshurls[0].includes(".nxz")){
                console.log(renderer)
                var nexus_obj=new NexusObject(meshurls[0],function(){},renderNXS,renderer);
                objects.add(nexus_obj)
                scene.add(objects);
                addRotationControls(nexus_obj,geometryF,objects)
                /*if(objects.children.length>0){
                        camera.lookAt( objects.children[0].position );
                }
                fitCameraToSelection(camera, controls, objects.children)*/
            }else if(meshurls[0].includes(".gltf")){
                var loader = new THREE.GLTFLoader();
                loader.load(meshurls[0], function ( gltf )
                {
                    object = gltf.scene;
                    object.position.x = 0;
                    object.position.y = 0;
                    objects.add(object)
                    scene.add(objects);
                    addRotationControls(object,geometryF,objects)
                    if(objects.children.length>0){
                        camera.lookAt( objects.children[0].position );
                    }
                    fitCameraToSelection(camera, controls, objects.children)
                });
            }
        }
        camera = new THREE.PerspectiveCamera(90,width / height, 0.1, 2000 );
        scene.add(new THREE.AmbientLight(0x222222));
        var light = new THREE.DirectionalLight(0xffffff, 1);
        light.position.set(20, 20, 0);
        scene.add(light);
        lightingFolder.add(light.position, "x").min(-5).max(5).step(0.01).name("X Position")
        lightingFolder.add(light.position, "y").min(-5).max(5).step(0.01).name("Y Position")
        lightingFolder.add(light.position, "z").min(-5).max(5).step(0.01).name("Z Position")
        axesHelper = new THREE.AxesHelper( Math.max(1000, 1000, 1000) );
        scene.add( axesHelper );
        console.log("Depth: "+(maxz-minz))
        scene.add( annotations );
        centervec=new THREE.Vector3()
        controls = new THREE.OrbitControls( camera, renderer.domElement );
        //controls.target.set( centervec.x,centervec.y,centervec.z );
        controls.target.set( 0,0,0 );
        camera.position.x= 0
        camera.position.y= 0
        camera.position.z = 150;
        controls.maxDistance= Math.max(1000, 1000, 1000)
        controls.update();
        const updateCamera = () => {
            camera.updateProjectionMatrix();
        }
        const cameraFolder = geometryFolder.addFolder("Camera");
        cameraFolder.add (camera, 'fov', 1, 180).name('Zoom').onChange(updateCamera);
        cameraFolder.add (camera.position, 'x').min(-500).max(500).step(5).name("X Position").onChange(updateCamera);
        cameraFolder.add (camera.position, 'y').min(-500).max(500).step(5).name("Y Position").onChange(updateCamera);
        cameraFolder.add (camera.position, 'z').min(-500).max(500).step(5).name("Z Position").onChange(updateCamera);
        gui.add(objects, 'visible').name('Meshes')
        gui.add(annotations, 'visible').name('Annotations')
        gui.add(axesHelper, 'visible').name('Axis Helper')
        gui.add({"FullScreen":toggleFullScreen2}, 'FullScreen')
        document.addEventListener("fullscreenchange",function(){
            if(document.fullscreenElement){
                camera.aspect = width / height;
                camera.updateProjectionMatrix();
                renderer.setSize( width, height );
            }
        })
        if(objects.children.length>0){
            camera.lookAt( objects.children[0].position );
        }
        fitCameraToSelection(camera, controls, objects.children)
        if(meshurls.length>0 && (meshurls[0].includes(".nxs") || meshurls[0].includes(".nxz"))){
            renderNXS()
        }
        animate()
    }

    function renderNXS(){
        console.log(renderer)
        Nexus.beginFrame(renderer.getContext());
        renderer.render( scene, camera );
        Nexus.endFrame(renderer.getContext());
    }

    function animate() {
        requestAnimationFrame( animate );
        controls.update();
        renderer.render( scene, camera );
    }

    function getTextAnnoContext(){
    $('span.textanno').each(function(i, obj) {
        startindex=$(obj).attr("start").val()
        endindex=$(obj).attr("end").val()
        exact=$(obj).attr("exact").val()
        if($(obj).attr("src")){
            source=$(obj).attr("src").val()
            $.get( source, function( data ) {
                markarea=data.substring(start,end)
                counter=0
                startindex=0
                endindex=data.indexOf("\\\\n",end)
                for(line in data.split("\\\\n")){
                    counter+=line.length
                    if(counter>start){
                        startindex=counter-line.length
                        break
                    }
                }
                $(obj).html(data.substring(startindex,endindex)+"</span>".replace(markarea,"<mark>"+markarea+"</mark>"))
            });
        }
      });
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

    function formatHTMLTableForPropertyRelations(propuri,result,propicon){
        dialogcontent="<h3><img src=\\""+propicon+"\\" height=\\"25\\" width=\\"25\\" alt=\\"Instance\\"/><a href=\\""+propuri.replace('/index.json','/index.html')+"\\" target=\\"_blank\\"> "+shortenURI(propuri)+"</a></h3><table border=1 id=classrelationstable><thead><tr><th>Incoming Concept</th><th>Relation</th><th>Outgoing Concept</th></tr></thead><tbody>"
        console.log(result)
        if("from" in result){
            for(instance in result["from"]){
        //
                    if(result["from"][instance]=="instancecount"){
                        continue;
                    }
                    dialogcontent+="<tr><td><img onclick=\\"getClassRelationDialog($('#jstree').jstree(true).get_node('"+result["from"][instance]+"'))\\" src=\\""+iconprefix+"class.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Class\\"/><a href=\\""+result["from"][instance]+"\\" target=\\"_blank\\">"+shortenURI(result["from"][instance])+"</a></td>"
                    dialogcontent+="<td><img src=\\""+propicon+"\\" height=\\"25\\" width=\\"25\\" alt=\\"Instance\\"/><a href=\\""+propuri+"\\" target=\\"_blank\\">"+shortenURI(propuri)+"</a></td><td></td></tr>"
               // }
            }
        }
        if("to" in result){
            for(instance in result["to"]){
                //for(instance in result["to"][res]){
                    if(result["to"][instance]=="instancecount"){
                        continue;
                    }
                    dialogcontent+="<tr><td></td><td><img src=\\""+propicon+"\\" height=\\"25\\" width=\\"25\\" alt=\\"Class\\"/><a href=\\""+propuri+"\\" target=\\"_blank\\">"+shortenURI(propuri)+"</a></td>"
                    dialogcontent+="<td><img onclick=\\"getClassRelationDialog($('#jstree').jstree(true).get_node('"+result["to"][instance]+"'))\\" src=\\""+iconprefix+"class.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Instance\\"/><a href=\\""+result["to"][instance]+"\\" target=\\"_blank\\">"+shortenURI(result["to"][instance])+"</a></td></tr>"
               // }
            }
        }
        dialogcontent+="</tbody></table>"
        dialogcontent+="<button style=\\"float:right\\" id=\\"closebutton\\" onclick='document.getElementById(\\"classrelationdialog\\").close()'>Close</button>"
        return dialogcontent
    }

    function determineTableCellLogo(uri){
        result="<td>"
        logourl=""
        finished=false
        if(uri in labelproperties){
            result+="<img onclick=\\"getPropRelationDialog('"+uri+"','"+iconprefix+"labelproperty.png')\\" src=\\""+iconprefix+"labelproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Label Property\\"/>"
            logourl=iconprefix+"labelproperty.png"
            finished=true
        }
        if(!finished){
            for(ns in annotationnamespaces){
                if(uri.includes(annotationnamespaces[ns])){
                    result+="<img onclick=\\"getPropRelationDialog('"+uri+"','"+iconprefix+"annotationproperty.png')\\" src=\\""+iconprefix+"annotationproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Annotation Property\\"/>"
                    logourl=iconprefix+"annotationproperty.png"
                    finished=true
                }
            }
        }
        if(!finished && uri in geoproperties && geoproperties[uri]=="ObjectProperty"){
            result+="<img onclick=\\"getPropRelationDialog('"+uri+"','"+iconprefix+"geoobjectproperty.png')\\" src=\\""+iconprefix+"geoobjectproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Geo Object Property\\"/>"
            logourl=iconprefix+"geoobjectproperty.png"
        }else if(!finished && uri in geoproperties && geoproperties[uri]=="DatatypeProperty"){
            result+="<img onclick=\\"getPropRelationDialog('"+uri+"','"+iconprefix+"geodatatypeproperty.png')\\" src=\\""+iconprefix+"geodatatypeproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Geo Datatype Property\\"/>"
            logourl=iconprefix+"geodatatypeproperty.png"
        }else if(!finished){
            result+="<img onclick=\\"getPropRelationDialog('"+uri+"','"+iconprefix+"objectproperty.png')\\" src=\\""+iconprefix+"objectproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Object Property\\"/>"
            logourl=iconprefix+"objectproperty.png"
        }
        result+="<a href=\\""+uri+"\\" target=\\"_blank\\">"+shortenURI(uri)+"</a></td>"
        return [result,logourl]
    }

    function formatHTMLTableForClassRelations(result,nodeicon,nodelabel,nodeid){
        dialogcontent=""
        if(nodelabel.includes("[")){
            nodelabel=nodelabel.substring(0,nodelabel.lastIndexOf("[")-1)
        }
        dialogcontent="<h3><img src=\\""+nodeicon+"\\" height=\\"25\\" width=\\"25\\" alt=\\"Instance\\"/><a href=\\""+nodeid.replace('/index.json','/index.html')+"\\" target=\\"_blank\\"> "+nodelabel+"</a></h3><table border=1 id=classrelationstable><thead><tr><th>Incoming Concept</th><th>Incoming Relation</th><th>Concept</th><th>Outgoing Relation</th><th>Outgoing Concept</th></tr></thead><tbody>"
        if("from" in result){
            for(res in result["from"]){
                for(instance in result["from"][res]){
                    if(instance=="instancecount"){
                        continue;
                    }
                    dialogcontent+="<tr><td><img onclick=\\"getClassRelationDialog($('#jstree').jstree(true).get_node('"+instance+"'))\\" src=\\""+iconprefix+"class.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Class\\"/><a href=\\""+instance+"\\" target=\\"_blank\\">"+shortenURI(instance)+"</a></td>"
                    dialogcontent+=determineTableCellLogo(res)[0]
                    dialogcontent+="<td><img onclick=\\"getClassRelationDialog($('#jstree').jstree(true).get_node('"+nodeid+"'))\\" src=\\""+nodeicon+"\\" height=\\"25\\" width=\\"25\\" alt=\\"Instance\\"/><a href=\\""+nodeid+"\\" target=\\"_blank\\">"+nodelabel+"</a></td><td></td><td></td></tr>"
                }
            }
        }
        if("to" in result){
            for(res in result["to"]){
                for(instance in result["to"][res]){
                    if(instance=="instancecount"){
                        continue;
                    }
                    dialogcontent+="<tr><td></td><td></td><td><img onclick=\\"getClassRelationDialog($('#jstree').jstree(true).get_node('"+nodeid+"'))\\" src=\\""+nodeicon+"\\" height=\\"25\\" width=\\"25\\" alt=\\"Instance\\"/><a href=\\""+nodeid+"\\" target=\\"_blank\\">"+nodelabel+"</a></td>"
                    dialogcontent+=determineTableCellLogo(res)[0]
                    dialogcontent+="<td><img onclick=\\"getClassRelationDialog($('#jstree').jstree(true).get_node('"+instance+"'))\\"  src=\\""+iconprefix+"class.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Class\\"/><a href=\\""+instance+"\\" target=\\"_blank\\">"+shortenURI(instance)+"</a></td></tr>"
                }
            }
        }
        dialogcontent+="</tbody></table>"
        dialogcontent+="<button style=\\"float:right\\" id=\\"closebutton\\" onclick='document.getElementById(\\"classrelationdialog\\").close()'>Close</button>"
        return dialogcontent
    }

    listthreshold=5

    function formatHTMLTableForResult(result,nodeicon,nodetype){
        dialogcontent=""
        dialogcontent="<h3><img src=\\""+nodeicon+"\\" height=\\"25\\" width=\\"25\\" alt=\\"Instance\\"/><a href=\\""+nodeid.replace('/index.json','/index.html')+"\\" target=\\"_blank\\"> "+nodelabel+"</a></h3><table border=1 id=dataschematable><thead><tr><th>Type</th><th>Relation</th><th>Value</th></tr></thead><tbody>"
        for(res in result){
            console.log(result)
            console.log(result[res])
            console.log(result[res].size)
            dialogcontent+="<tr>"
            detpropicon=""
            if(res in geoproperties && geoproperties[res]=="ObjectProperty"){
                dialogcontent+="<td><img src=\\""+iconprefix+"geoobjectproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Geo Object Property\\"/>Geo Object Property</td>"
                detpropicon=iconprefix+"geoobjectproperty.png"
            }else if((result[res][0]+"").startsWith("http")){
                dialogcontent+="<td><img src=\\""+iconprefix+"objectproperty.png\\" height=\\"25\\" width=\\"25\\" alt=\\"Object Property\\"/>Object Property</td>"
                detpropicon=iconprefix+"objectproperty.png"
            }else{
                finished=false
                ress=determineTableCellLogo(res)
                dialogcontent+=ress[0]
                detpropicon=ress[1]
            }
            dialogcontent+="<td><a href=\\""+res+"\\" target=\\"_blank\\">"+shortenURI(res)+"</a> <a href=\\"#\\" onclick=\\"getPropRelationDialog('"+res+"','"+detpropicon+"')\\">[x]</a></td>"
            if(Object.keys(result[res]).length>1){
                dialogcontent+="<td>"
                if(result[res].length>listthreshold){
                    dialogcontent+="<details><summary>"+result[res].length+" values</summary>"
                }
                dialogcontent+="<ul>"
                for(resitem in result[res]){
                    if(!(nodetype.includes("class"))) {
                        if ((result[res][resitem] + "").trim().startsWith("http")) {
                            dialogcontent += "<li><a href=\\"" + rewriteLink(result[res][resitem]) + "\\" target=\\"_blank\\">" + shortenURI(result[res][resitem]) + "</a> [" + result[res][resitem] + "]</li>"
                        } else if (resitem != "instancecount") {
                            dialogcontent += "<li>" + result[res][resitem] + "</li>"
                        }
                    }else{
                        if ((resitem+ "").trim().startsWith("http")) {
                            dialogcontent += "<li><a href=\\"" + rewriteLink(resitem) + "\\" target=\\"_blank\\">" + shortenURI(resitem) + "</a></li>"
                        } else if (resitem != "instancecount") {
                            dialogcontent += "<li>" + result[res][resitem] + "</li>"
                        }
                    }
                }
                dialogcontent+="</ul>"
                if(result[res].length>listthreshold){
                    dialogcontent+="</details>"
                }
                dialogcontent+="</td>"        
            }else if((Object.keys(result[res])[0]+"").startsWith("http") || (result[res][Object.keys(result[res])[0]]+"").startsWith("http")){
                if(!(nodetype.includes("class"))) {
                    dialogcontent+="<td><a href=\\""+rewriteLink(result[res][Object.keys(result[res])[0]]+"")+"\\" target=\\"_blank\\">"+shortenURI(result[res][Object.keys(result[res])[0]]+"")+"</a></td>"
                }else{
                    dialogcontent+="<td><a href=\\""+rewriteLink(Object.keys(result[res])[0]+"")+"\\" target=\\"_blank\\">"+shortenURI(Object.keys(result[res])[0]+"")+"</a></td>"
                }
            }else if(Object.keys(result[res])[0]!="instancecount"){
                if(!(nodetype.includes("class"))) {
                    dialogcontent += "<td>" + result[res][Object.keys(result[res])[0]] + "</td>"
                }else{
                    dialogcontent += "<td>" + Object.keys(result[res])[0] + "</td>"
                }
            }else{
                dialogcontent+="<td></td>"
            }
            dialogcontent+="</tr>"
        }
        dialogcontent+="</tbody></table>"
        dialogcontent+="<button style=\\"float:right\\" id=\\"closebutton\\" onclick='document.getElementById(\\"dataschemadialog\\").close()'>Close</button>"
        return dialogcontent
    }

    function getClassRelationDialog(node){
         nodeid=rewriteLink(normalizeNodeId(node)).replace(".html",".json")
         nodelabel=node.text
         nodetype=node.type
         nodeicon=node.icon
         props={}
         if("data" in node){
            props=node.data
         }
         console.log(nodetype)
         if(nodetype=="class" || nodetype=="geoclass" || nodetype=="collectionclass" || nodetype=="halfgeoclass"){
            console.log(props)
            dialogcontent=formatHTMLTableForClassRelations(props,nodeicon,nodelabel,nodeid)
            document.getElementById("classrelationdialog").innerHTML=dialogcontent
            $('#classrelationstable').DataTable();
            document.getElementById("classrelationdialog").showModal();
         }
    }

    function getPropRelationDialog(propuri,propicon){
         dialogcontent=formatHTMLTableForPropertyRelations(propuri,proprelations[propuri],propicon)
         console.log(dialogcontent)
         document.getElementById("classrelationdialog").innerHTML=dialogcontent
         $('#classrelationstable').DataTable();
         document.getElementById("classrelationdialog").showModal();
    }

    function normalizeNodeId(node){
        if(node.id.includes("_suniv")){
            return node.id.replace(/_suniv[0-9]+_/, "")
        }
        return node.id
    }

    function getDataSchemaDialog(node){
         nodeid=rewriteLink(normalizeNodeId(node)).replace(".html",".json")
         nodelabel=node.text
         nodetype=node.type
         nodeicon=node.icon
         props={}
         if("data" in node){
            props=node.data
         }
         console.log(nodetype)
         if(nodetype=="class" || nodetype=="halfgeoclass" || nodetype=="geoclass" || node.type=="collectionclass"){
            console.log(props)
            dialogcontent=formatHTMLTableForResult(props["to"],nodeicon,nodetype)
            document.getElementById("dataschemadialog").innerHTML=dialogcontent
            $('#dataschematable').DataTable();
            document.getElementById("dataschemadialog").showModal();
         }else{
             $.getJSON(nodeid, function(result){
                dialogcontent=formatHTMLTableForResult(result,nodeicon,nodetype)
                document.getElementById("dataschemadialog").innerHTML=dialogcontent
                $('#dataschematable').DataTable();
                document.getElementById("dataschemadialog").showModal();
              });
        }
    }

    iconprefix="https://cdn.jsdelivr.net/gh/i3mainz/geopubby@master/public/icons/"

    function setupJSTree(){
        console.log("setupJSTree")
        if(iconprefixx!=""){
            iconprefix=iconprefixx
        }
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
        tree["types"]={
                "default": {"icon": iconprefix+"instance.png"},
                "class": {"icon": iconprefix+"class.png"},
                "geoclass": {"icon": iconprefix+"geoclass.png","valid_children":["class","halfgeoclass","geoclass","geoinstance"]},
                "halfgeoclass": {"icon": iconprefix+"halfgeoclass.png"},
                "collectionclass": {"icon": iconprefix+"collectionclass.png"},
                "geocollection": {"icon": iconprefix+"geometrycollection.png"},
                "featurecollection": {"icon": iconprefix+"featurecollection.png"},
                "instance": {"icon": iconprefix+"instance.png"},
                "geoinstance": {"icon": iconprefix+"geoinstance.png"}
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
                    "icon": iconprefix+"searchclass.png",
                    "action": function (obj) {
                        newlink=normalizeNodeId(node)
                        var win = window.open(newlink, '_blank');
                        win.focus();
                    }
                },
                "copyuriclipboard":{
                    "separator_before": false,
                    "separator_after": false,
                    "label": "Copy URI to clipboard",
                    "icon": iconprefix+thelinkpart+"link.png",
                    "action":function(obj){
                        copyText=normalizeNodeId(node)
                        navigator.clipboard.writeText(copyText);
                    }
                },
                "discoverrelations":{
                    "separator_before": false,
                    "separator_after": false,
                    "label": "Discover "+node.type+" relations",
                    "icon": iconprefix+thelinkpart+"link.png",
                    "action":function(obj){
                        console.log("class relations")
                        if(node.type=="class" || node.type=="halfgeoclass" || node.type=="geoclass" || node.type=="collectionclass"){
                            getClassRelationDialog(node)
                        }
                    }
                },
                "loaddataschema": {
                    "separator_before": false,
                    "separator_after": false,
                    "icon": iconprefix+node.type+"schema.png",
                    "label": "Load dataschema for "+node.type,
                    "action": function (obj) {
                        console.log(node)
                        console.log(node.id)
                        console.log(baseurl)
                        if(node.id.includes(baseurl)){
                            getDataSchemaDialog(node)
                        }else if(node.type=="class" || node.type=="halfgeoclass" || node.type=="geoclass" || node.type=="collectionclass"){
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
                console.log(node[0].id)
                console.log(normalizeNodeId(node[0]))
                followLink(normalizeNodeId(node[0]))
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

    function toggleFullScreen2(){
        toggleFullScreen("threejs",true)
    }

    function toggleFullScreen(elementid,threejs=false) {
      if (!document.fullscreenElement) {
        document.getElementById(elementid).requestFullscreen();
        if(threejs){
            var elem = document.getElementById(elementid);
            var sceneWidth = window.innerWidth;
            var sceneHeight = elem.offsetHeight;
            camera.aspect = sceneWidth / sceneHeight;
            camera.updateProjectionMatrix();
            renderer.setSize( sceneWidth, sceneHeight );
        }
      } else if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }

    function restyleLayer(propertyName,geojsonLayer) {
        geojsonLayer.eachLayer(function(featureInstanceLayer) {
            propertyValue = featureInstanceLayer.feature.properties[propertyName];

            // Your function that determines a fill color for a particular
            // property name and value.
            var myFillColor = getColor(propertyName, propertyValue);

            featureInstanceLayer.setStyle({
                fillColor: myFillColor,
                fillOpacity: 0.8,
                weight: 0.5
            });
        });
    }

    function createColorRangeByAttribute(propertyName,geojsonlayer){
        var valueset={}
        var minamount=999999,maxamount=-999999
        var amountofrelevantitems=0
        var stringitems=0
        var numberitems=0
        var amountofitems=geojsonlayer.size()
        var maxColors=8
        for(feat of geojsonlayer){
            if(propertyName in feat["properties"]){
                if(!(feat["properties"][propertyName] in valueset)){
                    valueset[feat["properties"][propertyName]]=0
                }
                valueset[feat["properties"][propertyName]]+=1
                if(isNaN(feat["properties"][propertyName])){
                    stringitems+=1
                }else{
                    numberitems+=1
                    numb=Number(feat["properties"][propertyName])
                    if(numb<minamount){
                        minamount=numb
                    }
                    if(numb>maxamount){
                        maxamount=numb
                    }
                }
                amountofrelevantitems+=1
            }else{
                if(!("undefined" in valueset)){
                    valueset["undefined"]=0
                }
                valueset["undefined"]+=1
            }
        }
        if(numberitems===amountofrelevantitems){
            myrange=maxamount-minamount
            myrangesteps=myrange/maxColors
            curstep=minamount
            while(curstep<maxamount){
                curstepstr=(curstep+"")
                rangesByAttribute[propertyName]={cursteps:{"min":curstep,"max":curstep+myrangesteps,"label":"["+curstep+"-"+curstep+myrangesteps+"]"}}
                curstep+=myrangesteps
            }
        }else if(stringitems<amountofrelevantitems){

        }else if(stringitems===amountofrelevantitems){

        }
    }

function generateLeafletPopup(feature, layer){
    var popup="<b>"
    if("name" in feature && feature.name!=""){
        popup+="<a href=\""+rewriteLink(feature.id)+"\" class=\"footeruri\" target=\"_blank\">"+feature.name+"</a></b><br/><ul>"
    }else{
        popup+="<a href=\""+rewriteLink(feature.id)+"\" class=\"footeruri\" target=\"_blank\">"+feature.id.substring(feature.id.lastIndexOf('/')+1)+"</a></b><br/><ul>"
    }
    for(prop in feature.properties){
        popup+="<li>"
        if(prop.startsWith("http")){
            if(prop.includes("#")){
               popup+="<a href=\""+prop+"\" target=\"_blank\">"+prop.substring(prop.lastIndexOf('#')+1)+"</a>"
            }else{
               popup+="<a href=\""+prop+"\" target=\"_blank\">"+prop.substring(prop.lastIndexOf('/')+1)+"</a>"
            }
        }else{
            popup+=prop
        }
        popup+=" : "
        if(Array.isArray(feature.properties[prop]) && feature.properties[prop].length>1){
            popup+="<ul>"
            for(item of feature.properties[prop]){
                popup+="<li>"
                if((item+"").startsWith("http")){
                    if((item+"").includes("#")){
                        popup+="<a href=\""+item+"\" target=\"_blank\">"+item.substring(item.lastIndexOf('#')+1)+"</a>"
                    }else{
                        popup+="<a href=\""+item+"\" target=\"_blank\">"+item.substring(item.lastIndexOf('/')+1)+"</a>"
                    }
                }else{
                    popup+=item
                }
                popup+="</li>"
            }
            popup+="</ul>"
        }else if(Array.isArray(feature.properties[prop]) && (feature.properties[prop][0]+"").startsWith("http")){
            if(feature.properties[prop][0].includes("#")){
              popup+="<a href=\""+rewriteLink(feature.properties[prop][0])+"\" target=\"_blank\">"+feature.properties[prop][0].substring(feature.properties[prop][0].lastIndexOf('#')+1)+"</a>"
            }else{
              popup+="<a href=\""+rewriteLink(feature.properties[prop][0])+"\" target=\"_blank\">"+feature.properties[prop][0].substring(feature.properties[prop][0].lastIndexOf('/')+1)+"</a>"
            }
        }else{
            if((feature.properties[prop]+"").startsWith("http")){
                    if((feature.properties[prop]+"").includes("#")){
                        popup+="<a href=\""+(feature.properties[prop]+"")+"\" target=\"_blank\">"+(feature.properties[prop]+"").substring((feature.properties[prop]+"").lastIndexOf('#')+1)+"</a>"
                    }else{
                        popup+="<a href=\""+(feature.properties[prop]+"")+"\" target=\"_blank\">"+(feature.properties[prop]+"").substring((feature.properties[prop]+"").lastIndexOf('/')+1)+"</a>"
                    }
            }else{
                popup+=feature.properties[prop]+""
            }
        }
        popup+="</li>"
    }
    popup+="</ul>"
    return popup
}

    function fetchLayersFromList(thelist){
        fcolls=[]
        for(url in thelist){
            $.ajax({
                url:thelist[url],
                dataType : 'json',
                async : false,
                success : function(data) {
                    fcolls.push(data)
                }
            });
        }
        return fcolls
    }

    var centerpoints=[]

    function setupLeaflet(baselayers,epsg,baseMaps,overlayMaps,map,featurecolls,dateatt="",ajax=true){
        if(ajax){
            featurecolls=fetchLayersFromList(featurecolls)
        }
        if(typeof (baselayers) === 'undefined' || baselayers===[]){
            basemaps["OSM"]=L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'})
            baseMaps["OSM"].addTo(map);
        }else{
            first=true
            for(bl in baselayers){
                if("type" in baselayers[bl] && baselayers[bl]["type"]==="wms") {
                    if("layername" in baselayers[bl]){
                        baseMaps[bl] = L.tileLayer.wms(baselayers[bl]["url"],{"layers":baselayers[bl]["layername"]})
                    }else{
                        baseMaps[bl] = L.tileLayer.wms(baselayers[bl]["url"])
                    }

                }else if(!("type" in baselayers[bl]) || baselayers[bl]["type"]==="tile"){
                    baseMaps[bl]=L.tileLayer(baselayers[bl]["url"])
                }
                if(first) {
                    baseMaps[bl].addTo(map);
                    first = false
                }
            }
        }
        L.control.scale({
        position: 'bottomright',
        imperial: false
        }).addTo(map);
        L.Polygon.addInitHook(function () {
            this._latlng = this._bounds.getCenter();
        });
        L.Polygon.include({
            getLatLng: function () {
                return this._latlng;
            },
            setLatLng: function () {} // Dummy method.
        });
        var bounds = L.latLngBounds([]);
        first=true
        counter=1
        for(feature of featurecolls){
            var markercluster = L.markerClusterGroup.layerSupport({})
            if(epsg!="" && epsg!="EPSG:4326" && epsg in epsgdefs){
                feature=convertGeoJSON(feature,epsgdefs[epsg],null)
            }
            layerr=L.geoJSON.css(feature,{
            pointToLayer: function(feature, latlng){
                          var greenIcon = new L.Icon({
                            iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-black.png',
                            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                            iconSize: [25, 41],iconAnchor: [12, 41], popupAnchor: [1, -34],shadowSize: [41, 41]
                        });
                        return L.marker(latlng, {icon: greenIcon});
            },onEachFeature: function (feature, layer) {layer.bindPopup(generateLeafletPopup(feature, layer))}})
            layername="Content "+counter
            if("name" in feature) {
                layername = feature["name"]
            }else {
                counter += 1
            }
            markercluster.checkIn(layerr);
            overlayMaps[layername]=L.featureGroup.subGroup(markercluster,[layerr])
            if(first) {
                overlayMaps[layername].addTo(map);
                var layerBounds = layerr.getBounds();
                bounds.extend(layerBounds);
                map.fitBounds(bounds);
                first = false
            }
            centerpoints.push(layerr.getBounds().getCenter());
        }
        layercontrol=L.control.layers(baseMaps,overlayMaps).addTo(map)
        if(dateatt!=null && dateatt!="" && dateatt!="[]" && dateatt!=[]){
            var sliderControl = L.control.sliderControl({
                position: "bottomleft",
                layer: layerr,
                range: true,
                rezoom: 10,
                showAllOnStart: true,
                timeAttribute: dateatt
            });
            map.addControl(sliderControl);
            sliderControl.options.markers.sort(function (a, b) {
                return (a.properties[dateatt] > b.properties[dateatt]);
            });
            sliderControl.startSlider();
        }
        markercluster.addTo(map)
    }
    """,
        "stylesheet": """
    html { margin: 0; padding: 0; }
    body { font-family: sans-serif; font-size: 80%; margin: 0; padding: 1.2em 2em; }
    #rdficon { float: right; position: relative; top: -28px; }
    #header { border-bottom: 2px solid #696; margin: 0 0 1.2em; padding: 0 0 0.3em; }
    #footer { border-top: 2px solid #696; margin: 1.2em 0 0; padding: 0.3em 0 0; }
    .carousel-center {margin:auto;}
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
    #graph{
        background: #fff;
        border: 1px solid grey;
         position: relative;
        display: inline-block;
        width:100%;
        overflow: hidden;
    }
    #content {
        margin: 20px;
        text-align: center;
    }
    details > pre {
      background-color: #f5f5f5;
      padding: 4px;
      margin: 0;
      box-shadow: 1px 1px 2px #bbbbbb;
    }
    #reset {
        float: right;
        position: absolute;
        right: 5px;
        top: 5px;
    }
    #distanceSlider {
        float: right;
        position: absolute;
        right: 5px;
        bottom: 5px;
    }
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
    body { background: %%maincolorcode%%; }
    table.description .container > td { background: #c0e2c0; padding: 0.2em 0.8em; }
    table.description .even td { background: %%tablecolorcode%%; }
    table.description .odd td { background: #f0fcf0; }
    .image { background: white; text-align:center; width:100% margin: 0 1.5em 1.5em 0; padding: 2px; }
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
    }""",

        "htmltemplate": """<html about="{{subject}}" itemscope itemid="{{subject}}" id="subject"><head><title>{{toptitle}}</title><meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" type="text/css" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css" />
<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.12.1/css/jquery.dataTables.min.css" />
<link rel="stylesheet" type="text/css" href="https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" />
<link rel="stylesheet" href="https://code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css" />
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.1.1/themes/default/style.min.css" />
<link rel="stylesheet" type="text/css" href="{{stylepath}}" />
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script><script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script><script src="https://cdn.datatables.net/1.12.1/js/jquery.dataTables.min.js"></script>
<script src="{{scriptfolderpath}}"></script><script src="{{classtreefolderpath}}"></script><script src="{{proprelationpath}}"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.3.14/jstree.min.js"></script><script src="https://cdn.jsdelivr.net/npm/rdflib@2.2.19/dist/rdflib.min.js"></script>
<script type="text/javascript" src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/js/bootstrap.bundle.min.js"></script>
<script src="{{startscriptpath}}"></script></head>
<div id="mySidenav" class="sidenav" style="overflow:auto;"><a href="javascript:void(0)" class="closebtn" onclick="closeNav()">&times;</a>
  GeoClasses: <input type="checkbox" id="geoclasses"/><br/>
  Search:<input type="text" id="classsearch"><br/><div id="jstree"></div>
</div><script>var indexpage={{indexpage}}; var baseurl="{{baseurl}}"; var iconprefixx="{{iconprefixx}}";
var relativedepth={{relativedepth}}</script><body><div id="header">{{logo}}<h1 id="title">{{title}}</h1></div><div class="page-resource-uri"><a href="{{subject}}">{{subject}}</a> <b>powered by Static GeoPubby</b> generated using the <a style="color:blue;font-weight:bold" target="_blank" href="{{versionurl}}">{{version}}</a></div>
</div><div id="rdficon"><span style="font-size:30px;cursor:pointer" onclick="openNav()">&#9776;</span></div> <div class="search"><div class="ui-widget">Search: <input id="search" size="25"><button id="gotosearch" onclick="followLink()">Go</button><b>Download Options:</b>&nbsp;Format:<select id="format" onchange="changeDefLink()">{{exports}}</select><a id="formatlink" href="#" target="_blank"><svg width="1em" height="1em" viewBox="0 0 16 16" class="bi bi-info-circle-fill" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm.93-9.412l-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM8 5.5a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"/></svg></a>&nbsp;
<button id="downloadButton" onclick="download()">Download</button><a href="{{relativepath}}/sparql.html?endpoint={{deploypath}}/index.ttl&query=SELECT%20?sub%20?pred%20?obj%20%0AWHERE%20%7B%0A%20BIND(%3C{{subjectencoded}}%3E%20AS%20?sub)%20%0A?sub%20?pred%20?obj%20.%20%0A%7D%0A">Query</a>{{bibtex}}<br/>{{nonnslink}}</div></div><dialog id="classrelationdialog" width="500" height="500" modal="true"></dialog><dialog id="dataschemadialog" width="500" height="500" modal="true"></dialog>
<div class="container-fluid"><div class="row-fluid" id="main-wrapper">
    """,

        "imagecarouselheader": """<div id="imagecarousel" class="carousel slide lazy" data-ride="carousel"><div class="carousel-inner">""",

        "imagecarouselfooter": """</div> <a class="carousel-control-prev" href="#carouselExampleControls" role="button" data-slide="prev">
        <span class="carousel-control-prev-icon" aria-hidden="true"></span>
        <span class="sr-only">Previous</span>
      </a>
      <a class="carousel-control-next" href="#carouselExampleControls" role="button" data-slide="next">
        <span class="carousel-control-next-icon" aria-hidden="true"></span>
        <span class="sr-only">Next</span>
      </a></div>""",

        "imagestemplate": """<div class="{{carousel}}" width="100%">
    <a href="{{image}}" target=\"_blank\"><img src="{{image}}" style="max-width:485px;max-height:500px" alt="{{image}}" title="{{imagetitle}}" /></a>
    </div>
    """,

        "imageswithannotemplate": """<div class="{{carousel}}" width="100%">
    <a href=\"{{image}}\" target=\"_blank\"><img src="{{image}}" style="max-width:485px;max-height:500px" alt="{{image}}" title="{{imagetitle}}" /></a>
    {{svganno}}
    </div>
    """,

        "imagestemplatesvg": """<div class="{{carousel}}" style="max-width:485px;max-height:500px">
    {{image}}
    </div>
    """,

        "videotemplate": """
    <div class="video">
    <video width="320" height="240" controls>
      <source src="{{video}}">
    Your browser does not support the video tag.
    </video>
    </div>
    """,

        "audiotemplate": """
    <div class="audio">
    <audio controls>
      <source src="{{audio}}">
    Your browser does not support the audio element.
    </audio>
    </div>
    """,

        "threejstemplate": """
    <script src="https://cdn.jsdelivr.net/npm/three/build/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three/examples/js/controls/TrackballControls.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three/examples/js/loaders/PLYLoader.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three/examples/js/loaders/GLTFLoader.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three/examples/js/loaders/OBJLoader.js"></script>
    <script src="{{relativepath}}/js/nexus.js"></script>
    <script src="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/nexus@master/html/js/nexus_three.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/threex.domevents@1.0.1/threex.domevents.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/dat-gui/0.7.9/dat.gui.min.js"></script>
    <div id="wrapper" style="display: flex;"><div id="threejs" class="threejscontainer" style="max-width:485px;max-height:500px"></div><div id="threejsnav" style="flex: 1;"></div></div>
    <script>$(document).ready(function(){initThreeJS('threejs',parseWKTStringToJSON("{{wktstring}}"),{{meshurls}})})</script>
    """,

        "3dtemplate": """<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/cnr-isti-vclab/3DHOP@4.3/minimal/stylesheet/3dhop.css"/>
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
    start3dhop("{{meshurl}}","{{meshformat}}")});</script>""",

        "nongeoexports": """
    <option value="csv">Comma Separated Values (CSV)</option>
    <option value="geojson">(Geo)JSON</option>
    <option value="json">JSON-LD</option>
    <option value="tgf">Trivial Graph Format (TGF)</option>
    <option value="ttl" selected>Turtle (TTL)</option>
    """,

        "geoexports": """
    <option value="csv">Comma Separated Values (CSV)</option>
    <option value="geojson">(Geo)JSON</option>
    <option value="tgf">Trivial Graph Format (TGF)</option>
    <option value="ttl" selected>Turtle (TTL)</option>
    <option value="wkt">Well-Known-Text (WKT)</option>
    """,

        "sparqltemplate": """<link rel="stylesheet" type="text/css" href="https://unpkg.com/@triply/yasgui/build/yasgui.min.css" />
<script src="https://unpkg.com/@triply/yasgui/build/yasgui.min.js"></script>
<script src="https://rdf.js.org/comunica-browser/versions/v2/engines/query-sparql/comunica-browser.js"></script>
<div id="yasgui"><button id="query" onclick="queryFile()" class="yasqe_queryButton query_valid"><div class="svgImg queryIcon"><svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" height="81.9" width="72.9" version="1.1" y="0px" x="0px" viewBox="0 0 72.900002 81.900002" aria-hidden="true"><path id="queryIcon" d="m69.6 35.2-60.3-34.3c-2.2-1.2-4.4-1.2-6.4 0s-2.9 3.4-2.9 5.6v68.8c0 2.2 1.2 4.4 2.9 5.6 1 0.5 2.2 1 3.4 1s2.2-0.5 2.9-1l60.3-34.3c2.2-1.2 3.4-3.4 3.4-5.6s-1.1-4.3-3.3-5.8z"></path><path id="loadingIcon" d="m61.184 36.167-48.73-27.719c-1.7779-0.96976-3.5558-0.96976-5.172 0-1.6163 0.96976-2.3436 2.7476-2.3436 4.5255v55.599c0 1.7779 0.96976 3.5558 2.3436 4.5255 0.80813 0.40407 1.7779 0.80813 2.7476 0.80813 0.96975 0 1.7779-0.40406 2.3436-0.80813l48.73-27.719c1.7779-0.96976 2.7476-2.7476 2.7476-4.5255s-0.88894-3.475-2.6668-4.6872z" fill="none"></path></svg></div></button>
</div> 
<script language="JavaScript">
class Geo {
    // A priority value. If multiple plugin support rendering of a result, this value is used
    // to select the correct plugin
    priority = 10;

    // Whether to show a select-button for this plugin
    hideFromSelection = false;

    constructor(yasr) {
        this.yasr = yasr;
    }

    // Draw the resultset.
    draw() {
        const el = document.createElement("div");
        el.setAttribute("id", "map");
        el.setAttribute("class", "leaflet leaflet-container leaflet-touch leaflet-fade-anim leaflet-touch-zoom");
        this.yasr.resultsEl.appendChild(el);
		var wkt = new Wkt.Wkt();
        for (var key in this.yasr.results.json.results.bindings) {
            wkt.read(this.yasr.results.json.results.bindings[key].wkt.value);
            var feature = { "type": "Feature", 'properties': {"name": this.yasr.results.json.results.bindings[key].wktTooltip.value}, "geometry": wkt.toJson() };
            L.geoJson(feature, {
                style: function(feature) {
                    return {
                        color: "#a50026",
                        radius:6,
                        weight: 0,
                        opacity: 0.6,
                        fillOpacity: 0.6,
                    };
                },
                pointToLayer: function(feature, latlng) {
                    return new L.CircleMarker(latlng, {
                        radius: 10,
                        fillOpacity: 0.85
                    });
                }
            }).bindTooltip(function (layer) {
                return layer.feature.properties.name; }
            ).addTo(map);
        }
	}

	canHandleResults() {
        const vars = this.yasr.results.getVariables();
        return !!this.yasr.results && vars.includes("geo");
    }
    // A required function, used to identify the plugin, works best with an svg
    getIcon() {
        const textIcon = document.createElement("div");
        textIcon.classList.add("svgImg");
        const svg = document.createElement("svg");
        svg.setAttribute("xmlns", "http://www.w3.org/2000/svg");
        svg.setAttribute("viewBox", "0 0 510 512");
        svg.setAttribute("aria-hidden", "true");
        const path = document.createElement("path");
        path.setAttribute("fill", "currentColor");
        path.setAttribute("d", "M248 8C111.03 8 0 119.03 0 256s111.03 248 248 248 248-111.03 248-248S384.97 8 248 8zm160 215.5v6.93c0 5.87-3.32 11.24-8.57 13.86l-15.39 7.7a15.485 15.485 0 0 1-15.53-.97l-18.21-12.14a15.52 15.52 0 0 0-13.5-1.81l-2.65.88c-9.7 3.23-13.66 14.79-7.99 23.3l13.24 19.86c2.87 4.31 7.71 6.9 12.89 6.9h8.21c8.56 0 15.5 6.94 15.5 15.5v11.34c0 3.35-1.09 6.62-3.1 9.3l-18.74 24.98c-1.42 1.9-2.39 4.1-2.83 6.43l-4.3 22.83c-.62 3.29-2.29 6.29-4.76 8.56a159.608 159.608 0 0 0-25 29.16l-13.03 19.55a27.756 27.756 0 0 1-23.09 12.36c-10.51 0-20.12-5.94-24.82-15.34a78.902 78.902 0 0 1-8.33-35.29V367.5c0-8.56-6.94-15.5-15.5-15.5h-25.88c-14.49 0-28.38-5.76-38.63-16a54.659 54.659 0 0 1-16-38.63v-14.06c0-17.19 8.1-33.38 21.85-43.7l27.58-20.69a54.663 54.663 0 0 1 32.78-10.93h.89c8.48 0 16.85 1.97 24.43 5.77l14.72 7.36c3.68 1.84 7.93 2.14 11.83.84l47.31-15.77c6.33-2.11 10.6-8.03 10.6-14.7 0-8.56-6.94-15.5-15.5-15.5h-10.09c-4.11 0-8.05-1.63-10.96-4.54l-6.92-6.92a15.493 15.493 0 0 0-10.96-4.54H199.5c-8.56 0-15.5-6.94-15.5-15.5v-4.4c0-7.11 4.84-13.31 11.74-15.04l14.45-3.61c3.74-.94 7-3.23 9.14-6.44l8.08-12.11c2.87-4.31 7.71-6.9 12.89-6.9h24.21c8.56 0 15.5-6.94 15.5-15.5v-21.7C359.23 71.63 422.86 131.02 441.93 208H423.5c-8.56 0-15.5 6.94-15.5 15.5z");
        svg.appendChild(path);
        textIcon.appendChild(svg);
        return textIcon;
    }

}
Yasr.registerPlugin("Geo", Geo);
</script>
  <script>
 const urlParams = new URLSearchParams(window.location.search);
 const endpoint = urlParams.get('endpoint');
 const thequery = urlParams.get('query');
 const yasgui = new Yasgui(document.getElementById("yasgui"),{"pluginOrder": ["response", "table"],"yasqe":{"showQueryButton": false},"requestConfig": { "endpoint": endpoint},  "copyEndpointOnNewTab": false});
 if(typeof(thequery)!=='undefined' && thequery!=null){
	yasgui.getTab().yasqe.setValue(thequery)
 }
 yasgui.getTab().yasr.on("drawn",function(event){
	$('.iri').each(function(i,obj){
	    console.log(obj)
		if($(this).attr("href").includes(baseurl)){
			$(this).attr("href",$(this).attr("href").replace(baseurl,""))
		}
	})
 })
 const myEngine=new Comunica.QueryEngine()
 document.getElementsByClassName('yasqe_buttons')[0].appendChild(document.getElementById('query'));

 //yasgui.getTab().yasqe.on("query", function(event){ console.log(event); event.preventDefault(); queryFile()});	

async function queryFile(){
  yasres={"head":{"vars":[]},"results":{"bindings":[]}}
  config={"sources":[endpoint]}
  const result=await myEngine.queryBindings(yasgui.getTab().yasqe.getValue(), config)
  const data=await result.toArray()	
  vararray=[]
  ttypemap={"NamedNode":"uri","Literal":"literal"}
  for(bind of data){
	curbindings={}
	for(entry of bind["entries"]["_root"]["entries"]){
		if(!(vararray.includes(entry[0]))){
			vararray.push(entry[0])
		}
		curbindings[entry[0]]={"type":ttypemap[entry[1]["termType"]],"value":entry[1]["value"]}	
		if("datatype" in entry[1]){
			curbindings[entry[0]]["datatype"]=entry[1]["datatype"]["value"]
		}
		if("language" in entry[1] && entry[1]["language"]!=""){
			curbindings[entry[0]]["language"]=entry[1]["language"]
		}

	}
	yasres["results"]["bindings"].push(curbindings)
  }
  yasres["head"]["vars"]=vararray
	yasgui.getTab().yasr.setResponse({
	  data: yasres,
	  contentType: "application/sparql-results+json",
	  status: 200,
	  executionTime: 1000 // ms
	  // error to show
	})  		

// Draw results with current plugin
 //yasgui.getTab().yasr.draw()
}
  </script>""",

        "maptemplate": """
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script><script src="https://unpkg.com/leaflet.markercluster@1.0.6/dist/leaflet.markercluster-src.js"></script>
    <script src="https://unpkg.com/leaflet.markercluster.layersupport@2.0.1/dist/leaflet.markercluster.layersupport.js"></script>
    <script src="https://unpkg.com/leaflet.featuregroup.subgroup@1.0.2/dist/leaflet.featuregroup.subgroup.js"></script>
    <script src="https://api.mapbox.com/mapbox.js/plugins/leaflet-fullscreen/v1.0.1/Leaflet.fullscreen.min.js"></script>
    <script src="https://cdn.jsdelivr.net/gh/dwilhelm89/LeafletSlider@master/dist/leaflet.SliderControl.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/proj4js/2.9.0/proj4.min.js"></script><script src="https://cdn.jsdelivr.net/gh/albburtsev/Leaflet.geojsonCSS/leaflet.geojsoncss.min.js"></script>
    <script src="{{epsgdefspath}}"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/0.4.0/MarkerCluster.css" rel="stylesheet" />
    <link href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/0.4.0/MarkerCluster.Default.css" rel="stylesheet" />
    <link href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" rel="stylesheet" >
    <link href="https://api.mapbox.com/mapbox.js/plugins/leaflet-fullscreen/v1.0.1/leaflet.fullscreen.css" rel='stylesheet' />
    <div id="map" style="height:500px;z-index: 0;"></div><script>
    var rangesByAttribute={}
    var overlayMaps={}
    var baselayers={{baselayers}}
    var featurecolls = {{myfeature}}
    var ajax=true
    var epsg="{{epsg}}"
    var dateatt="{{dateatt}}"
    var map = L.map('map',{fullscreenControl: true,fullscreenControlOptions: {position: 'topleft'}}).setView([51.505, -0.09], 13);
    var baseMaps = {};
    props={}
    setupLeaflet(baselayers,epsg,baseMaps,overlayMaps,map,featurecolls,dateatt,ajax)
    </script>
    """,

        "vowltemplate": """<link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/gh/situx/mini-vowl@master/docs/css/vowl.css"/>
<script src="{{vowlpath}}"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.2.2/d3.v3.min.js"></script>
<script src="https://cdn.jsdelivr.net/gh/situx/mini-vowl@master/docs/js/webVOWLGraphProd.js"></script>
<div id="wrapper">
  <section id="vowl">
    <div id="graph">
      <div id="resetOption"></div>
      <div id="sliderOption"></div>
    </div>
  </section>
  <a href="vowl_result.js" target="_blank">Download VOWL File</a> <a href="minivowl_result.js" target="_blank">Download Mini VOWL File</a>
    <script>

    var graphTag = document.getElementById('graph')
    , linkDistanceClassSlider
    , linkDistanceClassLabel
    , linkDistanceLiteralLabel
    , linkDistanceLiteralSlider
    , onLoadCalled = false;
        var   height = 600
        , width = document.getElementById("vowl").offsetWidth;
    var graphOptions = function graphOptionsFunct() {

    var   resetOption = document.getElementById('resetOption'),
            fullscreenOption = document.getElementById('FullScreenOption')
        , sliderOption = document.getElementById('sliderOption');

      function fullscreenGraph() {
        if(!document.fullscreenElement) {
          document.getElementById("vowl").requestFullscreen()
          document.getElementById("svgGraph").width = "100%"
          document.getElementById("svgGraph").height = "100%"
        }else{
          document.exitFullscreen()
          document.getElementById("svgGraph").width = width
          document.getElementById("svgGraph").height = height
        }
      }

    d3.select(resetOption)
        .append("button")
        .attr("id", "reset")
        .property("type", "reset")
        .text("Reset")
        .on("click", resetGraph);

    d3.select(fullscreenOption)
        .append("button")
        .attr("id", "fullscreen")
        .property("type", "fullscreen")
        .text("FullScreen")
        .on("click", fullscreenGraph);

    var slidDiv = d3.select(sliderOption)
        .append("div")
        .attr("id", "distanceSlider");

    linkDistanceClassLabel = slidDiv.append("label")
        .attr("for", "distanceSlider")
        .text(DEFAULT_VISIBLE_LINKDISTANCE);
    linkDistanceLiteralLabel = linkDistanceClassLabel;

    linkDistanceClassSlider = slidDiv.append("input")
        .attr("type", "range")
        .attr("min", 10)
        .attr("max", 600)
        .attr("value", DEFAULT_VISIBLE_LINKDISTANCE)
        .attr("step", 10)
        .on("input", changeDistance);
    linkDistanceLiteralSlider = linkDistanceClassSlider;
};
    json=minivowlresult
    drawGraph(graphTag, width, height);
</script>
</div>""",

        "htmlcommenttemplate": """<p class="comment"><b>Description:</b> {{comment}}</p>""",

        "htmltabletemplate": """<div style="overflow-x:auto;"><table border=1 width=100% class=description><thead><tr><th>Property</th><th>Value</th></tr></thead><tbody>{{tablecontent}}</tbody></table></div>""",

        "footer": """<div id="footer"><div class="container-fluid">{{apis}}{{license}}{{bibtex}}{{stats}}</div></div></body><script>$(document).ready(function(){setSVGDimensions()})</script></html>""",

        "licensetemplate": """""",
        "chartviewtemplate": """<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.4.0/Chart.min.js"></script>
<canvas id="myChart" style="width:100%;max-width:700px"></canvas><button id="downlodChartData" onclick="exportChartJS()">Download Chart Data</button>
<script>
var xValues={{xValues}};
var yValues={{yValues}};
const myChart = new Chart("myChart", {
  type: "line",
  data: {
    labels: yValues,
    datasets: [{
      label: '{{xLabel}} over time',
      backgroundColor:"rgba(0,0,255,1.0)",
      borderColor: "rgba(0,0,255,0.1)",
      data: xValues
    }]},
  options: {scales: {x:{title:"{{xLabel}}"},y:{title:"{{yLabel}}"}}}
});
</script>""",
        "nexus": """
/*
Nexus
Copyright (c) 2012-2020, Visual Computing Lab, ISTI - CNR
All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/

Nexus = function() {

/* WORKER INITIALIZED ONCE */

var meco;
var corto;

var scripts = document.getElementsByTagName('script');
var i, j, k;
var path;
for(i = 0; i < scripts.length; i++) {
	var attrs = scripts[i].attributes;
	for(j = 0; j < attrs.length; j++) {
		var a = attrs[j];
		if(a.name != 'src') continue;
		if(!a.value) continue;
		if(a.value.search('nexus.js') >= 0) {
			path = a.value;
			break;
		}
	}
}

var meco = null;
function loadMeco() {

	meco = new Worker(path.replace('nexus.js', 'meco.js'));

	meco.onerror = function(e) { console.log(e); }
	meco.requests = {};
	meco.count = 0;
	meco.postRequest = function(sig, node, patches) {
		var signature = {
			texcoords: sig.texcoords ? 1 : 0,
			colors   : sig.colors    ? 1 : 0,
			normals  : sig.normals   ? 1 : 0,
			indices  : sig.indices   ? 1 : 0
		};
		meco.postMessage({
			signature:signature,
			node:{ nface: node.nface, nvert: node.nvert, buffer:node.buffer, request:this.count},
			patches:patches
		});
		node.buffer = null;
		this.requests[this.count++] = node;
	};
	meco.onmessage = function(e) {
		var node = this.requests[e.data.request];
		delete this.requests[e.data.request];
		node.buffer = e.data.buffer;
		readyNode(node);
	};
}

var corto = null;
function loadCorto() {

	corto = new Worker(path.replace('nexus.js', 'corto.em.js'));
	corto.requests = {};
	corto.count = 0;
	corto.postRequest = function(node) {
		corto.postMessage({ buffer: node.buffer, request:this.count, rgba_colors: true, short_index: true, short_normals: true});
		node.buffer = null;
		this.requests[this.count++] = node;
	}
	corto.onmessage = function(e) {
		var request = e.data.request;
		var node = this.requests[request];
		delete this.requests[request];
		node.model = e.data.model;
		readyNode(node);
	};
}

/* UTILITIES */

function getUint64(view) {
	var s = 0;
	var lo = view.getUint32(view.offset, true);
	var hi = view.getUint32(view.offset + 4, true);
	view.offset += 8;
	return ((hi * (1 << 32)) + lo);
}

function getUint32(view) {
	var s = view.getUint32(view.offset, true);
	view.offset += 4;
	return s;
}

function getUint16(view) {
	var s = view.getUint16(view.offset, true);
	view.offset += 2;
	return s;
}

function getFloat32(view) {
	var s = view.getFloat32(view.offset, true);
	view.offset += 4;
	return s;
}

/* MATRIX STUFF */

function vecMul(m, v, r) {
	var w = m[3]*v[0] + m[7]*v[1] + m[11]*v[2] + m[15];

	r[0] = (m[0]*v[0]  + m[4]*v[1]  + m[8 ]*v[2] + m[12 ])/w;
	r[1] = (m[1]*v[0]  + m[5]*v[1]  + m[9 ]*v[2] + m[13 ])/w;
	r[2] = (m[2]*v[0]  + m[6]*v[1]  + m[10]*v[2] + m[14])/w;
}


function matMul(a, b, r) {
	r[ 0] = a[0]*b[0] + a[4]*b[1] + a[8]*b[2] + a[12]*b[3];
	r[ 1] = a[1]*b[0] + a[5]*b[1] + a[9]*b[2] + a[13]*b[3];
	r[ 2] = a[2]*b[0] + a[6]*b[1] + a[10]*b[2] + a[14]*b[3];
	r[ 3] = a[3]*b[0] + a[7]*b[1] + a[11]*b[2] + a[15]*b[3];

	r[ 4] = a[0]*b[4] + a[4]*b[5] + a[8]*b[6] + a[12]*b[7];
	r[ 5] = a[1]*b[4] + a[5]*b[5] + a[9]*b[6] + a[13]*b[7];
	r[ 6] = a[2]*b[4] + a[6]*b[5] + a[10]*b[6] + a[14]*b[7];
	r[ 7] = a[3]*b[4] + a[7]*b[5] + a[11]*b[6] + a[15]*b[7];

	r[ 8] = a[0]*b[8] + a[4]*b[9] + a[8]*b[10] + a[12]*b[11];
	r[ 9] = a[1]*b[8] + a[5]*b[9] + a[9]*b[10] + a[13]*b[11];
	r[10] = a[2]*b[8] + a[6]*b[9] + a[10]*b[10] + a[14]*b[11];
	r[11] = a[3]*b[8] + a[7]*b[9] + a[11]*b[10] + a[15]*b[11];

	r[12] = a[0]*b[12] + a[4]*b[13] + a[8]*b[14] + a[12]*b[15];
	r[13] = a[1]*b[12] + a[5]*b[13] + a[9]*b[14] + a[13]*b[15];
	r[14] = a[2]*b[12] + a[6]*b[13] + a[10]*b[14] + a[14]*b[15];
	r[15] = a[3]*b[12] + a[7]*b[13] + a[11]*b[14] + a[15]*b[15];
}

function matInv(m, t) {
	var s = 1.0/(
		m[12]* m[9]*m[6]*m[3]-m[8]*m[13]*m[6]*m[3]-m[12]*m[5]*m[10]*m[3]+m[4]*m[13]*m[10]*m[3]+
		m[8]*m[5]*m[14]*m[3]-m[4]*m[9]*m[14]*m[3]-m[12]*m[9]*m[2]*m[7]+m[8]*m[13]*m[2]*m[7]+
		m[12]*m[1]*m[10]*m[7]-m[0]*m[13]*m[10]*m[7]-m[8]*m[1]*m[14]*m[7]+m[0]*m[9]*m[14]*m[7]+
		m[12]*m[5]*m[2]*m[11]-m[4]*m[13]*m[2]*m[11]-m[12]*m[1]*m[6]*m[11]+m[0]*m[13]*m[6]*m[11]+
		m[4]*m[1]*m[14]*m[11]-m[0]*m[5]*m[14]*m[11]-m[8]*m[5]*m[2]*m[15]+m[4]*m[9]*m[2]*m[15]+
		m[8]*m[1]*m[6]*m[15]-m[0]*m[9]*m[6]*m[15]-m[4]*m[1]*m[10]*m[15]+m[0]*m[5]*m[10]*m[15]
	);

	t[ 0] = (m[9]*m[14]*m[7]-m[13]*m[10]*m[7]+m[13]*m[6]*m[11]-m[5]*m[14]*m[11]-m[9]*m[6]*m[15]+m[5]*m[10]*m[15])*s;
	t[ 1] = (m[13]*m[10]*m[3]-m[9]*m[14]*m[3]-m[13]*m[2]*m[11]+m[1]*m[14]*m[11]+m[9]*m[2]*m[15]-m[1]*m[10]*m[15])*s;
	t[ 2] = (m[5]*m[14]*m[3]-m[13]*m[6]*m[3]+m[13]*m[2]*m[7]-m[1]*m[14]*m[7]-m[5]*m[2]*m[15]+m[1]*m[6]*m[15])*s;
	t[ 3] = (m[9]*m[6]*m[3]-m[5]*m[10]*m[3]-m[9]*m[2]*m[7]+m[1]*m[10]*m[7]+m[5]*m[2]*m[11]-m[1]*m[6]*m[11])*s;

	t[ 4] = (m[12]*m[10]*m[7]-m[8]*m[14]*m[7]-m[12]*m[6]*m[11]+m[4]*m[14]*m[11]+m[8]*m[6]*m[15]-m[4]*m[10]*m[15])*s;
	t[ 5] = (m[8]*m[14]*m[3]-m[12]*m[10]*m[3]+m[12]*m[2]*m[11]-m[0]*m[14]*m[11]-m[8]*m[2]*m[15]+m[0]*m[10]*m[15])*s;
	t[ 6] = (m[12]*m[6]*m[3]-m[4]*m[14]*m[3]-m[12]*m[2]*m[7]+m[0]*m[14]*m[7]+m[4]*m[2]*m[15]-m[0]*m[6]*m[15])*s;
	t[ 7] = (m[4]*m[10]*m[3]-m[8]*m[6]*m[3]+m[8]*m[2]*m[7]-m[0]*m[10]*m[7]-m[4]*m[2]*m[11]+m[0]*m[6]*m[11])*s;

	t[ 8] = (m[8]*m[13]*m[7]-m[12]*m[9]*m[7]+m[12]*m[5]*m[11]-m[4]*m[13]*m[11]-m[8]*m[5]*m[15]+m[4]*m[9]*m[15])*s;
	t[ 9] = (m[12]*m[9]*m[3]-m[8]*m[13]*m[3]-m[12]*m[1]*m[11]+m[0]*m[13]*m[11]+m[8]*m[1]*m[15]-m[0]*m[9]*m[15])*s;
	t[10] = (m[4]*m[13]*m[3]-m[12]*m[5]*m[3]+m[12]*m[1]*m[7]-m[0]*m[13]*m[7]-m[4]*m[1]*m[15]+m[0]*m[5]*m[15])*s;
	t[11] = (m[8]*m[5]*m[3]-m[4]*m[9]*m[3]-m[8]*m[1]*m[7]+m[0]*m[9]*m[7]+m[4]*m[1]*m[11]-m[0]*m[5]*m[11])*s;

	t[12] = (m[12]*m[9]*m[6]-m[8]*m[13]*m[6]-m[12]*m[5]*m[10]+m[4]*m[13]*m[10]+m[8]*m[5]*m[14]-m[4]*m[9]*m[14])*s;
	t[13] = (m[8]*m[13]*m[2]-m[12]*m[9]*m[2]+m[12]*m[1]*m[10]-m[0]*m[13]*m[10]-m[8]*m[1]*m[14]+m[0]*m[9]*m[14])*s;
	t[14] = (m[12]*m[5]*m[2]-m[4]*m[13]*m[2]-m[12]*m[1]*m[6]+m[0]*m[13]*m[6]+m[4]*m[1]*m[14]-m[0]*m[5]*m[14])*s;
	t[15] = (m[4]*m[9]*m[2]-m[8]*m[5]*m[2]+m[8]*m[1]*m[6]-m[0]*m[9]*m[6]-m[4]*m[1]*m[10]+m[0]*m[5]*m[10])*s;
}

/* PRIORITY QUEUE */

PriorityQueue = function(max_length) {
	this.error = new Float32Array(max_length);
	this.data = new Int32Array(max_length);
	this.size = 0;
}

PriorityQueue.prototype = {
	push: function(data, error) {
		this.data[this.size] = data;
		this.error[this.size] = error;
		this.bubbleUp(this.size);
		this.size++;
	},

	pop: function() {
		var result = this.data[0];
		this.size--;
		if(this.size > 0) {
			this.data[0] = this.data[this.size];
			this.error[0] = this.error[this.size];
			this.sinkDown(0);
		}
		return result;
	},

	bubbleUp: function(n) {
		var data = this.data[n];
		var error = this.error[n];
		while (n > 0) {
			var pN = ((n+1)>>1) -1;
			var pError = this.error[pN];
			if(pError > error)
				break;
			//swap
			this.data[n] = this.data[pN];
			this.error[n] = pError;
			this.data[pN] = data;
			this.error[pN] = error;
			n = pN;
		}
	},

	sinkDown: function(n) {
		var data = this.data[n];
		var error = this.error[n];

		while(true) {
			var child2N = (n + 1) * 2;
			var child1N = child2N - 1;
			var swap = -1;
			if (child1N < this.size) {
				var child1Error = this.error[child1N];
				if(child1Error > error)
					swap = child1N;
			}
			if (child2N < this.size) {
				var child2Error = this.error[child2N];
				if (child2Error > (swap == -1 ? error : child1Error))
					swap = child2N;
			}

			if (swap == -1) break;

			this.data[n] = this.data[swap];
			this.error[n] = this.error[swap];
			this.data[swap] = data;
			this.error[swap] = error;
			n = swap;
		}
	}
};


/* HEADER AND PARSING */

var padding = 256;
var Debug = {
	verbose : false,  //debug messages
	nodes   : false,  //color each node
	draw    : false,  //final rendering call disabled
	extract : false,  //extraction disabled
//	culling : false,  //visibility culling disabled
//	request : false,  //network requests disabled
//	worker  : false   //web workers disabled
};


var glP = WebGLRenderingContext.prototype;
var attrGlMap = [glP.NONE, glP.BYTE, glP.UNSIGNED_BYTE, glP.SHORT, glP.UNSIGNED_SHORT, glP.INT, glP.UNSIGNED_INT, glP.FLOAT, glP.DOUBLE];
var attrSizeMap = [0, 1, 1, 2, 2, 4, 4, 4, 8];

var targetError   = 2.0;    //error won't go lower than this if we reach it
var maxError      = 15;     //error won't go over this even if fps is low
var minFps        = 15;
var maxPending    = 3;
var maxBlocked    = 3;
var maxReqAttempt = 2;
var maxCacheSize  = 512*(1<<20); //TODO DEBUG
var drawBudget    = 5*(1<<20);


/* MESH DEFINITION */

Mesh = function() {
	var t = this;
	t.onLoad = null;
	t.reqAttempt = 0;
}

Mesh.prototype = {
	open: function(url) {
		var mesh = this;
		mesh.url = url;
		mesh.httpRequest(
			0,
			88,
			function() {
				if(Debug.verbose) console.log("Loading header for " + mesh.url);
				var view = new DataView(this.response);
				view.offset = 0;
				mesh.reqAttempt++;
				var header = mesh.importHeader(view);
				if(!header) {
					if(Debug.verbose) console.log("Empty header!");
					if(mesh.reqAttempt < maxReqAttempt) mesh.open(mesh.url + '?' + Math.random()); // BLINK ENGINE CACHE BUG PATCH
					return;
				}
				mesh.reqAttempt = 0;
				for(i in header)
					mesh[i] = header[i];
				mesh.vertex = mesh.signature.vertex;
				mesh.face = mesh.signature.face;
				mesh.renderMode = mesh.face.index?["FILL", "POINT"]:["POINT"];
				mesh.compressed = (mesh.signature.flags & (2 | 4)); //meco or corto
				mesh.meco = (mesh.signature.flags & 2);
				mesh.corto = (mesh.signature.flags & 4);
				mesh.requestIndex();
			},
			function() { console.log("Open request error!");},
			function() { console.log("Open request abort!");}
		);
	},

	httpRequest: function(start, end, load, error, abort, type) {
		if(!type) type = 'arraybuffer';
		var r = new XMLHttpRequest();
		r.open('GET', this.url, true);
		r.responseType = type;
		r.setRequestHeader("Range", "bytes=" + start + "-" + (end -1));
		r.onload = function(){
			switch (this.status){
				case 0:
//					console.log("0 response: server unreachable.");//returned in chrome for local files
				case 206:
//					console.log("206 response: partial content loaded.");
					load.bind(this)();
					break;
				case 200:
//					console.log("200 response: server does not support byte range requests.");
			}
		};
		r.onerror = error;
		r.onabort = abort;
		r.send();
		return r;
	},

	requestIndex: function() {
		var mesh = this;
		var end = 88 + mesh.nodesCount*44 + mesh.patchesCount*12 + mesh.texturesCount*68;
		mesh.httpRequest(
			88,
			end,
			function() { if(Debug.verbose) console.log("Loading index for " + mesh.url); mesh.handleIndex(this.response); },
			function() { console.log("Index request error!");},
			function() { console.log("Index request abort!");}
		);
	},

	handleIndex: function(buffer) {
		var t = this;
		var view = new DataView(buffer);
		view.offset = 0;

		var n = t.nodesCount;

		t.noffsets  = new Uint32Array(n);
		t.nvertices = new Uint32Array(n);
		t.nfaces    = new Uint32Array(n);
		t.nerrors   = new Float32Array(n);
		t.nspheres  = new Float32Array(n*5);
		t.nsize     = new Float32Array(n);
		t.nfirstpatch = new Uint32Array(n);

		for(i = 0; i < n; i++) {
			t.noffsets[i] = padding*getUint32(view); //offset
			t.nvertices[i] = getUint16(view);        //verticesCount
			t.nfaces[i] = getUint16(view);           //facesCount
			t.nerrors[i] = getFloat32(view);
			view.offset += 8;                        //skip cone
			for(k = 0; k < 5; k++)
				t.nspheres[i*5+k] = getFloat32(view);       //sphere + tight
			t.nfirstpatch[i] = getUint32(view);          //first patch
		}
		t.sink = n -1;

		t.patches = new Uint32Array(view.buffer, view.offset, t.patchesCount*3); //noded, lastTriangle, texture
		t.nroots = t.nodesCount;
		for(j = 0; j < t.nroots; j++) {
			for(i = t.nfirstpatch[j]; i < t.nfirstpatch[j+1]; i++) {
				if(t.patches[i*3] < t.nroots)
					t.nroots = t.patches[i*3];
			}
		}

		view.offset += t.patchesCount*12;

		t.textures = new Uint32Array(t.texturesCount);
		t.texref = new Uint32Array(t.texturesCount);
		for(i = 0; i < t.texturesCount; i++) {
			t.textures[i] = padding*getUint32(view);
			view.offset += 16*4; //skip proj matrix
		}

		t.vsize = 12 + (t.vertex.normal?6:0) + (t.vertex.color?4:0) + (t.vertex.texCoord?8:0);
		t.fsize = 6;

		//problem: I have no idea how much space a texture is needed in GPU. 10x factor assumed.
		var tmptexsize = new Uint32Array(n-1);
		var tmptexcount = new Uint32Array(n-1);
		for(var i = 0; i < n-1; i++) {
			for(var p = t.nfirstpatch[i]; p != t.nfirstpatch[i+1]; p++) {
				var tex = t.patches[p*3+2];
				tmptexsize[i] += t.textures[tex+1] - t.textures[tex];
				tmptexcount[i]++;
			}
			t.nsize[i] = t.vsize*t.nvertices[i] + t.fsize*t.nfaces[i];
		}
		for(var i = 0; i < n-1; i++) {
			t.nsize[i] += 10*tmptexsize[i]/tmptexcount[i];
		}

		t.status = new Uint8Array(n); //0 for none, 1 for ready, 2+ for waiting data
		t.frames = new Uint32Array(n);
		t.errors = new Float32Array(n); //biggest error of instances
		t.ibo    = new Array(n);
		t.vbo    = new Array(n);
		t.texids = new Array(n);

		t.isReady = true;
		if(t.onLoad) t.onLoad();
	},

	importAttribute: function(view) {
		var a = {};
		a.type = view.getUint8(view.offset++, true);
		a.size = view.getUint8(view.offset++, true);
		a.glType = attrGlMap[a.type];
		a.normalized = a.type < 7;
		a.stride = attrSizeMap[a.type]*a.size;
		if(a.size == 0) return null;
		return a;
	},

	importElement: function(view) {
		var e = [];
		for(i = 0; i < 8; i++)
			e[i] = this.importAttribute(view);
		return e;
	},

	importVertex: function(view) {	//enum POSITION, NORMAL, COLOR, TEXCOORD, DATA0
		var e = this.importElement(view);
		var color = e[2];
		if(color) {
			color.type = 2; //unsigned byte
			color.glType = attrGlMap[2];
		}
		return { position: e[0], normal: e[1], color: e[2], texCoord: e[3], data: e[4] };
	},

	//enum INDEX, NORMAL, COLOR, TEXCOORD, DATA0
	importFace: function(view) {
		var e = this.importElement(view);
		var color = e[2];
		if(color) {
			color.type = 2; //unsigned byte
			color.glType = attrGlMap[2];
		}
		return { index: e[0], normal: e[1], color: e[2], texCoord: e[3], data: e[4] };
	},

	importSignature: function(view) {
		var s = {};
		s.vertex = this.importVertex(view);
		s.face = this.importFace(view);
		s.flags = getUint32(view);
		return s;
	},

	importHeader: function(view) {
		var magic = getUint32(view);
		if(magic != 0x4E787320) return null;
		var h = {};
		h.version = getUint32(view);
		h.verticesCount = getUint64(view);
		h.facesCount = getUint64(view);
		h.signature = this.importSignature(view);
		h.nodesCount = getUint32(view);
		h.patchesCount = getUint32(view);
		h.texturesCount = getUint32(view);
		h.sphere = {
			center: [getFloat32(view), getFloat32(view), getFloat32(view)],
			radius: getFloat32(view)
		};
		return h;
	}
};

Instance = function(gl) {
	this.gl = gl;
	this.onLoad = function() {};
	this.onUpdate = null;
	this.drawBudget = drawBudget;
	this.attributes = { 'position':0, 'normal':1, 'color':2, 'uv':3, 'size':4 };
}

Instance.prototype = {
	open: function(url) {
		var t = this;
		t.context = getContext(t.gl);

		t.modelMatrix      = new Float32Array(16);
		t.viewMatrix       = new Float32Array(16);
		t.projectionMatrix = new Float32Array(16);
		t.modelView        = new Float32Array(16);
		t.modelViewInv     = new Float32Array(16);
		t.modelViewProj    = new Float32Array(16);
		t.modelViewProjInv = new Float32Array(16);
		t.planes           = new Float32Array(24);
		t.viewport         = new Float32Array(4);
		t.viewpoint        = new Float32Array(4);

		t.context.meshes.forEach(function(m) {
			if(m.url == url){
				t.mesh = m;
				t.renderMode = t.mesh.renderMode;
				t.mode = t.renderMode[0];
				t.onLoad();
			}
		});

		if(!t.mesh) {
			t.mesh = new Mesh();
			t.mesh.onLoad = function() { t.renderMode = t.mesh.renderMode; t.mode = t.renderMode[0]; t.onLoad(); }
			t.mesh.open(url);
			t.context.meshes.push(t.mesh);
		}
	},

	close: function() {
		//remove instance from mesh.
	},

	get isReady() { return this.mesh.isReady; },
	setPrimitiveMode : function (mode) { this.mode = mode; },
	get datasetRadius() { if(!this.isReady) return 1.0;       return this.mesh.sphere.radius; },
	get datasetCenter() { if(!this.isReady) return [0, 0, 0]; return this.mesh.sphere.center; },

	updateView: function(viewport, projection, modelView) {
		var t = this;

		for(var i = 0; i < 16; i++) {
			t.projectionMatrix[i] = projection[i];
			t.modelView[i] = modelView[i];
		}
		for(var i = 0; i < 4; i++)
			t.viewport[i] = viewport[i];

		matMul(t.projectionMatrix, t.modelView, t.modelViewProj);
		matInv(t.modelViewProj, t.modelViewProjInv);

		matInv(t.modelView, t.modelViewInv);
		t.viewpoint[0] = t.modelViewInv[12];
		t.viewpoint[1] = t.modelViewInv[13];
		t.viewpoint[2] = t.modelViewInv[14];
		t.viewpoint[3] = 1.0;


		var m = t.modelViewProj;
		var mi = t.modelViewProjInv;
		var p = t.planes;

		//frustum planes Ax + By + Cz + D = 0;
		p[0]  =  m[0] + m[3]; p[1]  =  m[4] + m[7]; p[2]  =  m[8] + m[11];  p[3]  =  m[12] + m[15]; //left
		p[4]  = -m[0] + m[3]; p[5]  = -m[4] + m[7]; p[6]  = -m[8] + m[11];  p[7]  = -m[12] + m[15]; //right
		p[8]  =  m[1] + m[3]; p[9]  =  m[5] + m[7]; p[10] =  m[9] + m[11];  p[11] =  m[13] + m[15]; //bottom
		p[12] = -m[1] + m[3]; p[13] = -m[5] + m[7]; p[14] = -m[9] + m[11];  p[15] = -m[13] + m[15]; //top
		p[16] = -m[2] + m[3]; p[17] = -m[6] + m[7]; p[18] = -m[10] + m[11]; p[19] = -m[14] + m[15]; //near
		p[20] = -m[2] + m[3]; p[21] = -m[6] + m[7]; p[22] = -m[10] + m[11]; p[23] = -m[14] + m[15]; //far

		//normalize planes to get also correct distances
		for(var i = 0; i < 24; i+= 4) {
			var l = Math.sqrt(p[i]*p[i] + p[i+1]*p[i+1] + p[i+2]*p[i+2]);
			p[i] /= l; p[i+1] /= l; p[i+2] /= l; p[i+3] /= l;
		}

		//side is M'(1,0,0,1) - M'(-1,0,0,1) and they lie on the planes
		var r3 = mi[3] + mi[15];
		var r0 = (mi[0]  + mi[12 ])/r3;
		var r1 = (mi[1]  + mi[13 ])/r3;
		var r2 = (mi[2]  + mi[14 ])/r3;

		var l3 = -mi[3] + mi[15];
		var l0 = (-mi[0]  + mi[12 ])/l3 - r0;
		var l1 = (-mi[1]  + mi[13 ])/l3 - r1;
		var l2 = (-mi[2]  + mi[14 ])/l3 - r2;

		var side = Math.sqrt(l0*l0 + l1*l1 + l2*l2);

		//center of the scene is M'*(0, 0, 0, 1)
		var c0 = mi[12]/mi[15] - t.viewpoint[0];
		var c1 = mi[13]/mi[15] - t.viewpoint[1];
		var c2 = mi[14]/mi[15] - t.viewpoint[2];
		var dist = Math.sqrt(c0*c0 + c1*c1 + c2*c2);

		var resolution = (2*side/dist)/ t.viewport[2];
		t.currentResolution == resolution ? t.sameResolution = true : t.sameResolution = false;
		t.currentResolution = resolution;
	},

	traversal : function () {
		var t = this;

		if(Debug.extract == true)
			return;

		if(!t.isReady) return;

		if(t.sameResolution)
			if(!t.visitQueue.size && !t.nblocked) return;

		var n = t.mesh.nodesCount;
		t.visited  = new Uint8Array(n);
		t.blocked  = new Uint8Array(n);
		t.selected = new Uint8Array(n);

		t.visitQueue = new PriorityQueue(n);
		for(var i = 0; i < t.mesh.nroots; i++)
			t.insertNode(i);

		t.currentError = t.context.currentError;
		t.drawSize = 0;
		t.nblocked = 0;

		var requested = 0;
		while(t.visitQueue.size && t.nblocked < maxBlocked) {
			var error = t.visitQueue.error[0];
			var node = t.visitQueue.pop();
			if ((requested < maxPending) && (t.mesh.status[node] == 0)) {
				t.context.candidates.push({id: node, instance:t, mesh:t.mesh, frame:t.context.frame, error:error});
				requested++;
			}

			var blocked = t.blocked[node] || !t.expandNode(node, error);
			if (blocked)
				t.nblocked++;
			else {
				t.selected[node] = 1;
			}
			t.insertChildren(node, blocked);
		}
	},

	insertNode: function (node) {
		var t = this;
		t.visited[node] = 1;

		var error = t.nodeError(node);
		if(node > 0 && error < t.currentError) return;  //2% speed TODO check if needed

		var errors = t.mesh.errors;
		var frames = t.mesh.frames;
		if(frames[node] != t.context.frame || errors[node] < error) {
			errors[node] = error;
			frames[node] = t.context.frame;
		}
		t.visitQueue.push(node, error);
	},

	insertChildren : function (node, block) {
		var t = this;
		for(var i = t.mesh.nfirstpatch[node]; i < t.mesh.nfirstpatch[node+1]; ++i) {
			var child = t.mesh.patches[i*3];
			if (child == t.mesh.sink) return;
			if (block) t.blocked[child] = 1;
			if (!t.visited[child])
				t.insertNode(child);
		}
	},

	expandNode : function (node, error) {
		var t = this;
		if(node > 0 && error < t.currentError) {
//			console.log("Reached error", error, t.currentError);
			return false;
		}

		if(t.drawSize > t.drawBudget) {
//			console.log("Reached drawsize", t.drawSize, t.drawBudget);
			return false;
		}

		if(t.mesh.status[node] != 1) { //not ready
//			console.log("Node " + node + " still not loaded (cache?)");
			return false;
		}

		var sp = t.mesh.nspheres;
		var off = node*5;
		if(t.isVisible(sp[off], sp[off+1], sp[off+2], sp[off+3])) //expanded radius
			t.drawSize += t.mesh.nvertices[node]*0.8;
			//we are adding half of the new faces. (but we are using the vertices so *2)

		return true;
	},

	nodeError : function (n, tight) {
		var t = this;
		var spheres = t.mesh.nspheres;
		var b = t.viewpoint;
		var off = n*5;
		var cx = spheres[off+0];
		var cy = spheres[off+1];
		var cz = spheres[off+2];
		var r  = spheres[off+3];
		if(tight)
			r = spheres[off+4];
		var d0 = b[0] - cx;
		var d1 = b[1] - cy;
		var d2 = b[2] - cz;
		var dist = Math.sqrt(d0*d0 + d1*d1 + d2*d2) - r;
		if (dist < 0.1)
			dist = 0.1;

		//resolution is how long is a pixel at distance 1.
		var error = t.mesh.nerrors[n]/(t.currentResolution*dist); //in pixels

		if (!t.isVisible(cx, cy, cz, spheres[off+4]))
			error /= 1000.0;
		return error;
	},

	isVisible : function (x, y, z, r) {
		var p = this.planes;
		for (i = 0; i < 24; i +=4) {
			if(p[i]*x + p[i+1]*y + p[i+2]*z + p[i+3] + r < 0) //plane is ax+by+cz+d = 0; 
				return false;
		}
		return true;
	},

	renderNodes: function() {
		var t = this;
		var m = t.mesh;
		var gl = t.gl;
		var attr = t.attributes;

		var vertexEnabled = gl.getVertexAttrib(attr.position, gl.VERTEX_ATTRIB_ARRAY_ENABLED);
		var normalEnabled = attr.normal >= 0? gl.getVertexAttrib(attr.normal, gl.VERTEX_ATTRIB_ARRAY_ENABLED): false;
		var colorEnabled  = attr.color  >= 0? gl.getVertexAttrib(attr.color,  gl.VERTEX_ATTRIB_ARRAY_ENABLED): false;
		var uvEnabled     = attr.uv     >= 0? gl.getVertexAttrib(attr.uv,     gl.VERTEX_ATTRIB_ARRAY_ENABLED): false;

		var rendered = 0;
		var last_texture = -1;

		t.realError = 0.0;
		for(var n = 0; n < m.nodesCount; n++) {
			if(!t.selected[n]) continue;

			if(t.mode != "POINT") {
				var skip = true;
				for(var p = m.nfirstpatch[n]; p < m.nfirstpatch[n+1]; p++) {
					var child = m.patches[p*3];
					if(!t.selected[child]) {
						skip = false;
						break;
					}
				}
				if(skip) continue;
			}

			var sp = m.nspheres;
			var off = n*5;
			if(!t.isVisible(sp[off], sp[off+1], sp[off+2], sp[off+4])) //tight radius
				continue;

			let err = t.nodeError(n, true);
			t.realError = Math.max(err, t.realError);

			gl.bindBuffer(gl.ARRAY_BUFFER, m.vbo[n]);
			if(t.mode != "POINT")
				gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, m.ibo[n]);

			gl.vertexAttribPointer(attr.position, 3, gl.FLOAT, false, 12, 0);
			gl.enableVertexAttribArray(attr.position);

			var nv = m.nvertices[n];
			var offset = nv*12;

			if(m.vertex.texCoord && attr.uv >= 0){
				gl.vertexAttribPointer(attr.uv, 2, gl.FLOAT, false, 8, offset), offset += nv*8;
				gl.enableVertexAttribArray(attr.uv);
			}
			if(m.vertex.color && attr.color >= 0){
				gl.vertexAttribPointer(attr.color, 4, gl.UNSIGNED_BYTE, true, 4, offset), offset += nv*4;
				gl.enableVertexAttribArray(attr.color);
			}
			if(m.vertex.normal && attr.normal >= 0){
				gl.vertexAttribPointer(attr.normal, 3, gl.SHORT, true, 6, offset);
				gl.enableVertexAttribArray(attr.normal);
			}

			if(Debug.nodes) {
				gl.disableVertexAttribArray(2);
				gl.disableVertexAttribArray(3);

				var error = t.nodeError(n, true);
				var palette = [
					[1, 1, 1, 1], //white
					[1, 1, 1, 1], //white
					[1, 0, 1, 1], //magenta
					[0, 1, 1, 1], //cyan
					[1, 1, 0, 1], //yellow
					[0, 0, 1, 1], //blue
					[0, 1, 0, 1], //green
					[1, 0, 0, 1]  //red
				];
				let w = Math.min(6.99, Math.max(0, Math.log2(error)));
				let low = Math.floor(w);
				w -= low;
				let color = [];
				for( let k = 0; k < 4; k++)
					color[k] = palette[low][k]*(1-w) + palette[low+1][k]*w;
				gl.vertexAttrib4fv(attr.color, color);
//				gl.vertexAttrib4fv(2, [(n*200 %255)/255.0, (n*140 %255)/255.0,(n*90 %255)/255.0, 1]);
			}

			if (Debug.draw) continue;

			if(t.mode == "POINT") {
				var pointsize = t.pointsize;
				var error = t.nodeError(n);
				if(!pointsize)
					var pointsize = Math.ceil(1.2* Math.min(error, 5));

				if(typeof attr.size == 'object') { //threejs pointcloud rendering
					gl.uniform1f(attr.size, t.pointsize);
					gl.uniform1f(attr.scale, t.pointscale);
				} else
					gl.vertexAttrib1fv(attr.size, [pointsize]);

//				var fraction = (error/t.realError - 1);
//				if(fraction > 1) fraction = 1;

				var count = nv;
				if(count != 0) {
					if(m.vertex.texCoord) {
						var texid = m.patches[m.nfirstpatch[n]*3+2];
						if(texid != -1 && texid != last_texture) { //bind texture
							var tex = m.texids[texid];
							gl.activeTexture(gl.TEXTURE0);
							gl.bindTexture(gl.TEXTURE_2D, tex);
						}
					}
					gl.drawArrays(gl.POINTS, 0, count);
					rendered += count;
				}
				continue;
			}

			//concatenate renderings to remove useless calls. except we have textures.
			var offset = 0;
			var end = 0;
			var last = m.nfirstpatch[n+1]-1;
			for (var p = m.nfirstpatch[n]; p < m.nfirstpatch[n+1]; ++p) {
				var child = m.patches[p*3];

				if(!t.selected[child]) {
					end = m.patches[p*3+1];
					if(p < last) //if textures we do not join. TODO: should actually check for same texture of last one.
						continue;
				}
				if(end > offset) {
					if(m.vertex.texCoord) {
						var texid = m.patches[p*3+2];
						if(texid != -1 && texid != last_texture) { //bind texture
							var tex = m.texids[texid];
							gl.activeTexture(gl.TEXTURE0);
							gl.bindTexture(gl.TEXTURE_2D, tex);
							last_texture = texid;
						}
					}
					gl.drawElements(gl.TRIANGLES, (end - offset) * 3, gl.UNSIGNED_SHORT, offset * 6);
					rendered += end - offset;
				}
				offset = m.patches[p*3+1];
			}
		}

		t.context.rendered += rendered;
		t.context.realError = Math.max(t.context.realError, t.realError);

		if(!vertexEnabled) gl.disableVertexAttribArray(attr.position);
		if(!normalEnabled && attr.normal >= 0) gl.disableVertexAttribArray(attr.normal);
		if(!colorEnabled && attr.color >= 0) gl.disableVertexAttribArray(attr.color);
		if(!uvEnabled && attr.uv >= 0) gl.disableVertexAttribArray(attr.uv);

		gl.bindBuffer(gl.ARRAY_BUFFER, null);
		if(t.mode != "POINT")
			gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, null);
	},

	render: function() {
		this.traversal();
		this.renderNodes();
	}
};

//keep track of meshes and which GL they belong to (no sharing between contexts)
var contexts = [];

function getContext(gl) {
	var c = null;
	if(!gl.isTexture) throw "Something wrong";
	contexts.forEach(function(g) {
		if(g.gl == gl) c = g;
	});
	if(c) return c;
	c = { gl:gl, meshes:[], frame:0, cacheSize:0, candidates:[], pending:0, maxCacheSize: maxCacheSize,
		minFps: minFps, targetError: targetError, currentError: targetError, maxError: maxError, realError: 0 };
	contexts.push(c);
	return c;
}

function beginFrame(gl, fps) { //each context has a separate frame count.
	var c = getContext(gl);

	c.frame++;
	c.candidates = [];
	if(fps && c.minFps) {
		c.currentFps = fps;
		var r = c.minFps/fps;
		if(r > 1.1)
			c.currentError *= 1.05;
		if(r < 0.9)
			c.currentError *= 0.95;

		c.currentError = Math.max(c.targetError, Math.min(c.maxError, c.currentError));

	} else
		c.currentError = c.targetError;

	c.rendered = 0;
	c.realError = 0;
}

function endFrame(gl) {
	updateCache(gl);
}

function removeNode(context, node) {
	var n = node.id;
	var m = node.mesh;
	if(m.status[n] == 0) return;

	if(Debug.verbose) console.log("Removing " + m.url + " node: " + n);
	m.status[n] = 0;

	if (m.georeq.readyState != 4) {
		m.georeq.abort();
		context.pending--;
	}

	context.cacheSize -= m.nsize[n];
	context.gl.deleteBuffer(m.vbo[n]);
	context.gl.deleteBuffer(m.ibo[n]);
	m.vbo[n] = m.ibo[n] = null;

	if(!m.vertex.texCoord) return;
	if (m.texreq && m.texreq.readyState != 4) m.texreq.abort();
	var tex = m.patches[m.nfirstpatch[n]*3+2]; //TODO assuming one texture per node
	m.texref[tex]--;

	if(m.texref[tex] == 0 && m.texids[tex]) {
		context.gl.deleteTexture(m.texids[tex]);
		m.texids[tex] = null;
	}
}

function requestNode(context, node) {
	var n = node.id;
	var m = node.mesh;

	m.status[n] = 2; //pending

	context.pending++;
	context.cacheSize += m.nsize[n];

	node.reqAttempt = 0;
	node.context = context;
	node.nvert = m.nvertices[n];
	node.nface = m.nfaces[n];

//	console.log("Requesting " + m.url + " node: " + n);
	requestNodeGeometry(context, node);
	requestNodeTexture(context, node);
}

function requestNodeGeometry(context, node) {
	var n = node.id;
	var m = node.mesh;

	m.status[n]++; //pending
	m.georeq = m.httpRequest(
		m.noffsets[n],
		m.noffsets[n+1],
		function() { loadNodeGeometry(this, context, node); },
		function() {
			if(Debug.verbose) console.log("Geometry request error!");
			recoverNode(context, node, 0);
		},
		function() {
			if(Debug.verbose) console.log("Geometry request abort!");
			removeNode(context, node);
		},
		'arraybuffer'
	);
}

function requestNodeTexture(context, node) {
	var n = node.id;
	var m = node.mesh;

	if(!m.vertex.texCoord) return;

	var tex = m.patches[m.nfirstpatch[n]*3+2];
	m.texref[tex]++;
	if(m.texids[tex])
		return;

	m.status[n]++; //pending

	m.texreq = m.httpRequest(
		m.textures[tex],
		m.textures[tex+1],
		function() { loadNodeTexture(this, context, node, tex); },
		function() {
			if(Debug.verbose) console.log("Texture request error!");
			recoverNode(context, node, 1);
		},
		function() {
			if(Debug.verbose) console.log("Texture request abort!");
			removeNode(context, node);
		},
		'blob'
	);
}

function recoverNode(context, node, id) {
	var n = node.id;
	var m = node.mesh;
	if(m.status[n] == 0) return;

	m.status[n]--;

	if(node.reqAttempt > maxReqAttempt) {
		if(Debug.verbose) console.log("Max request limit for " + m.url + " node: " + n);
		removeNode(context, node);
		return;
	}

	node.reqAttempt++;

	switch (id){
		case 0:
			requestNodeGeometry(context, node);
			if(Debug.verbose) console.log("Recovering geometry for " + m.url + " node: " + n);
			break;
		case 1:
			requestNodeTexture(context, node);
			if(Debug.verbose) console.log("Recovering texture for " + m.url + " node: " + n);
			break;
	}
}

function loadNodeGeometry(request, context, node) {
	var n = node.id;
	var m = node.mesh;
	if(m.status[n] == 0) return;

	node.buffer = request.response;

	if(!m.compressed)
		readyNode(node);
	else if(m.meco) {
		var sig = { texcoords: m.vertex.texCoord, normals:m.vertex.normal, colors:m.vertex.color, indices: m.face.index }
		var patches = [];
		for(var k = m.nfirstpatch[n]; k < m.nfirstpatch[n+1]; k++)
			patches.push(m.patches[k*3+1]);
		if(!meco) loadMeco();
		meco.postRequest(sig, node, patches);
	} else {
		if(!corto) loadCorto();
		corto.postRequest(node);
	}
}

function powerOf2(n) {
	return n && (n & (n - 1)) === 0;
}

function loadNodeTexture(request, context, node, texid) {
	var n = node.id;
	var m = node.mesh;
	if(m.status[n] == 0) return;

	var blob = request.response;

	var urlCreator = window.URL || window.webkitURL;
	var img = document.createElement('img');
	img.onerror = function(e) { console.log("Texture loading error!"); };
	img.src = urlCreator.createObjectURL(blob);

	var gl = context.gl;
	img.onload = function() {
		urlCreator.revokeObjectURL(img.src);

		var flip = gl.getParameter(gl.UNPACK_FLIP_Y_WEBGL);
		gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
		var tex = m.texids[texid] = gl.createTexture();
		gl.bindTexture(gl.TEXTURE_2D, tex);

//TODO some textures might be alpha only! save space
		var s = gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img);
		gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
		gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
		gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);

		if(gl instanceof WebGL2RenderingContext || (powerOf2(img.width) && powerOf2(img.height))) {
			gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST_MIPMAP_LINEAR);
			gl.generateMipmap(gl.TEXTURE_2D);
		} else {
			gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
		}

		gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, flip);

		m.status[n]--;

		if(m.status[n] == 2) {
			m.status[n]--; //ready
			node.reqAttempt = 0;
			node.context.pending--;
			node.instance.onUpdate && node.instance.onUpdate();
			updateCache(gl);
		}
	}
}

function scramble(n, coords, normals, colors) {
	while (n > 0) {
		var i = Math.floor(Math.random() * n);
		n--;
		for(var k =0; k < 3; k++) {
			var v = coords[n*3+k];
			coords[n*3+k] = coords[i*3+k];
			coords[i*3+k] = v;

			if(normals) {
				var v = normals[n*3+k];
				normals[n*3+k] = normals[i*3+k];
				normals[i*3+k] = v;
			}
			if(colors) {
				var v = colors[n*4+k];
				colors[n*4+k] = colors[i*4+k];
				colors[i*4+k] = v;
			}
		}
	}
}

function readyNode(node) {
	var m = node.mesh;
	var n = node.id;
	var nv = m.nvertices[n];
	var nf = m.nfaces[n];
	var model = node.model;

	var vertices;
	var indices;

	if(!m.corto) {
		indices  = new Uint8Array(node.buffer, nv*m.vsize,  nf*m.fsize);
		vertices = new Uint8Array(nv*m.vsize);
		var view = new Uint8Array(node.buffer, 0, nv*m.vsize);
		var v = view.subarray(0, nv*12);
		vertices.set(v);
		var off = nv*12;
		if(m.vertex.texCoord) {
			var uv = view.subarray(off, off + nv*8);
			vertices.set(uv, off);
			off += nv*8;
		}
		if(m.vertex.normal && m.vertex.color) {
			var no = view.subarray(off, off + nv*6);
			var co = view.subarray(off + nv*6, off + nv*6 + nv*4);
			vertices.set(co, off);
			vertices.set(no, off + nv*4);
		}
		else {
			if(m.vertex.normal) {
				var no = view.subarray(off, off + nv*6);
				vertices.set(no, off);
			}
			if(m.vertex.color) {
				var co = view.subarray(off, off + nv*4);
				vertices.set(co, off);
			}
		}
	} else {
		indices = node.model.index;
		vertices = new ArrayBuffer(nv*m.vsize);
		var v = new Float32Array(vertices, 0, nv*3);
		v.set(model.position);
		var off = nv*12;
		if(model.uv) {
			var uv = new Float32Array(vertices, off, nv*2);
			uv.set(model.uv);
			off += nv*8;
		}
		if(model.color) {
			var co = new Uint8Array(vertices, off, nv*4);
			co.set(model.color);
			off += nv*4;
		}
		if(model.normal) {
			var no = new Int16Array(vertices, off, nv*3);
			no.set(model.normal);
		}
	}

	if(nf == 0)
		scramble(nv, v, no, co);

	if(n == 1) {
		m.basev = new Float32Array(vertices, 0, nv*3);
		m.basei = new Uint16Array(indices, 0, nf*3);
	}

	var gl = node.context.gl;
	var vbo = m.vbo[n] = gl.createBuffer();
	gl.bindBuffer(gl.ARRAY_BUFFER, vbo);
	gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);
	var ibo = m.ibo[n] = gl.createBuffer();
	gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, ibo);
	gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, indices, gl.STATIC_DRAW);

	m.status[n]--;

	if(m.status[n] == 2) {
		m.status[n]--; //ready
		node.reqAttempt = 0;
		node.context.pending--;
		node.instance.onUpdate && node.instance.onUpdate();
		updateCache(gl);
	}
}

function flush(context, mesh) {
	for(var i = 0; i < mesh.nodesCount; i++)
		removeNode(context, {mesh:mesh, id: i });
}

function updateCache(gl) {
	var context = getContext(gl);

	var best = null;
	context.candidates.forEach(function(e) {
		if(e.mesh.status[e.id] == 0 && (!best || e.error > best.error)) best = e;
	});
	context.candidates = [];
	if(!best) return;

	while(context.cacheSize > context.maxCacheSize) {
		var worst = null;
		//find node with smallest error in cache
		context.meshes.forEach(function(m) {
			var n = m.nodesCount;
			for(i = 0; i < n; i++)
				if(m.status[i] == 1 && (!worst ||  m.errors[i] < worst.error))
					worst = {error: m.errors[i], frame: m.frames[i], mesh:m, id:i};
		});
		if(!worst || (worst.error >= best.error && worst.frame == best.frame))
			return;
		removeNode(context, worst);
	}

	if(context.pending < maxPending) {
		requestNode(context, best);
		updateCache(gl);
	}
}

//nodes are loaded asincronously, just update mesh content (VBO) cache size is kept globally.
//but this could be messy.

function getTargetError(gl)  { return getContext(gl).targetError; }
function getMinFps(gl)       { return getContext(gl).minFps; }
function getMaxCacheSize(gl) { return getContext(gl).maxCacheSize; }

function setTargetError(gl, error) { getContext(gl).targetError = error; }
function setMinFps(gl, fps)        { getContext(gl).minFps = fps; }
function setMaxCacheSize(gl, size) { getContext(gl).maxCacheSize = size; }

return { Mesh: Mesh, Renderer: Instance, Renderable: Instance, Instance:Instance,
	Debug: Debug, contexts: contexts, beginFrame:beginFrame, endFrame:endFrame, updateCache: updateCache, flush: flush,
	setTargetError:setTargetError, setMinFps: setMinFps, setMaxCacheSize:setMaxCacheSize, getTargetError:getTargetError, getMinFps: getMinFps, getMaxCacheSize:getMaxCacheSize };

}();
""",
        "corto.em": """
/*
Corto
Copyright (c) 2017-2020, Visual Computing Lab, ISTI - CNR
All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/

onmessage = async function(job) {
	if(typeof(job.data) == "string") return;

	var buffer = job.data.buffer;
	if(!buffer) return;
	if(!CortoDecoder.instance)
		await CortoDecoder.ready;

	var model = CortoDecoder.decode(buffer, job.data.short_index, job.data.short_normals, job.data.rgba_colors ? 4 : 3);
	postMessage({ model: model, buffer: buffer, request: job.data.request});
};

var CortoDecoder = (function() {
	"use strict";
	var wasm_base = "0061736D0100000001530D60037F7F7F0060027F7F0060017F017F60017F0060047F7F7F7F0060027F7F017F60057F7F7F7F7F0060037F7F7F017F60000060067F7F7F7F7F7F0060047F7F7F7F017F60077F7F7F7F7F7F7F006000017F02410203656E761F656D736372697074656E5F6E6F746966795F6D656D6F72795F67726F77746800030D776173695F756E737461626C650970726F635F65786974000303A401A2010302070107080C08070703010307050102080200010901010A00050003010405040501050101020008010402000603070402000605030802040500010203020401030300020204050100000404000200000004000102020100020302010005000606000000010600060A020003010003010101000203030102010000090901060605070504040007070503030302010B00000101010000010004000100030201020504050170013E3E05030100100608017F014190DD010B07FF0117066D656D6F727902000A6E65774465636F64657200A301076E67726F75707300760667726F7570730072056E76657274006C056E66616365003307686173417474720060096861734E6F726D616C005008686173436F6C6F72004705686173557600A2010C736574506F736974696F6E730099010C7365744E6F726D616C7333320094010C7365744E6F726D616C73313600900109736574436F6C6F7273008801067365745576730080010A736574496E6465783136007B0A736574496E64657833320079066465636F646500780D64656C6574654465636F6465720077065F7374617274002A066D616C6C6F63003904667265650002047362726B00120955010041010B3D285D5C5B696867666564635E5830575A2F565553522F59302D514F4C4AA0019F012D9E019D019C019A01970196012A401E8F018D01338C01401E3F3F8A011E89017E810187011E7F820186011E84010A89A303A2018C0D01077F02402000450D00200041786A22032000417C6A280200220141787122006A2105024020014101710D002001410371450D012003200328020022026B220341A8192802002204490D01200020026A2100200341AC19280200470440200241FF014D0440200328020822042002410376220241037441C0196A471A2004200328020C2201460440419819419819280200417E200277713602000C030B2004200136020C200120043602080C020B2003280218210602402003200328020C22014704402004200328020822024D0440200228020C1A0B2002200136020C200120023602080C010B0240200341146A220228020022040D00200341106A220228020022040D00410021010C010B0340200221072004220141146A220228020022040D00200141106A2102200128021022040D000B200741003602000B2006450D0102402003200328021C220241027441C81B6A22042802004604402004200136020020010D01419C19419C19280200417E200277713602000C030B20064110411420062802102003461B6A20013602002001450D020B2001200636021820032802102202044020012002360210200220013602180B20032802142202450D0120012002360214200220013602180C010B200528020422014103714103470D0041A019200036020020052001417E7136020420032000410172360204200020036A20003602000F0B200520034D0D0020052802042201410171450D0002402001410271450440200541B01928020046044041B019200336020041A41941A41928020020006A220036020020032000410172360204200341AC19280200470D0341A019410036020041AC1941003602000F0B200541AC1928020046044041AC19200336020041A01941A01928020020006A220036020020032000410172360204200020036A20003602000F0B200141787120006A21000240200141FF014D0440200528020C2102200528020822042001410376220141037441C0196A220747044041A8192802001A0B20022004460440419819419819280200417E200177713602000C020B2002200747044041A8192802001A0B2004200236020C200220043602080C010B2005280218210602402005200528020C220147044041A819280200200528020822024D0440200228020C1A0B2002200136020C200120023602080C010B0240200541146A220228020022040D00200541106A220228020022040D00410021010C010B0340200221072004220141146A220228020022040D00200141106A2102200128021022040D000B200741003602000B2006450D0002402005200528021C220241027441C81B6A22042802004604402004200136020020010D01419C19419C19280200417E200277713602000C020B20064110411420062802102005461B6A20013602002001450D010B2001200636021820052802102202044020012002360210200220013602180B20052802142202450D0020012002360214200220013602180B20032000410172360204200020036A2000360200200341AC19280200470D0141A01920003602000F0B20052001417E7136020420032000410172360204200020036A20003602000B200041FF014D04402000410376220141037441C0196A2100027F41981928020022024101200174220171450440419819200120027236020020000C010B20002802080B2102200020033602082002200336020C2003200036020C200320023602080F0B200342003702102003027F410020004108762201450D001A411F200041FFFFFF074B0D001A200120014180FE3F6A411076410871220174220220024180E01F6A411076410471220274220420044180800F6A411076410271220474410F7620012002722004726B22014101742000200141156A7641017172411C6A0B220236021C200241027441C81B6A21010240419C1928020022044101200274220771450440419C192004200772360200200120033602002003200336020C20032001360218200320033602080C010B20004100411920024101766B2002411F461B7421022001280200210102400340200122042802044178712000460D012002411D76210120024101742102200420014104716A220741106A28020022010D000B200720033602102003200336020C20032004360218200320033602080C010B20042802082200200336020C20042003360208200341003602182003200436020C200320003602080B41B81941B819280200417F6A220036020020000D0041E01C210303402003280200220041086A210320000D000B41B819417F3602000B0B2F01027F2000410120001B2100034002402000103922010D004194192802002202450D0020021108000C010B0B20010B820401037F20024180C0004F0440200020012002107C20000F0B200020026A210302402000200173410371450440024020024101480440200021020C010B2000410371450440200021020C010B200021020340200220012D00003A0000200141016A2101200241016A220220034F0D0120024103710D000B0B02402003417C71220441C000490D002002200441406A22054B0D0003402002200128020036020020022001280204360204200220012802083602082002200128020C36020C2002200128021036021020022001280214360214200220012802183602182002200128021C36021C2002200128022036022020022001280224360224200220012802283602282002200128022C36022C2002200128023036023020022001280234360234200220012802383602382002200128023C36023C200141406B2101200241406B220220054D0D000B0B200220044F0D01034020022001280200360200200141046A2101200241046A22022004490D000B0C010B20034104490440200021020C010B2003417C6A22042000490440200021020C010B200021020340200220012D00003A0000200220012D00013A0001200220012D00023A0002200220012D00033A0003200141046A2101200241046A220220044D0D000B0B200220034904400340200220012D00003A0000200141016A2101200241016A22022003470D000B0B20000BE40101067F0240024020002802082203200028020422026B20014F04400340200241003A00002000200028020441016A22023602042001417F6A22010D000C02000B000B2002200028020022046B220620016A2202417F4C0D01027F2002200320046B2203410174220720072002491B41FFFFFFFF07200341FFFFFFFF03491B220304402003100321050B200520066A22020B41002001100A1A0340200241016A21022001417F6A22010D000B200641014E044020052004200610041A0B200020053602002000200320056A360208200020023602042004450D00200410020B0F0B1007000B1C00200245044020002001460F0B20002802042001280204108B01450B080041F912100C000B05001038000B05001038000BF30202027F017E02402002450D00200020026A2203417F6A20013A0000200020013A000020024103490D002003417E6A20013A0000200020013A00012003417D6A20013A0000200020013A000220024107490D002003417C6A20013A0000200020013A000320024109490D002000410020006B41037122046A2203200141FF017141818284086C22013602002003200220046B417C7122046A2202417C6A200136020020044109490D002003200136020820032001360204200241786A2001360200200241746A200136020020044119490D002003200136021820032001360214200320013602102003200136020C200241706A20013602002002416C6A2001360200200241686A2001360200200241646A20013602002004200341047141187222046B22024120490D002001AD22054220862005842105200320046A2101034020012005370318200120053703102001200537030820012005370300200141206A2101200241606A2202411F4B0D000B0B20000BA50201037F230041406A220324002000280200220441786A28020021052004417C6A280200210420034100360214200320013602102003200036020C2003200236020841002101200341186A41004127100A1A200020056A2100024020042002410010060440200341013602382004200341086A200020004101410020042802002802141109002000410020032802204101461B21010C010B2004200341086A2000410141002004280200280218110600200328022C220041014B0D00200041016B0440200328021C410020032802284101461B410020032802244101461B410020032802304101461B21010C010B2003280220410147044020032802300D0120032802244101470D0120032802284101470D010B200328021821010B200341406B240020010B2D01027F100822022201419813360200200141C413360200200141046A2000109501200241F4133602001009000BF20101077F20002802082202200028020422036B41027520014F044020002003410020014102742200100A20006A3602040F0B02402003200028020022036B2206410275220720016A2205418080808004490440027F41002005200220036B2202410175220420042005491B41FFFFFFFF03200241027541FFFFFFFF01491B2202450D001A20024180808080044F0D022002410274100322080B220420074102746A41002001410274100A1A200641014E044020082003200610041A0B200020043602002000200420024102746A3602082000200420054102746A36020420030440200310020B0F0B1007000B41F009100C000B1B0002402000280208450D0020002802042200450D00200010020B0B4301037F02402002450D00034020002D0000220420012D00002205460440200141016A2101200041016A21002002417F6A22020D010C020B0B200420056B21030B20030B810101037F027F20002802142202200148044020004120200120026B22026B22013602142000200028020C220341046A36020C200041106A2104200028021020027420032802002202200176720C010B2000200220016B2201360214200041106A2104200028021022022001760B210320042002417F200174417F737136020020030B5501017F230041106B220224002000420037020020004100360208024020012C000B41004E044020002001280208360208200020012902003702000C010B2000200128020020012802041093010B200241106A24000B4A01017F41901D280200220120006A2200417F4C04404190194130360200417F0F0B024020003F004110744D0D002000107A0D004190194130360200417F0F0B41901D200036020020010B080041A812100C000B8F0101037F20002101024002402000410371450D0020002D00004504400C020B0340200141016A2201410371450D0120012D00000D000B0C010B03402001220241046A210120022802002203417F73200341FFFDFB776A7141808182847871450D000B200341FF0171450440200221010C010B034020022D00012103200241016A2201210220030D000B0B200120006B0BC50201067F027F20002802082204044020002802140C010B418002210420004180023602084180081003210320004280808080800437021020004100360200200020033602042000200336020C41200B220320024C0440200020002802102003742001200220036B767222083602100240200028020022032004480440200028020421060C010B417F20044103742004410174220541FEFFFFFF03712005471B1003220620002802042207200441027410042104200704402007100220002802084101742105200028020021030B20002005360208200020043602040B2000200341016A360200200620034102746A200836020020004100360210200028021421044120210320004120360214200220046B220241027441F0086A28020020017121010B200241014E04402000200320026B360214200020002802102002742001723602100B0B9D0101047F02402000280200220241014D0440200241016B450D012000280208220328000021022000200341046A2203360208024020022001280204200128020022046B22054B04402001200220056B100520012802002104200028020821030C010B200220054F0D002001200220046A3602040B2000200220036A36020820042003200210041A0F0B100822004199083602001009000B2000200110740B900201077F02402000280204200028020022076B220841186D220B41016A220641ABD5AAD5004904402006200028020820076B41186D2209410174220C200C2006491B41AAD5AAD500200941D5AAD52A491B22060440200641ABD5AAD5004F0D02200641186C1003210A0B2001280200210920022802002102200328020021032004280200210420052802002105200A200B41186C6A220141003A0014200120053602102001200436020C2001200336020820012002360204200120093602002001200841686D41186C6A2102200841014E044020022007200810041A0B200020023602002000200A200641186C6A3602082000200141186A36020420070440200710020B0F0B1007000B41AD11100C000B41002001044020002001280200101820002001280204101820012C0027417F4C0440200128021C10020B20012C001B417F4C0440200128021010020B200110020B0BFA0101067F20011071200041046A21062001280200210502402000280208200028020422026B2203417B4D044020064104100520002802082104200028020421020C010B2000200220036A41046A22043602080B200220036A20053602000240200420026B220320034104200341037122056B410020051B22076A220549044020062007100520002802082104200028020421020C010B200320054D0D002000200220056A22043602080B200128020421050240200420026B22042004200128020041027422016A2203490440200620011005200628020021020C010B200420034D0D002000200220036A3602080B200220046A2005200110041A0BFD0201047F20022D00012104024020012D0001220720002D00014D0440200441FF017120074D0D0120012F00002104200120022F00003B0000200220043B00004101210520012D000120002D00014D0440200441087621040C020B20002F00002104200020012F00003B0000200120043B000020022D00012104410221050C010B20002F00002106200441FF017120074B0440200020022F00003B0000200220063B000020064180FE03714108762104410121050C010B200020012F00003B0000200120063B00004101210520022D00012204200641087622074D0D00200120022F00003B0000200220063B000041022105200721040B20032D0001200441FF01714B047F20022F00002104200220032F00003B0000200320043B000020022D000120012D00014D0440200541016A0F0B20012F00002103200120022F00003B0000200220033B000020012D000120002D00014D0440200541026A0F0B20002F00002102200020012F00003B0000200120023B0000200541036A0520050B0B8E0201067F20002802082204200028020422036B41027520014F0440034020032002280200360200200341046A21032001417F6A22010D000B200020033602040F0B02402003200028020022066B2207410275220820016A2203418080808004490440027F41002003200420066B2204410175220520052003491B41FFFFFFFF03200441027541FFFFFFFF01491B2204450D001A20044180808080044F0D02200441027410030B220520084102746A2103034020032002280200360200200341046A21032001417F6A22010D000B200741014E044020052006200710041A0B200020053602002000200520044102746A3602082000200336020420060440200610020B0F0B1007000B41F009100C000B440020002001360208417F2001410274200141FFFFFFFF03712001471B1003210120004280808080800437021020004100360200200020013602042000200136020C20000BBF0101047F02402000280200220341014D0440200341016B450D01200041046A210602402000280208200028020422036B2204417B4D044020064104100520002802082105200028020421030C010B2000200320046A41046A22053602080B200320046A20013602000240200520036B2204200120046A2205490440200620011005200628020021030C010B200420054D0D002000200320056A3602080B200320046A2002200110041A0F0B10084199083602001009000B20002002200110750B0600200010020BC50101067F02402000280204200028020022046B2206410275220541016A2202418080808004490440027F41002002200028020820046B2203410175220720072002491B41FFFFFFFF03200341027541FFFFFFFF01491B2202450D001A20024180808080044F0D02200241027410030B220320054102746A22052001280200360200200641014E044020032004200610041A0B200020033602002000200320024102746A3602082000200541046A36020420040440200410020B0F0B1007000B41AD11100C000B850301047F230041306B22042400200441003602102004420037030802402001101422064170490440024002402006410B4F0440200641106A4170712207100321052004200741808080807872360210200420053602082004200636020C0C010B200420063A0013200441086A21052006450D010B20052001200610041A0B200520066A41003A0000200041146A2206200441086A1023210520042C0013417F4C0440200428020810020B2005200041186A470440200441003602102004420037030820011014220041704F0D02024002402000410B4F0440200041106A4170712207100321052004200741808080807872360210200420053602082004200036020C0C010B200420003A0013200441086A21052000450D010B20052001200010041A0B200020056A41003A00002004200441086A360220200441286A2006200441086A200441206A1022200428022828021C210020042C0013417F4C0440200428020810020B20002002360204200020033602140B200441306A24000F0B1013000B1013000B8D03010A7F230041106B2202240020024100360208200242003703002001101422034170490440024002402003410B4F0440200341106A417071220610032104200220064180808080787236020820022004360200200220033602040C010B200220033A000B200221042003450D010B20042001200310041A0B200320046A41003A000020022D000B2201411874411875210A027F410020002802182205450D001A20022802042001200A41004822001B21082002280200200220001B210B0340200541106A2107024002400240024002400240200528021420052D001B2200200041187441187541004822031B22062008200620084922011B22090440200B2007280200200720031B22042009100F22000D010B20082006490D052009450D022007280200200720031B21040C010B2000417F4C0D040B2004200B2009100F22000D010B20010D0141010C040B2000417F4C0D0041010C030B200541046A21050B200528020022050D000B41000B2100200A417F4C0440200228020010020B200241106A240020000F0B1013000BAA03010A7F0240200141046A220528020022040440200228020420022D000B2205200541187441187541004822051B21072002280200200220051B2108200141046A21050340200441106A21020240024002400240024002400240200428021420042D001B2206200641187441187541004822091B220A2007200A200749220C1B2206044020082002280200200220091B220B2006100F220D0D010B2007200A490D012006450D032002280200200220091B210B0C020B200D417F4A0D010B200428020022020D04200421050C070B200B20082006100F22020D010B200C0D010C050B2002417F4A0D040B200441046A210520042802042202450D03200521040B20042105200221040C00000B000B200521040B200020052802002202047F4100054120100322022003280200220329020037021020022003280208360218200342003702002003410036020820022004360208200242003702002002410036021C200520023602002002210420012802002802002203044020012003360200200528020021040B2001280204200410262001200128020841016A36020841010B3A0004200020023602000B9B0201087F02400240200041046A22052802002200450D00200128020420012D000B2202200241187441187541004822021B21032001280200200120021B210720052102034002402003200028021420002D001B2201200141187441187541004822091B2208200320084922041B22060440200041106A2201280200200120091B20072006100F22010D010B417F200420082003491B21010B2002200020014100481B210220002001411D764104716A28020022000D000B20022005460D000240200228021420022D001B2200200041187441187541004822061B2204200320042003491B220104402007200241106A2200280200200020061B2001100F22000D010B20032004490D010C020B2000417F4A0D010B200521020B20020B2F002001044020002001280200102420002001280204102420012C001B417F4C0440200128021010020B200110020B0B5701027F2000420037020020004100360208024020010440200141D6AAD5AA014F0D0120002001410C6C2201100322023602002000200120026A2203360208200241002001100A1A200020033602040B20000F0B1007000B9C0401037F2001200020014622033A000C024020030D000340200128020822032D000C0D0102402003200328020822022802002204460440024020022802042204450D0020042D000C0D000C020B024020012003280200460440200321010C010B200320032802042201280200220036020420012000047F2000200336020820032802080520020B36020820032802082200200041046A20002802002003461B20013602002001200336020020032001360208200128020821020B200141013A000C200241003A000C200220022802002200280204220136020020010440200120023602080B2000200228020836020820022802082201200141046A20012802002002461B200036020020002002360204200220003602080F0B02402004450D0020042D000C0D000C010B024020012003280200470440200321010C010B20032001280204220036020020012000047F2000200336020820032802080520020B36020820032802082200200041046A20002802002003461B20013602002001200336020420032001360208200128020821020B200141013A000C200241003A000C200220022802042200280200220136020420010440200120023602080B2000200228020836020820022802082201200141046A20012802002002461B200036020020002002360200200220003602080C020B2004410C6A2101200341013A000C200220002002463A000C200141013A0000200222012000470D000B0B0BC60E01097F024003402001417F6A210A2001417E6A210803402000210203400240024002400240200120026B2203410175220041054D0440024002400240200041026B0E0400010402070B2001417F6A2D000020022D00014D0D0620022F0000210020022001417E6A22012F00003B0000200120003B00000F0B2001417E6A21002001417F6A22072D0000210320022D0003220420022D00014D0440200320044D0D0620022F00022101200220002F00003B0002200020013B000020022D000320022D00014D0D0620022F000221000C0A0B20022F00002101200320044B0440200220002F00003B0000200020013B00000F0B20022F00022103200220013B0002200220033B000020072D000020014180FE03714108764D0D05200220002F00003B0002200020013B00000F0B2002200241026A200241046A200241066A101A1A2001417F6A2D0000200241076A2D00004D0D0420022F0006210020022001417E6A22012F00003B0006200120003B000020022D000720022D00054D0D0420022F00062100200220022F00043B0006200220003B000420022D0003200041087622014F0D04200220022F00023B0004200220003B000220022D000120014F0D040C080B2003413D4C044020022D00052100024020022D0003220420022D000122034D0440200020044D0D0120022F00042100200220022F00023B0004200220003B0002200320004108764F0D01200220022F00003B0002200220003B00000C010B20022F00002103200020044B044020022F00042100200220033B0004200220003B00000C010B20022F00022104200220033B0002200220043B0000200020034180FE03714108764D0D0020022F00042100200220033B0004200220003B00020B200241066A22002001460D04200241046A21040340200022072D000120042D00014B044020072F00002208410876210520072103034002402003200422002F00003B000020002002460440200221000C010B2000417E6A2104200021032000417F6A2D00002005490D010B0B200020083B00000B2007220441026A22002001470D000B0C040B2002200041026D41017422096A21050240200341CF0F4E044020022002200041046D41017422036A22002005200320056A2203101A2106200A2D000020032D00014D0D0120032F00002104200320082F00003B0000200820043B000020032D0001200220096A220441016A2D00004D0440200641016A21060C020B20052F00002107200520032F00003B0000200320073B000020042D000120002D00014D0440200641026A21060C020B20002F00002103200020052F00003B0000200520033B000020002D000120022D00014D0440200641036A21060C020B20022F00002103200220002F00003B0000200020033B0000200641046A21060C010B200A2D000021030240200220096A220041016A2D0000220420022D00014D044041002106200320044D0D0220052F00002103200520082F00003B0000200820033B00004101210620002D000120022D00014D0D0220022F00002100200220052F00003B0000200520003B00000C010B20022F00002100200320044B0440200220082F00003B0000200820003B0000410121060C020B200220052F00003B0000200520003B000041012106200A2D000020004180FE03714108764D0D01200520082F00003B0000200820003B00000B410221060B2008210402402002220741016A2D00002203200220096A2D000122024B0440200821000C010B03402004417E6A22002007460440200741026A21042003200A2D00004B0D0520042008460D060340200320042D00014B044020042F00002100200420082F00003B0000200820003B0000200441026A21040C070B200441026A22042008470D000B0C060B2004417F6A21092000210420092D000020024D0D000B20072F00002103200720002F00003B0000200020033B0000200641016A21060B200741026A220320004F0D01034020052D0001210403402003220241026A210320022D000120044B0D000B03402000417F6A21092000417E6A210020092D000020044D0D000B200220004B0440200221030C030520022F00002104200220002F00003B0000200020043B00002000200520022005461B2105200641016A21060C010B00000B000B2002200241026A200241046A2001417E6A101A1A0C020B024020032005460D0020052D000120032D00014D0D0020032F00002100200320052F00003B0000200520003B0000200641016A21060B20064504402007200310362102200341026A220020011036044020032101200721002002450D060C030B20020D040B200320076B200120036B480440200720031027200341026A21000C040B200341026A2001102720032101200721000C040B200420082200460D00034020072D0001210303402004220241026A2104200320022D00014D0D000B03402000417F6A21052000417E6A2100200320052D00004B0D000B200220004F0D0220022F00002103200220002F00003B0000200020033B00000C00000B000B0B0B0B0F0B200220022F00003B0002200220003B00000B1400200041C413360200200041046A108E0120000B10002002044020002001200210041A0B0B0300010BE803010A7F230041306B220324002001280208220428000021022001200441046A360208200041206A21050240200220002802242204200028022022076B41047522064B04402005200220066B10A101200028022421040C010B200220064F0D002004200720024104746A22024704400340200441746A200441786A2802001018200441706A22042002470D000B0B20002002360224200221040B20042005280200220547044003402005200128020822022800003602002001200241056A2200360208024020022D00042208450D00200541046A210941002106034002402001200041026A220720002F00006A22003602082001200041026A220A20002F00006A360208200341003602102003420037030820071014220241704F0D00024002402002410B4F0440200241106A417071220B100321002003200B41808080807872360210200320003602082003200236020C0C010B200320023A0013200341086A21002002450D010B20002007200210041A0B200020026A41003A00002003200341086A360220200341286A2009200341086A200341206A102C2003280228411C6A200A103D20032C0013417F4C0440200328020810020B200641016A22062008460D02200128020821000C010B0B1013000B200541106A22052004470D000B0B200341306A24000BB103010A7F0240200141046A220528020022040440200228020420022D000B2205200541187441187541004822051B21072002280200200220051B2108200141046A21050340200441106A21020240024002400240024002400240200428021420042D001B2206200641187441187541004822091B220A2007200A200749220C1B2206044020082002280200200220091B220B2006100F220D0D010B2007200A490D012006450D032002280200200220091B210B0C020B200D417F4A0D010B200428020022020D04200421050C070B200B20082006100F22020D010B200C0D010C050B2002417F4A0D040B200441046A210520042802042202450D03200521040B20042105200221040C00000B000B200521040B200020052802002202047F410005412810032202200328020022032902003702102002200328020836021820034200370200200341003602082002200436020820024200370200200241003602242002420037021C200520023602002002210420012802002802002203044020012003360200200528020021040B2001280204200410262001200128020841016A36020841010B3A0004200020023602000B040041010B9D0301077F230041306B220324002003420037032820034200370320200342003703182000280208220628000021042000200641046A2205360208200520002802046B410371220604402000200520066B41046A22053602080B2003420037022820034100360220200320043602182003200536021C200320053602242000200028020820044102746A3602082003410036021020034200370308024020024101480D000240200145044003402000200341086A1016200741016A22072002470D000B20032802082104200328020C1A0C010B03402000200341086A101641002105200328020C2208210420032802082206200847044003400240200520066A22092D000022044504402001200220056C20076A6A41003A00000C010B2001200220056C20076A6A4100200341186A200410102204410120092D0000417F6A7422066A6B200420042006481B3A000020032802082106200328020C21080B200541016A22052008200622046B490D000B0B200741016A22072002470D000B0B2004450D002003200436020C200410020B200341186A100E200341306A24000B0300010B3A01017F2000418410360200200028022C2201044020002001360230200110020B20002802202201044020002001360224200110020B200010020B970301077F230041306B220324002003420037032820034200370320200342003703182000280208220428000021052000200441046A2204360208200420002802046B410371220604402000200420066B41046A22043602080B2003420037022820034100360220200320053602182003200436021C200320043602242000200028020820054102746A36020820034100360210200342003703082000200341086A1016200328020C2206200328020822006B210402402001450D002004450D0020024101480440410021010340200141016A22012004490D000B0C010B200241027421084100210503402001200220056C4102746A21070240200020056A22092D00002204044041012004744101752106410021000340200720004102746A200341186A200441FF0171101020066B3602002002200041016A220047044020092D000021040C010B0B20032802082100200328020C21060C010B200741002008100A1A0B200541016A2205200620006B2204490D000B0B200004402003200036020C200010020B200341186A100E200341306A240020040B960501097F230041306B22062400200641186A2001101C210A200641003602102006420037030802402001450D0002402001417F4A044020062001100322053602082006200536020C2006200120056A360210200121040340200541003A00002006200628020C41016A220536020C2004417F6A22040D000B2001450D0220034102480D01034002402002200320096C4102746A220C280200220741016A220441014D0440200441016B450D01410121070C010B2007411F7520077321044102210503402005220741016A2105200441017522040D000B0B4101210B03400240200C200B4102746A280200220841016A220441014D0440200441016B450D01410121080C010B2008411F7520087321054102210403402004220841016A2104200541017522050D000B0B2008200720072008491B2107200B41016A220B2003470D000B200628020820096A20073A000002402007450D0020034101480D0041012007417F6A742104410021050340200A200C20054102746A28020020046A20071015200541016A22052003470D000B0B200941016A22092001470D000B0C020B1007000B03400240024002402002200320096C4102746A2207280200220441016A220841014D044041012104200841016B0D010C020B2004411F7520047321054102210803402008220441016A2108200541017522050D000B0B200628020820096A20043A000020034101480D0141012004417F6A742108410021050340200A200720054102746A28020020086A20041015200541016A22052003470D000B0C010B200628020820096A41003A00000B200941016A22092001470D000B0B2000200A10192000200628020C200628020822006B2000101D2006280208220004402006200036020C200010020B200A100E200641306A24000B070020002802040BC50201057F02400240024020002802082205200028020422036B410C6D20014F04400340200320022902003702002003200228020836020820002000280204410C6A22033602042001417F6A22010D000C02000B000B2003200028020022046B410C6D220620016A220341D6AAD5AA014F0D01027F41002003200520046B410C6D2205410174220420042003491B41D5AAD5AA01200541AAD5AAD500491B2205450D001A200541D6AAD5AA014F0D032005410C6C10030B22072006410C6C6A22042103034020032002290200370200200320022802083602082003410C6A21032001417F6A22010D000B20042000280204200028020022016B220241746D410C6C6A2104200241014E044020042001200210041A0B20002004360200200020072005410C6C6A360208200020033602042001450D00200110020B0F0B1007000B41800E100C000B880302097F067D230041106B220524002004200428020036020420054100360208200542003703002000044020042000200510340B200241036C220041014E0440200320004102746A210A20042802002106034020012003280208410C6C220B6A2207280200210C20012003280204410C6C220D6A2208280200210420012003280200410C6C22026A22092802002100200220066A220220022A02002008280204B22009280204B222109322122007280208B22009280208B2220E93220F942008280208B2200E93220E2007280204B2201093221394932211923802002002200E200CB22000B2220E932210942004B2200E93220E200F9493220F20022A0204923802042002200E201394201220109493220E20022A0208923802082006200D6A2200201120002A0200923802002000200F20002A0204923802042000200E20002A0208923802082006200B6A2200201120002A0200923802002000200F20002A0204923802042000200E20002A0208923802082003410C6A2203200A490D000B0B200541106A24000BAF0601077F41012102024002400240200120006B410175220341054D04400240024002400240200341026B0E0400010203050B2001417F6A2D000020002D00014D0D0420002F0000210220002001417E6A22002F00003B0000200020023B00000C060B2001417E6A21032001417F6A22062D0000210420002D0003220520002D00014D0440200420054D0D0420002F00022101200020032F00003B0002200320013B000020002D000320002D00014D0D0420002F000221010C050B20002F00002101200420054B0440200020032F00003B0000200320013B00000C060B20002F00022104200020013B0002200020043B000020062D000020014180FE03714108764D0D03200020032F00003B0002200320013B00000C050B2000200041026A200041046A2001417E6A101A1A0C040B2000200041026A200041046A200041066A101A1A2001417F6A2D000020002D00074D0D0120002F0006210320002001417E6A22012F00003B0006200120033B000020002D000720002D00054D0D0120002F00062101200020002F00043B0006200020013B000420002D0003200141087622034F0D01200020002F00023B0004200020013B000220002D000120034F0D010C020B20002D00052102024020002D0003220420002D000122034D0440200220044D0D0120002F00042102200020002F00023B0004200020023B0002200320024108764F0D01200020002F00003B0002200020023B00000C010B20002F00002103200220044B044020002F00042102200020033B0004200020023B00000C010B20002F00022104200020033B0002200020043B0000200220034180FE03714108764D0D0020002F00042102200020033B0004200020023B00020B2001200041066A2202460D02200041046A210402400340200222032D000120042D00014B044020032F00002207410876210820032105034002402005200422022F00003B000020002002460440200021020C010B2002417E6A2104200221052002417F6A2D00002008490D010B0B200220073B0000200641016A22064108460D020B2003220441026A22022001470D000B0C030B200341026A20014621020B20020F0B200020002F00003B0002200020013B00000B41010B940F01177F230041206B2205240002402000280210200028020C6B221441017522064102490D002000280204210220054100360218200542003703100240027F0240027F02400240024002404101200274220B4101742204044020044180808080044F0D012005200B4103742201100322023602102005200220044102746A3602182005200241002001100A20016A3602140B200041186A210F02402004200028021C200028021822026B41027522014B0440200F200420016B100D0C010B200420014F0D002000200220044102746A36021C0B200041246A2110024020042000280228200028022422026B41027522014B04402010200420016B100D0C010B200420014F0D002000200220044102746A3602280B200041306A210E02402000280234200028023022026B220141FF3F4D0440200E4180C00020016B10050C010B20014180C000460D00200020024180406B3602340B200541003602082005420037030002402014044020064180808080044F0D01200520144101742202100322073602002005200720064102746A3602082005200741002002100A20026A3602040B200B417F6A22172006417F6A22166E2104200028020C22022D000341087421014102210320022D000122084108742212210A03400240200A20126C411076210A2003220920044F0D00200941016A2103200A20014B0D010B0B2009410F4D044020140D03410021014100210241000C080B200E28020020022D00003A00002009417F6A210C41012101200641014D0D034101210203402001200C6A2107200028020C210303402001220420002802306A20032D00003A0000200028020C2103200141016A22012007470D000B200E28020020076A200320024101746A2D00003A0000200441026A2101200241016A22022006470D000B200528020022022006200C6C221336020041012103200641014D0D040340200220034102746A2003360200200341016A22032006470D000B20052802102215200641014D0D051A2000280224210D20002802182111200028020C210E41002102034041012103200241016A2104200220066C210C024020020440034020152003200C6A41027422076A200E20034101746A2D0001200A6C410874411076360200200720116A200320096C20026B3602002007200D6A2004360200200341016A22032006470D000C02000B000B034020152003200C6A41027422076A200E20034101746A2D0001410874360200200720116A200320096C3602002007200D6A2004360200200341016A22032006470D000B0B200A20126C411076201220021B210A200422022009470D000B200528021021080C060B1007000B1007000B4100210103402007200141027422046A2001360200200528021020046A200841FF0171410874360200200F28020020046A2001360200201028020020046A4101360200200E28020020016A200220014101746A2D00003A0000200141016A220120064F04402001210220060C0605200028020C220220014101746A2D00012108200528020021070C010B00000B000B20052802002006200C6C22133602000B20052802100B2108410021030340200A20126C411076201220031B210A200341016A22032009470D000B2010280200210D200F28020021110B2008201341027422026A200A360200200220116A41003602002002200D6A2009360200200620096C2102200920166C41016A0B220D200B4F0D00201404400340410021032005280210210A2005280200210941002108410021070340200A200920034102746A2802004102746A28020022042008200420084B22041B21082003200720041B2107200341016A22032006490D000B201028020022112009200741027422156A28020041027422046A280200221341016A210E2004200A6A280200410874210C200F280200220820046A28020021074100210303400240200A200241027422046A200C20034101742209200028020C6A2D00016C411076360200200420086A2001360200200420116A200E3602002000280230220420016A200420076A201310041A200120136A220120002802306A200028020C20096A2D00003A0000200241016A2102200141016A21012003200D6A2017460D00200341016A220320064F0D0020102802002111200F28020021082005280210210A0C010B0B20032006460440200528020020156A2204200428020020066A3602000B200D20166A220D200B490D000C02000B000B0340200D20166A220D200B490D000B0B200204402005280200210C4100210141002103410021080340200C2001410020012006491B22074102746A28020020034D0440200F2802002209200841027422016A2009200341027422046A2802003602002001201028020022016A200120046A280200360200200841016A21080B200741016A2101200341016A22032002470D000B0B0240200B200028021C200028021822026B41027522014B0440200F200B20016B100D0C010B200B20014F0D0020002002200B4102746A36021C0B0240200B2000280228200028022422026B41027522014B04402010200B20016B100D0C010B200B20014F0D0020002002200B4102746A3602280B20052802002200044020052000360204200010020B20052802102200450D0020052000360214200010020B200541206A24000B070041011001000BC82D010B7F230041106B220B240002400240024002400240024002400240024002400240200041F4014D0440419819280200220641102000410B6A4178712000410B491B2205410376220076220141037104402001417F7341017120006A2202410374220441C8196A280200220141086A2100024020012802082203200441C0196A22044604404198192006417E200277713602000C010B41A8192802001A2003200436020C200420033602080B200120024103742202410372360204200120026A220120012802044101723602040C0C0B200541A01928020022084D0D0120010440024041022000742202410020026B722001200074712200410020006B71417F6A22002000410C764110712200762201410576410871220220007220012002762200410276410471220172200020017622004101764102712201722000200176220041017641017122017220002001766A2202410374220341C8196A28020022012802082200200341C0196A22034604404198192006417E2002777122063602000C010B41A8192802001A2000200336020C200320003602080B200141086A210020012005410372360204200120056A22072002410374220220056B2203410172360204200120026A2003360200200804402008410376220441037441C0196A210141AC192802002102027F20064101200474220471450440419819200420067236020020010C010B20012802080B2104200120023602082004200236020C2002200136020C200220043602080B41AC19200736020041A01920033602000C0C0B419C19280200220A450D01200A4100200A6B71417F6A22002000410C764110712200762201410576410871220220007220012002762200410276410471220172200020017622004101764102712201722000200176220041017641017122017220002001766A41027441C81B6A280200220128020441787120056B210320012102034002402002280210220045044020022802142200450D010B200028020441787120056B22022003200220034922021B21032000200120021B2101200021020C010B0B200128021821092001200128020C220447044041A819280200200128020822004D0440200028020C1A0B2000200436020C200420003602080C0B0B200141146A2202280200220045044020012802102200450D03200141106A21020B0340200221072000220441146A220228020022000D00200441106A2102200428021022000D000B200741003602000C0A0B417F2105200041BF7F4B0D002000410B6A22004178712105419C192802002207450D00410020056B2102024002400240027F410020004108762200450D001A411F200541FFFFFF074B0D001A200020004180FE3F6A411076410871220074220120014180E01F6A411076410471220174220320034180800F6A411076410271220374410F7620002001722003726B22004101742005200041156A7641017172411C6A0B220841027441C81B6A2802002203450440410021000C010B20054100411920084101766B2008411F461B7421014100210003400240200328020441787120056B220620024F0D0020032104200622020D0041002102200321000C030B200020032802142206200620032001411D764104716A2802102203461B200020061B21002001200341004774210120030D000B0B200020047245044041022008742200410020006B722007712200450D032000410020006B71417F6A22002000410C764110712200762201410576410871220320007220012003762200410276410471220172200020017622004101764102712201722000200176220041017641017122017220002001766A41027441C81B6A28020021000B2000450D010B0340200028020441787120056B220320024921012003200220011B21022000200420011B210420002802102201047F20010520002802140B22000D000B0B2004450D00200241A01928020020056B4F0D00200428021821082004200428020C220147044041A819280200200428020822004D0440200028020C1A0B2000200136020C200120003602080C090B200441146A2203280200220045044020042802102200450D03200441106A21030B0340200321062000220141146A220328020022000D00200141106A2103200128021022000D000B200641003602000C080B41A019280200220120054F044041AC1928020021000240200120056B220241104F044041A019200236020041AC19200020056A220336020020032002410172360204200020016A2002360200200020054103723602040C010B41AC19410036020041A019410036020020002001410372360204200020016A220120012802044101723602040B200041086A21000C0A0B41A419280200220120054B044041A419200120056B220136020041B01941B019280200220020056A22023602002002200141017236020420002005410372360204200041086A21000C0A0B410021002005412F6A2204027F41F01C280200044041F81C2802000C010B41FC1C427F37020041F41C4280A0808080800437020041F01C200B410C6A41707141D8AAD5AA057336020041841D410036020041D41C41003602004180200B22026A2206410020026B220771220220054D0D0941D01C2802002203044041C81C280200220820026A220920084D0D0A200920034B0D0A0B41D41C2D00004104710D040240024041B0192802002203044041D81C210003402000280200220820034D0440200820002802046A20034B0D030B200028020822000D000B0B410010122201417F460D052002210641F41C2802002200417F6A22032001710440200220016B200120036A410020006B716A21060B200620054D0D05200641FEFFFFFF074B0D0541D01C2802002200044041C81C280200220320066A220720034D0D06200720004B0D060B2006101222002001470D010C070B200620016B200771220641FEFFFFFF074B0D04200610122201200028020020002802046A460D03200121000B200021010240200541306A20064D0D00200641FEFFFFFF074B0D002001417F460D0041F81C2802002200200420066B6A410020006B71220041FEFFFFFF074B0D0620001012417F470440200020066A21060C070B410020066B10121A0C040B2001417F470D050C030B410021040C070B410021010C050B2001417F470D020B41D41C41D41C2802004104723602000B200241FEFFFFFF074B0D012002101222014100101222004F0D012001417F460D012000417F460D01200020016B2206200541286A4D0D010B41C81C41C81C28020020066A2200360200200041CC1C2802004B044041CC1C20003602000B02400240024041B0192802002203044041D81C21000340200120002802002202200028020422046A460D02200028020822000D000B0C020B41A81928020022004100200120004F1B45044041A81920013602000B4100210041DC1C200636020041D81C200136020041B819417F36020041BC1941F01C28020036020041E41C410036020003402000410374220241C8196A200241C0196A2203360200200241CC196A2003360200200041016A22004120470D000B41A419200641586A2200417820016B4107714100200141086A4107711B22026B220336020041B019200120026A220236020020022003410172360204200020016A412836020441B41941801D2802003602000C020B20002D000C4108710D00200120034D0D00200220034B0D002000200420066A36020441B0192003417820036B4107714100200341086A4107711B22006A220136020041A41941A41928020020066A220220006B220036020020012000410172360204200220036A412836020441B41941801D2802003602000C010B200141A819280200220449044041A8192001360200200121040B200120066A210241D81C2100024002400240024002400240034020022000280200470440200028020822000D010C020B0B20002D000C410871450D010B41D81C210003402000280200220220034D0440200220002802046A220420034B0D030B200028020821000C00000B000B200020013602002000200028020420066A3602042001417820016B4107714100200141086A4107711B6A220920054103723602042002417820026B4107714100200241086A4107711B6A220120096B20056B2100200520096A21072001200346044041B019200736020041A41941A41928020020006A2200360200200720004101723602040C030B200141AC1928020046044041AC19200736020041A01941A01928020020006A220036020020072000410172360204200020076A20003602000C030B2001280204220241037141014604402002417871210A0240200241FF014D0440200128020822032002410376220441037441C0196A471A2003200128020C2202460440419819419819280200417E200477713602000C020B2003200236020C200220033602080C010B2001280218210802402001200128020C22064704402004200128020822024D0440200228020C1A0B2002200636020C200620023602080C010B0240200141146A220328020022050D00200141106A220328020022050D00410021060C010B0340200321022005220641146A220328020022050D00200641106A2103200628021022050D000B200241003602000B2008450D0002402001200128021C220241027441C81B6A22032802004604402003200636020020060D01419C19419C19280200417E200277713602000C020B20084110411420082802102001461B6A20063602002006450D010B2006200836021820012802102202044020062002360210200220063602180B20012802142202450D0020062002360214200220063602180B2001200A6A21012000200A6A21000B20012001280204417E7136020420072000410172360204200020076A2000360200200041FF014D04402000410376220141037441C0196A2100027F41981928020022024101200174220171450440419819200120027236020020000C010B20002802080B2101200020073602082001200736020C2007200036020C200720013602080C030B2007027F410020004108762201450D001A411F200041FFFFFF074B0D001A200120014180FE3F6A411076410871220174220220024180E01F6A411076410471220274220320034180800F6A411076410271220374410F7620012002722003726B22014101742000200141156A7641017172411C6A0B220136021C20074200370210200141027441C81B6A21020240419C1928020022034101200174220471450440419C192003200472360200200220073602000C010B20004100411920014101766B2001411F461B742103200228020021010340200122022802044178712000460D032003411D76210120034101742103200220014104716A220428021022010D000B200420073602100B200720023602182007200736020C200720073602080C020B41A419200641586A2200417820016B4107714100200141086A4107711B22026B220736020041B019200120026A220236020020022007410172360204200020016A412836020441B41941801D28020036020020032004412720046B4107714100200441596A4107711B6A41516A22002000200341106A491B2202411B360204200241E01C290200370210200241D81C29020037020841E01C200241086A36020041DC1C200636020041D81C200136020041E41C4100360200200241186A2100034020004107360204200041086A2101200041046A210020012004490D000B20022003460D0320022002280204417E713602042003200220036B220441017236020420022004360200200441FF014D04402004410376220141037441C0196A2100027F41981928020022024101200174220171450440419819200120027236020020000C010B20002802080B2101200020033602082001200336020C2003200036020C200320013602080C040B200342003702102003027F410020044108762200450D001A411F200441FFFFFF074B0D001A200020004180FE3F6A411076410871220074220120014180E01F6A411076410471220174220220024180800F6A411076410271220274410F7620002001722002726B22004101742004200041156A7641017172411C6A0B220036021C200041027441C81B6A21010240419C1928020022024101200074220671450440419C19200220067236020020012003360200200320013602180C010B20044100411920004101766B2000411F461B742100200128020021010340200122022802044178712004460D042000411D76210120004101742100200220014104716A220628021022010D000B20062003360210200320023602180B2003200336020C200320033602080C030B20022802082200200736020C20022007360208200741003602182007200236020C200720003602080B200941086A21000C050B20022802082200200336020C20022003360208200341003602182003200236020C200320003602080B41A419280200220020054D0D0041A419200020056B220136020041B01941B019280200220020056A22023602002002200141017236020420002005410372360204200041086A21000C030B4190194130360200410021000C020B02402008450D000240200428021C220041027441C81B6A220328020020044604402003200136020020010D01419C192007417E2000777122073602000C020B20084110411420082802102004461B6A20013602002001450D010B2001200836021820042802102200044020012000360210200020013602180B20042802142200450D0020012000360214200020013602180B02402002410F4D04402004200220056A2200410372360204200020046A220020002802044101723602040C010B20042005410372360204200420056A22032002410172360204200220036A2002360200200241FF014D04402002410376220141037441C0196A2100027F41981928020022024101200174220171450440419819200120027236020020000C010B20002802080B2101200020033602082001200336020C2003200036020C200320013602080C010B2003027F410020024108762200450D001A411F200241FFFFFF074B0D001A200020004180FE3F6A411076410871220074220120014180E01F6A411076410471220174220520054180800F6A411076410271220574410F7620002001722005726B22004101742002200041156A7641017172411C6A0B220036021C20034200370210200041027441C81B6A21010240024020074101200074220571450440419C192005200772360200200120033602000C010B20024100411920004101766B2000411F461B742100200128020021050340200522012802044178712002460D022000411D76210520004101742100200120054104716A220628021022050D000B200620033602100B200320013602182003200336020C200320033602080C010B20012802082200200336020C20012003360208200341003602182003200136020C200320003602080B200441086A21000C010B02402009450D000240200128021C220041027441C81B6A220228020020014604402002200436020020040D01419C19200A417E200077713602000C020B20094110411420092802102001461B6A20043602002004450D010B2004200936021820012802102200044020042000360210200020043602180B20012802142200450D0020042000360214200020043602180B02402003410F4D04402001200320056A2200410372360204200020016A220020002802044101723602040C010B20012005410372360204200120056A22042003410172360204200320046A2003360200200804402008410376220541037441C0196A210041AC192802002102027F41012005742205200671450440419819200520067236020020000C010B20002802080B2105200020023602082005200236020C2002200036020C200220053602080B41AC19200436020041A01920033602000B200141086A21000B200B41106A240020000BA30100200041013A0035024020002802042002470D00200041013A00342000280210220245044020004101360224200020033602182000200136021020034101470D0120002802304101470D01200041013A00360F0B2001200246044020002802182202410246044020002003360218200321020B20002802304101470D0120024101470D01200041013A00360F0B200041013A00362000200028022441016A3602240B0B4E01017F02402001450D00200141DC1441DC16100B2201450D0020012802082000280208417F73710D00200028020C200128020C41001006450D00200028021020012802104100100621020B20020B5D01017F200028021022034504402000410136022420002002360218200020013602100F0B02402001200346044020002802184102470D01200020023602180F0B200041013A0036200041023602182000200028022441016A3602240B0B0D0020002001200110141092010B1400417F200049044041B512100C000B200010030B0300010B040020000B981702137F017E23004190016B22042400200441003602880120044200370380010240200028027022050440200541ABD5AAD5004F0D012004200541186C2206100322053602840120042005360280012004200520066A360288010B20044100360278200442003703700240200220016B2205410176220604402005417F4C0D0120042006410274220610032205360274200420053602702004200520066A3602780B200441003602682004420037036041C000200035020042018879A76B21052004417F36025C0240200220014D0D00200541016A210D200041D8006A210C2004412C6A2114200441186A2112200441D0006A210F200441CC006A2113200441C8006A210E200441C4006A21100340027F024002400240200428025C2205417F460440024020112004280274200428027022056B4102754F044020042802642004280260470D01200028028401210520032003280200220741016A3602002005417F6A2105410021062004027F02402007200028024C6A2D00004106470D00200C410310102206410171450D00200C200D10100C010B2000280234200028028401410C6C6A2207200536020820072005360204200720053602002000200028028401220541016A3602840120050B22073602400240200028022422090440200920014101746A20073B01000C010B200028022020014102746A20073602000B2006410271450D05200C200D10100C060B2004200520114102746A2802002205360258201141016A21110C030B2004280264220520042802604704402005417C6A22062802002105200420063602640C020B10084180113602001009000B2004417F36025C0B200420053602580B200F2004280280012207200541186C6A2206290210370300200E200629020837030020042006290200370340024020042D00540D0020032003280200220641016A3602002006200028024C6A2D0000220A4104460D0020042004280240221536023C20042004280244221636023820042007200428024C41186C6A2209290208370328200420092902103703302004200929020037032020042007200428025041186C6A220829020837031020122008290210370300200420082902003703082004200428028401220620076B41186D220B36025C2004417F3602040240200A41064B0D000240024002400240024002400240200A41016B0E06030406070500010B200C200D101021050C010B2000280234200028028401410C6C6A2205200428024836020820052015360204200520163602002000200028028401220541016A360284010B200420053602042004280280012206200428024C41186C6A200428025C3602102006200428025041186C6A200428025C41016A36020C2004200428025C41016A220736020002402004280284012205200428028801490440200428023C2109200428020421082004280238210A200428024C210B200541003A0014200520073602102005200B36020C2005200A36020820052008360204200520093602002004200541186A2205360284010C010B20044180016A2004413C6A200441046A200441386A201320041017200428028401210520042802800121060B2004200520066B41186D22073602000240200428027422062004280278490440200620073602002004200641046A3602740C010B200441F0006A2004101F20042802840121050B20052004280288014904402004280204210620042802382107200428023C2109200428025C21082004280250210A200541003A00142005200A3602102005200836020C2005200936020820052007360204200520063602002004200541186A360284010C050B20044180016A200441046A200441386A2004413C6A200441DC006A200F10170C040B200941013A00142007200428022C41186C6A200B3602102007200428025041186C6A200428025C36020C20042004280220220536020420042802880120064B044020042802382107200428023C2109200428022C21082004280250210A200641003A00142006200A3602102006200836020C2006200936020820062007360204200620053602002004200641186A360284010C040B20044180016A200441046A200441386A2004413C6A2014200F10170C030B200841013A00142007200428021841186C6A200B36020C2007200428024C41186C6A200428025C3602102004200428020C220536020420042802880120064B0440200428023C210720042802382109200428024C21082004280218210A200641003A00142006200A3602102006200836020C2006200936020820062005360204200620073602002004200641186A360284010C030B20044180016A2004413C6A200441046A200441386A2013201210170C020B200428026422062004280268470440200620053602002004200641046A3602642004417F36025C0C030B200441E0006A200441D8006A101F2004417F36025C0C020B200941013A0014200841013A00142007200428022C220541186C6A20042802183602102007200428021841186C6A200536020C2004417F36025C200420042802203602040B200428023821050240200028022422060440200620014101746A220620053B01002006200428023C3B0102200620042802043B01040C010B200028022020014102746A220620053602002006200428023C360204200620042802043602080B200141036A21010B20012002490D020C030B2000280234200028028401410C6C6A2207200536020820072005360204200720053602002000200028028401220541016A3602840120050B2107200141016A2109200420073602440240200028022422080440200820094101746A20073B01000C010B200028022020094102746A20073602000B024020064104710440200C200D101021050C010B2000280234200028028401410C6C6A2206200536020820062005360204200620053602002000200028028401220541016A360284010B200141026A2106200420053602480240200028022422070440200720064101746A20053B01000C010B200028022020064102746A20053602000B200420042802840122052004280280016B41186D22063602200240200428027422072004280278490440200720063602002004200741046A3602740C010B200441F0006A200441206A101F20042802840121050B2004200641026A22073602202004200641016A2209360208024020052004280288014904402004290244211720042802402108200541003A0014200520093602102005200736020C20052008360208200520173702002004200541186A2205360284010C010B20044180016A2010200E200441406B200441206A200441086A101720042802840121050B200420052004280280016B41186D220A36022002402004280274220820042802784904402008200A3602002004200841046A3602740C010B200441F0006A200441206A101F20042802840121050B200420063602202004200736020802402005200428028801490440200428024821082004280240210A2004280244210B200541003A0014200520073602102005200636020C2005200B3602082005200A360204200520083602002004200541186A2205360284010C010B20044180016A200E200441406B2010200441206A200441086A101720042802840121050B200420052004280280016B41186D22083602200240200428027422072004280278490440200720083602002004200741046A3602740C010B200441F0006A200441206A101F20042802840121050B200141036A21012004200936022020042006360208024020052004280288014904402004290240211720042802482107200541003A0014200520063602102005200936020C20052007360208200520173702002004200541186A360284010C010B20044180016A200441406B2010200E200441206A200441086A10170B20012002490D000B0B20042802602200044020042000360264200010020B20042802702200044020042000360274200010020B200428028001220004402004200036028401200010020B20044190016A24000F0B41AD11100C000B41AD11100C000BEB0101067F20002802082203200028020422026B410C6D20014F0440200020022001410C6C6A3602040F0B02402002200028020022026B2205410C6D220620016A220441D6AAD5AA01490440027F41002004200320026B410C6D2203410174220720072004491B41D5AAD5AA01200341AAD5AAD500491B2204450D001A200441D6AAD5AA014F0D022004410C6C10030B22072006410C6C6A2206200541746D410C6C6A2103200541014E044020032002200510041A0B20002003360200200020072004410C6C6A360208200020062001410C6C6A36020420020440200210020B0F0B1007000B41AD11100C000BC10401067F230041206B220324002003410036021820034200370310200041206A200041F8006A2206102B20002802142201200041186A2205470440034020032001220241106A10112003200228021C220136020C200120002802002006200128020028021C11000020032C000B417F4C0440200328020010020B024020022802042204450440200228020822012802002002460D01200241086A210203402002280200220441086A2102200420042802082201280200470D000B0C010B03402004220128020022040D000B0B20012005470D000B200028021421010B024020012005460D00034020032001220241106A10112003200228021C220136020C20012000280200200341106A200128020028022011000020032C000B417F4C0440200328020010020B024020022802042204450440200228020822012802002002460D01200241086A210203402002280200220441086A2102200420042802082201280200470D000B0C010B03402004220128020022040D000B0B20012005470D000B200028021422042005460D00034020032004220241106A10112003200228021C220136020C20012000280200200128020028022811010020032C000B417F4C0440200328020010020B024020022802042201450440200228020822042802002002460D01200241086A210203402002280200220141086A2102200120012802082204280200470D000B0C010B03402001220428020022010D000B0B20042005470D000B0B20032802102200044020032000360214200010020B200341206A24000B800801087F230041206B22042400200041206A2208200041F8006A2205102B200020002802800122012800003602702000200141046A360280012005200041CC006A1016200028028001220328000021012000200341046A2203360280012003200028027C6B410371220204402000200320026B41046A2203360280010B2000420037026820004100360260200020013602582000200336025C20002003360264200020002802800120014102746A3602800120002802142201200041186A22064704400340200441106A2001220241106A10112004200228021C220136021C200120002802002005200128020028021C11000020042C001B417F4C0440200428021010020B024020022802042203450440200228020822012802002002460D01200241086A210303402003280200220241086A2103200220022802082201280200470D000B0C010B03402003220128020022030D000B0B20012006470D000B0B0240200028020022012000280238200041346A220728020022026B410C6D22034B04402007200120036B10420C010B200120034F0D00200020022001410C6C6A3602380B410021012004410036020C200041406B28020022032000280244220247044003402000200141036C200328020041036C2004410C6A104120032802002101200341106A2205210320022005470D000B0B0240200041146A220528020022012006460D000340200441106A2001220241106A10112004200228021C220136021C200120002802002007200128020028022011000020042C001B417F4C0440200428021010020B024020022802042203450440200228020822012802002002460D01200241086A210303402003280200220241086A2103200220022802082201280200470D000B0C010B03402003220128020022030D000B0B20012006470D000B200528020022012006460D000340200441106A2001220241106A10112004200228021C220136021C20012000280200200028020420052008200128020028022411060020042C001B417F4C0440200428021010020B024020022802042203450440200228020822012802002002460D01200241086A210303402003280200220241086A2103200220022802082201280200470D000B0C010B03402003220128020022030D000B0B20012006470D000B200528020022012006460D000340200441106A2001220241106A10112004200228021C220136021C20012000280200200128020028022811010020042C001B417F4C0440200428021010020B024020022802042203450440200228020822012802002002460D01200241086A210303402003280200220241086A2103200220022802082201280200470D000B0C010B03402003220128020022030D000B0B20012006470D000B0B200441206A24000BFE0101037F230041306B220324002003418080802836021020034200370308200341003A000D200341FA10280000360208200341FE102D00003A000C200041146A2204200341086A1023210520032C0013417F4C0440200328020810020B2005200041186A470440200341808080283602102003420037030841002100200341FA10280000360208200341FE102D00003A000C200341003A000D2003200341086A360220200341286A2004200341086A200341206A1022200328022828021C22040440200441B40B41F00F100B21000B20032C0013417F4C0440200328020810020B2000200236024820002001360204200041043602140B200341306A24000BED0201057F230041106B2204240020002802142201200041186A2205470440034020042001220341106A10112004200128021C220136020C20010440200120012802002802041103000B20042C000B417F4C0440200428020010020B024020032802042202450440200328020822012802002003460D01200341086A210203402002280200220341086A2102200320032802082201280200470D000B0C010B03402002220128020022020D000B0B20012005470D000B0B200041D8006A100E200028024C2201044020002001360250200110020B200041406B28020022010440027F2001200120002802442202460D001A0340200241746A200241786A2802001018200241706A22022001470D000B20002802400B210220002001360244200210020B20002802342201044020002001360238200110020B2000280228220104402000200136022C200110020B200041146A20002802181024200041086A200028020C1018200441106A240020000B0900200041870810210B8F03010A7F0240200141046A220528020022040440200228020420022D000B2205200541187441187541004822051B21072002280200200220051B2108200141046A21050340200441106A21020240024002400240024002400240200428021420042D001B2206200641187441187541004822091B220A2007200A200749220C1B2206044020082002280200200220091B220B2006100F220D0D010B2007200A490D012006450D032002280200200220091B210B0C020B200D417F4A0D010B200428020022020D04200421050C070B200B20082006100F22020D010B200C0D010C050B2002417F4A0D040B200441046A210520042802042202450D03200521040B20042105200221040C00000B000B200521040B200020052802002202047F41000541201003220241106A2003280200101120022004360208200242003702002002410036021C200520023602002002210420012802002802002203044020012003360200200528020021040B2001280204200410262001200128020841016A36020841010B3A0004200020023602000B830901097F230041306B220224002000410C6A22034200370200200041186A220442003702002000200336020820002004360214200041206A410041D400100A1A200042003702800120004201370278024002400240200141037145044020002001360280012000200136027C200128000021032000200141046A3602800120034180C6E9C307470D012000200141096A36028001200020012D00083602782001280009210420002001410D6A2201360280012004450D03200041086A210803402000200141026A220620012F00006A2201360280012000200141026A220520012F00006A36028001200241003602102002420037030820061014220141704F0D03024002402001410B4F0440200141106A4170712209100321032002200941808080807872360210200220033602082002200136020C0C010B200220013A0013200241086A21032001450D010B20032006200110041A0B200120036A41003A00002002200241086A360220200241286A2008200241086A200241206A102C2002280228411C6A2005103D20022C0013417F4C0440200228020810020B2000280280012101200741016A22072004470D000B0C030B100841C4103602001009000B100841EA103602001009000B1013000B200128000021062000200141046A2201360280010240200641014E0440200041146A21094100210803402000200141026A220520012F00006A220136028001200241003602102002420037030820051014220341704F0D02024002402003410B4F0440200341106A4170712207100321042002200741808080807872360210200220043602082002200336020C0C010B200220033A0013200241086A21042003450D010B20042005200310041A0B200320046A41003A0000200128000021042000200141046A36028001200128000421052000200141096A3602800120012D0008210320002001410A6A3602800120012D0009210720002001410B6A3602800120012D000A210A02402004417E6A220141014D0440200141016B044041C8001003220141B40D36020020014201370214200142003702242001420037022C200142003702342001420037023C200141003602442001428080808030370204200141003602202001430000004438020C200141023602100C020B41CC0010032201420037020420014104360248200141900F36020020014284808080800137024020014284808080C0003702382001420037020C20014200370220200142013702142001420037022820014200370230200120033602080C010B4138100322014200370204200141FC113602002001420037020C20014201370214200142003702202001420037022820014200370230200120033602080B2001200536020C2001200A360210200120073602142002200241086A360220200241286A2009200241086A200241206A10482002280228200136021C20022C0013417F4C0440200228020810020B2000280280012101200841016A22082006470D000B0B200020012800003602002000200141046A36028001200020012800043602042000200141086A36028001200241306A240020000F0B1013000BB10602047F027D024020002802042204450D002000280214220341074B0D00200028020820016C210202400240024002400240024002400240200341016B0E0703060200040105070B2002450D072004027F20002A020C20042C0000B29422068B430000004F5D04402006A80C010B4180808080780B3A00004101210320024101460D072000220121040340027F20012A020C200428020420036A22052C0000B29422068B430000004F5D04402006A80C010B4180808080780B2100200520003A0000200341016A22032002470D000B0C070B2002450D06410021010340200420014102746A20002A020C200120046A2D0000B394380200200141016A22012002470D000B0C060B2002450D0520002A020C2107410021010340027F2007200420014101746A22032F0100B3942206430000804F5D20064300000000607104402006A90C010B41000B2100200320003B0100200141016A22012002470D000B0C050B2002450D0420002A020C2107410021010340027F2007200420014102746A2203280200B3942206430000804F5D20064300000000607104402006A90C010B41000B210020032000360200200141016A22012002470D000B0C040B2002450D032004027F20002A020C20042C0000B29422068B430000004F5D04402006A80C010B4180808080780B3A00004101210320024101460D032000220121040340027F20012A020C200428020420036A22052C0000B29422068B430000004F5D04402006A80C010B4180808080780B2100200520003A0000200341016A22032002470D000B0C030B2002450D0220002A020C2106410021010340200420014103746A2006200120046A2D0000B394BB390300200141016A22012002470D000B0C020B2002450D0120002A020C2107410021010340027F2007200420014101746A22032F0100B3942206430000804F5D20064300000000607104402006A90C010B41000B2100200320003B0100200141016A22012002470D000B0C010B2002450D0020002A020C2107410021010340027F2007200420014102746A2203280200B3942206430000804F5D20064300000000607104402006A90C010B41000B210020032000360200200141016A22012002470D000B0B0B840301067F230041306B220324002003420037032820034200370320200342003703182000280208220428000021052000200441046A2204360208200420002802046B410371220604402000200420066B41046A22043602080B2003420037022820034100360220200320053602182003200436021C200320043602242000200028020820054102746A36020820034100360210200342003703082000200341086A1016200328020C2206200328020822006B210402402001450D002004450D0041002105200241014E044003402001200220056C6A21070240200020056A22082D00002204044041012004744101762106410021000340200020076A200341186A200441FF0171101020066B3A00002002200041016A220047044020082D000021040C010B0B20032802082100200328020C21060C010B200741002002100A1A0B200541016A2205200620006B490D000C02000B000B0340200541016A22052004490D000B0B200004402003200036020C200010020B200341186A100E200341306A24000B2E01017F200028020821012000280204210320002D00104102710440200220032001104B0F0B200220032001102E0BC00301087F230041306B22082400200841186A2001101C2109200841086A200310252105024020034101480D00200104400340027F02402005280200200A410C6C6A220622072802042006280200220B6B220420014F0440200420014D0D0120072001200B6A36020441000C020B2006200120046B10050B41000B2104034002402002200320046C200A6A6A2D000022070440200628020020046A41C1002007AD42018879A76B220B3A000020092007200B10150C010B200628020020046A41003A00000B200441016A22042001470D000B200A41016A220A2003470D000B0C010B20052802002101034020012004410C6C6A2202220628020420022802002202470440200620023602040B200441016A22042003470D000B0B2000200910194100210420052802002101200341004A04400340200020012004410C6C6A2201280204200128020022016B2001101D20052802002101200441016A22042003470D000B0B20010440027F2001200120052802042200460D001A0340200041746A220228020022030440200041786A2003360200200310020B200222002001470D000B20052802000B210020052001360204200010020B2009100E200841306A24000BF90301077F230041306B22062400200641186A2001101C21092006410036021020064200370308024002402001450D002001417F4C0D0120062001100322043602082006200436020C2006200120046A360210200121050340200441003A00002006200628020C41016A220436020C2005417F6A22050D000B2001450D00200341024E0440034041222002200320076C6A220A2D00002205410176676B410020051B210441012105034041222005200A6A2D00002208410176676B410020081B2208200420042008481B2104200541016A22052003470D000B200628020820076A20043A000002402004450D0020034101480D0041012004417F6A742108410021050340200920082005200A6A2D00006A20041015200541016A22052003470D000B0B200741016A22072001470D000C02000B000B034002402002200320076C6A220A2D00002205450440200628020820076A41003A00000C010B200628020820076A412220054101766722046B22053A00002005450D0020034101480D004101412120046B742108410021040340200920082004200A6A2D00006A20051015200441016A22042003470D000B0B200741016A22072001470D000B0B2000200910192000200628020C200628020822006B2000101D2006280208220004402006200036020C200010020B2009100E200641306A24000F0B1007000B6901027F2002200228020820022802046B36021020002802082103200028022C2104024020002D001041027104402002200120042003104E0C010B2002200120042003104D0B200228021021012002200228020820022802046B22023602102000200220016B3602180B0900200041800810210B9A0603077F017D017C200041206A21080240200028020820016C22032000280224200028022022046B22014B04402008200320016B10050C010B200320014F0D002000200320046A3602240B024020032000280230200028022C22046B22014B04402000412C6A200320016B10050C010B200320014F0D002000200320046A3602300B0240024002400240024002402000280214417F6A220141064B0D000240200141016B0E06010301040500020B2003450D05410021010340200028022020016A027F200220014103746A2B030020002A020CBBA3220B44000000000000F04163200B44000000000000000066710440200BAB0C010B41000B3A0000200141016A22012003470D000B0C050B100841B0103602001009000B2003450D03410021010340200028022020016A027F200220014102746A280200B220002A020C95220A430000804F5D200A430000000060710440200AA90C010B41000B3A0000200141016A22012003470D000B0C030B2003450D02410021010340200028022020016A027F200220014101746A2E0100B220002A020C95220A430000804F5D200A430000000060710440200AA90C010B41000B3A0000200141016A22012003470D000B0C020B2003450D01410021010340200028022020016A027F200120026A2C0000B220002A020C95220A430000804F5D200A430000000060710440200AA90C010B41000B3A0000200141016A22012003470D000B0C010B2003450D00410021010340200028022020016A027F200220014102746A2A020020002A020C95220A430000804F5D200A430000000060710440200AA90C010B41000B3A0000200141016A22012003470D000B0B2000410036021C2000280208220441014E044003402008280200220920056A2D000021020240200520034F0440200221010C010B20022101200420056A220620034F0D000340200620096A2D00002207200120012007491B210120072002200220074A1B2102200420066A22062003490D000B0B2000200028021C220441C00020012002417F736AAC42018879A76B220141016A200420014A1B36021C200541016A220520002802082204480D000B0B0BC80301067F024020002802042205450D00200228020421042002280200210320002D00104101710440200420036B410C6D4102490D012000220641086A2802002100410121010340200041014E044020032001410C6C6A220421074100210303402005200020016C20036A6A220820082D00002005200428020420006C20036A6A2D00002005200428020020006C20036A6A2D00006A2005200728020820006C20036A6A2D00006B6A3A0000200341016A220320062802082200480D000B20022802042104200228020021030B200141016A2201200420036B410C6D490D000B0C010B20032004470440200420036B410C6D4102490D012000220641086A2802002100410121010340200041014E044020032001410C6C6A21044100210303402005200020016C20036A6A220720072D00002005200428020020006C20036A6A2D00006A3A0000200341016A220320062802082200480D000B20022802042104200228020021030B200141016A2201200420036B410C6D490D000B0C010B2000220241086A2802002200200020016C4F0D00200021030340200320056A220620062D00002005200320006B6A2D00006A3A0000200341016A22032002280208220020016C490D000B0B0B5201037F2000280208220441014E04402002280208210103402002200141016A2205360208200020034102746A20012D000036023820052101200341016A22032004480D000B0B200220002802042004102E0BE30301087F230041306B22092400200941186A2001101C210A200941086A200310252106024020034101480D00200104400340027F02402006280200200B410C6C6A22082205280204200828020022076B220420014F0440200420014D0D012005200120076A36020441000C020B2008200120046B10050B41000B2104034002402002200320046C200B6A6A2C000022050440200828020020046A41C10020052005411F7522076A200773AD42018879A76B22073A0000200A4100200541012007744101756A6B200520054100481B200710150C010B200828020020046A41003A00000B200441016A22042001470D000B200B41016A220B2003470D000B0C010B2006280200210241002101034020022001410C6C6A2204220528020420042802002204470440200520043602040B200141016A22012003470D000B0B2000200A10194100210120062802002104200341004A04400340200020042001410C6C6A2202280204200228020022026B2002101D20062802002104200141016A22012003470D000B0B20040440027F2004200420062802042200460D001A0340200041746A220128020022020440200041786A2002360200200210020B200122002004470D000B20062802000B210020062004360204200010020B200A100E200941306A24000BC10101057F200220022802082204200228020422036B3602100240200028020822054101480D00200241046A21070340200020064102746A28023821050240200420036B2204417F470440200741011005200728020021030C010B200220033602080B200320046A20053A0000200641016A2206200028020822054E0D0120022802082104200228020421030C00000B000B20022001200028022C20051054200228021021012002200228020820022802046B22023602102000200220016B3602180BD10301087F2000280208220341014E04400340200028022C20026A2000280220200128020028020020036C20026A6A2D00003A0000200241016A220220002802082203480D000B0B2001280204200128020022026B410475220441024F0440410121060340200220064104746A22052108024002402005280204220420052802082209460D0020002D0010410171450D0020034101480D01410021020340200028022C200320066C20026A6A20002802202207200528020020036C20026A6A2D00002007200320046C20026A6A2D00006B2007200320096C20026A6A2D00006B2007200528020C20036C20026A6A2D00006A3A0000200241016A2202200028020822034E0D0220052802082109200828020421040C00000B000B20034101480D00410021020340200028022C200320066C20026A6A20002802202207200528020020036C20026A6A2D00002007200320046C20026A6A2D00006B3A0000200241016A2202200028020822034E0D01200828020421040C00000B000B200641016A22062001280204200128020022026B4104752204490D000B0B200320046C22012000280230200028022C22036B22024B04402000412C6A200120026B10050F0B200120024904402000200120036A3602300B0B040041030B3801017F2000418410360200200028022C2201044020002001360230200110020B20002802202201044020002001360224200110020B20000BDC0401077F230041106B220324000240024020002802042206450D00024002402000280214417C6A220241024B0D000240200241016B0E020102000B2000280208210420002802482107200341FF013A0003200120046C22024101480D02200220066A21082006200120076C6A21050340200820046B210841002102200441004A04400340200220036A200220086A2D00003A0000200241016A22022004470D000B0B200520076B2105200320032D00002201410874200120032D00026A41FF01717220032D000120016A41FF01714110747220032D00034118747236020041002102200741004A04400340200220056A200220036A2D0000200020024102746A2D00386C3A0000200241016A220220002802482207480D000B200028020421060B200820064D0D03200028020821040C00000B000B100841E50E3602001009000B2003410036020820034200370300200145044041002006200141027410041A0C010B20014180808080044F0D01200320014102742205100322023602002003200220056A22043602082003200436020420022006200510041A410021050340200220054102746A220220022D00002204410874200420022D00026A41FF01717220022D000120046A41FF01714110747220022D000341187472360000410021022000280248220441004A044003402006200241027422076A220820082A0200200020076A280238B2944300007F4395380200200241016A22022004480D000B0B200620044102746A210620032802002102200541016A22052001470D000B2002450D0020032002360204200210020B200341106A24000F0B1007000BA80502077F017D230041106B220424000240200028020820016C22032000280224200041206A220528020022076B22064B04402005200320066B10050C010B200320064F0D002000200320076A3602240B0240200320002802302000412C6A220728020022086B22064B04402007200320066B10050C010B200320064F0D002000200320086A3602300B0240024002402000280214417C6A220341024B0D000240200341016B0E020102000B2001450D02200528020021062000280208210541002107034041002103200541004A044003402004410C6A20036A200220036A2D0000200020034102746A2802386D3A0000200341016A22032005480D000B0B200420042D000E20042D000D22036B41FF017141087420037220042D000C20036B41FF01714110747220042D000F4118747236020C41002103200541004A04400340200320066A2004410C6A20036A2D00003A0000200341016A220320002802082205480D000B0B200520066A2106200220056A2102200741016A22072001470D000B0C020B1008220041C50E3602001009000B200441FF013A000B2001450D00200028020821052000280220210741002108034041002103200541004A044003402000200341027422066A2802382109200441086A20036A027F200220066A2A02004300007F4394220A8B430000004F5D0440200AA80C010B4180808080780B20096D3A0000200341016A22032005480D000B0B200420042D000A20042D000922036B41FF017141087420037220042D000820036B41FF01714110747220042D000B4118747236020841002103200541004A04400340200320076A200441086A20036A2D00003A0000200341016A220320002802082205480D000B0B200520076A2107200220054102746A2102200841016A22082001470D000B0B2000410036021C200441106A24000B040041020B5201017F200041B40D360200200028023C22010440200041406B2001360200200110020B20002802302201044020002001360234200110020B20002802242201044020002001360228200110020B200010020B5001017F200041B40D360200200028023C22010440200041406B2001360200200110020B20002802302201044020002001360234200110020B20002802242201044020002001360228200110020B20000B950502077F047D02402000280204450D0020002802200D00024002402000280214417D6A220241034B0D000240200241016B0E03010102000B2001450D020340200028023C2202200541037422064104726A280200411074220341107522042003411F7522036A2003732103200220066A280200411074220241107522062002411F7522026A2002732107027F20002A020C22098B430000004F5D04402009A80C010B4180808080780B220220076B220720036B2208B2210A027D2008417F4A04402006B2210B2004B20C010B200220036B2202410020026B200641004A1BB2210B2007410020076B200441004A1BB20B21092000280204200541066C6A2204027F200A200A200A942009200994200B200B94929291220A954300FEFF4694220C8B430000004F5D0440200CA80C010B4180808080780B3B01042004027F2009200A954300FEFF469422098B430000004F5D04402009A80C010B4180808080780B3B01022004027F200B200A954300FEFF469422098B430000004F5D04402009A80C010B4180808080780B3B0100200541016A22052001470D000B0C020B1008220041E30C3602001009000B2001450D000340200028023C2202200541037422034104726A28020022042004411F7522066A2006732106200220036A28020022022002411F7522036A2003732107027F20002A020C22098B430000004F5D04402009A80C010B4180808080780B220320076B220720066B2208B221092008417F4C0440410020076B200720044101481B21044100200320066B22036B200320024101481B21020B20002802042005410C6C6A2203200920092009942004B222092009942002B2220B200B94929291220A9538020820032009200A953802042003200B200A95380200200541016A22052001470D000B0B0BBB04020B7F047D2002280204200228020022036B2204410C6D210B02402004450D00200028023C210C034020012008410C6C22056A2104200320056A21030240024020002802204101470440200028022420084102746A280200450D010B20032A020022108B20032A020422118B9220032A0208220E8B92210F200E43000000005D4101732103027F20002A020C220E8B430000004F5D0440200EA80C010B4180808080780B21052011200F95210E2010200F95210F024020030440200F21100C010B430000803F200E8B93220E8C200E201043000000005D1B2110430000803F200F8B93210E201143000000005D4101730D00200E8C210E0B027F200E2005B2220F94220E8B430000004F5D0440200EA80C010B4180808080780B200C20094103746A22062802046A22032003411F7522076A200773210A2005027F2010200F94220F8B430000004F5D0440200FA80C010B4180808080780B20062802006A22072007411F7522066A2006736B2206200A6B220DB2210F200D417F4C044041002005200A6B22056B200520074101481B2107410020066B200620034101481B21030B200941016A210920042007B22210200F200F942003B2220E200E9420102010949292912210953802002004200F2010953802082004200E2010953802040C010B200420032A0200220F200F200F9420032A0204220F200F949220032A020822102010949291220E9538020020042010200E953802082004200F200E953802040B200841016A2208200B4F0D01200228020021030C00000B000B0B08002000200110210BBD06020A7F047D2002280204200228020022046B2203410C6D210A02402003450D00200028023C210B034020042006410C6C6A21030240024020002802204101470440200028022420064102746A280200450D010B20032A0200220F8B20032A020422108B9220032A0208220D8B92210E200D43000000005D4101732103027F20002A020C220D8B430000004F5D0440200DA80C010B4180808080780B21042010200E95210D200F200E95210E024020030440200E210F0C010B430000803F200D8B93220D8C200D200F43000000005D1B210F430000803F200E8B93210D201043000000005D4101730D00200D8C210D0B027F200D2004B2220E94220D8B430000004F5D0440200DA80C010B4180808080780B200B20084103746A22052802046A411074220741107522032007411F7522076A20077321072004027F200F200E94220F8B430000004F5D0440200FA80C010B4180808080780B20052802006A411074220541107522092005411F7522056A2005736B220520076B220CB2210D027D200C417F4A04402003B2210E2009B20C010B2005410020056B200341004A1BB2210E200420076B2204410020046B200941004A1BB20B210F2001200641066C6A2204027F200D200D200D94200E200E94200F200F94929291220D954300FEFF469422108B430000004F5D04402010A80C010B4180808080780B3B0104200841016A21082004027F200E200D954300FEFF4694220E8B430000004F5D0440200EA80C010B4180808080780B3B0102200F200D954300FEFF4694220F8B430000004F5D04402004200FA83B01000C020B20044180808080783B01000C010B20032A0200220F200F9420032A0204220E200E949220032A0208220D200D949291221043ACC527375D4101734504402003410036020020034100360204200341808080FC033602080C010B2001200641066C6A2204027F4300FEFF462010952210200D94220D8B430000004F5D0440200DA80C010B4180808080780B3B01042004027F2010200E94220E8B430000004F5D0440200EA80C010B4180808080780B3B01022004027F2010200F94220F8B430000004F5D0440200FA80C010B4180808080780B3B01000B200641016A2206200A4F0D01200228020021040C00000B000B0B880302097F067D230041106B220524002004200428020036020420054100360208200542003703002000044020042000200510340B200241036C220041014E0440200320004101746A210A200428020021060340200120032F0104410C6C220B6A2207280200210C200120032F0102410C6C220D6A22082802002104200120032F0100410C6C22026A22092802002100200220066A220220022A02002008280204B22009280204B222109322122007280208B22009280208B2220E93220F942008280208B2200E93220E2007280204B2201093221394932211923802002002200E200CB22000B2220E932210942004B2200E93220E200F9493220F20022A0204923802042002200E201394201220109493220E20022A0208923802082006200D6A2200201120002A0200923802002000200F20002A0204923802042000200E20002A0208923802082006200B6A2200201120002A0200923802002000200F20002A0204923802042000200E20002A020892380208200341066A2203200A490D000B0B200541106A24000BCD0701047F230041306B22052400024002400240024002402000280204450D002000280220450D0020054100360210200541003A0010200542F0DECDCBC6AEDAB7EE00370308200541083A00132003200541086A1023210620052C0013417F4C0440200528020810020B2006200341046A460D0120054100360210200541003A0010200542F0DECDCBC6AEDAB7EE00370308200541083A00132005200541086A360220200541286A2003200541086A200541206A1022200528022828021C22030440200341B40B41D40B100B21070B20052C0013417F4C0440200528020810020B2007450D02200541003602102005420037030820010440200141D6AAD5AA014F0D0420052001410C6C2206100322033602082005200336020C2005200320066A360210200341002006100A1A2001210603402003410C6A21032006417F6A22060D000B2005200336020C0B2007280204210302402004280200220604402001200320022006200541086A10350C010B2001200320022004280204200541086A10620B024020002802204102470D002004280200220304402000200028022436022820054100360228200041246A21042001044020042001200541286A101B0B200241036C22014101480D01200320014102746A2102200428020021010340200120032802004102746A22042004280200200328020473360200200120032802004102746A22042004280200200328020873360200200120032802044102746A22042004280200200328020873360200200120032802044102746A22042004280200200328020073360200200120032802084102746A22042004280200200328020073360200200120032802084102746A220420042802002003280204733602002003410C6A22032002490D000B0C010B200428020421032000200028022436022820054100360228200041246A21042001044020042001200541286A101B0B200241036C22014101480D00200320014101746A2107200428020021010340200120032F010022024102746A220820032F0104220420032F0102220620082802007373360200200120064102746A22082008280200200220047373360200200120044102746A22042004280200200220067373360200200341066A22032007490D000B0B0240024002402000280214417D6A220141034B0D000240200141016B0E03010102000B20002000280204200541086A10610C020B100841A50C3602000C060B20002000280204200541086A105F0B20052802082200450D002005200036020C200010020B200541306A24000F0B100841DD0A3602000C020B100841E00B3602000C010B1007000B1009000BE20101037F02402000280204450D0020002802200D002002280204200228020022056B2202410C6D21032002044020034102490D01200028023C21004101210203402000200241037422016A22042004280200200020052002410C6C6A22042802004103746A2802006A360200200020014104726A22012001280200200020042802004103744104726A2802006A360200200241016A22022003470D000B0C010B200141017422024103490D00200028023C2103410221000340200320004102746A22012001280200200141786A2802006A360200200041016A22002002470D000B0B0BC80101037F20022002280208220341016A360208200020032D00003602202000413C6A2103024020014101742204200041406B280200200028023C22016B41027522054B04402003200420056B100D200328020021010C010B200420054F0D00200041406B200120044102746A3602000B20022001410210312101024020002802204102470D0020014101742201200041406B280200200028023C22046B41027522024B04402003200120026B100D0F0B200120024F0D00200041406B200420014102746A3602000B0B970101027F2000280220210302402002280208200228020422016B2204417F470440200241046A41011005200228020421010C010B200220013602080B200120046A20033A00002002200228020820022802046B3602102002200041406B280200200028023C22016B410275410176200141021032200228021021012002200228020820022802046B22023602102000200220016B3602180BFB0301087F0240024002402000280220220304402001280204220420012802002205460D01200420056B4104752106410021010340200520014104746A22072802002104024020034102460440200028022420044102746A280200450D010B200028023C2203200241037422086A2000280230220920044103746A280200360200200320084104726A200920072802004103744104726A280200360200200241016A21020B200141016A220120064F0D02200028022021030C00000B000B200028023C220320002802302205200128020022042802004103746A2802003602002003200520042802004103744104726A28020036020441012102200128020420046B2206410475220741014B044003402003200241037422086A2005200420024104746A22012802004103746A280200200520012802044103746A2802006B360200200320084104726A200520012802004103744104726A280200200520012802044103744104726A2802006B360200200241016A22022007490D000B0B20064103752201200041406B28020020036B41027522024B04400C030B200120024F0D01200041406B200320014102746A3602000F0B20024101742201200041406B280200200028023C22036B41027522024B04400C020B200120024F0D00200041406B200320014102746A3602000B0F0B2000413C6A200120026B100D0BE00602027F067D230041306B2205240002402000280220450D0020054100360210200541003A0010200542F0DECDCBC6AEDAB7EE00370308200541083A00132003200541086A1023210620052C0013417F4C0440200528020810020B0240024002402006200341046A4704404100210620054100360210200541003A0010200542F0DECDCBC6AEDAB7EE00370308200541083A00132005200541086A360220200541286A2003200541086A200541206A1022200528022828021C22030440200341B40B41D40B100B21060B20052C0013417F4C0440200528020810020B2006450D012004280208210320054100360210200542003703082001200628022020022003200541086A1035024020002802204102470D002000200028022436022820054100360228200041246A21042001044020042001200541286A101B0B200241036C22024101480D00200320024102746A2106200428020021020340200220032802004102746A22042004280200200328020473360200200220032802004102746A22042004280200200328020873360200200220032802044102746A22042004280200200328020873360200200220032802044102746A22042004280200200328020073360200200220032802084102746A22042004280200200328020073360200200220032802084102746A220420042802002003280204733602002003410C6A22032006490D000B0B200528020821022001450D0220002802302104027F20002A020C22078B430000004F5D04402007A80C010B4180808080780BB2210A41002103034020022003410C6C6A22002A0204220B20002A020022098B200B8B9220002A0208220C8B922207952108200920079521070240200C43000000005D4101730440200721090C010B430000803F20088B9322088C2008200943000000005D1B2109430000803F20078B932108200B43000000005D4101730D0020088C21080B200420034103746A22002000280200027F2009200A9422078B430000004F5D04402007A80C010B4180808080780B6B36020020002000280204027F2008200A9422078B430000004F5D04402007A80C010B4180808080780B6B360204200341016A22032001470D000B0C030B100841DD0A3602001009000B100841E00B3602001009000B2002450D010B2005200236020C200210020B200541306A24000BCA0C04097F017E047D027C200041306A210B0240200141017422032000280234200028023022056B410275220A4B0440200B2003200A6B100D0C010B2003200A4F0D002000200520034102746A3602340B02402003200041406B280200200028023C22056B410275220A4B04402000413C6A2003200A6B100D0C010B2003200A4F0D00200041406B200520034102746A3602000B0240024002400240024002402000280214417F6A220341054B0D002000280230210A024002400240200341016B0E050301030204000B2001450D05034020022007410C6C6A220328020422052005411F7522066A200673200328020022062006411F7522046A2004736A200328020822092009411F7522036A2003736A2104027F20002A020C220D8B430000004F5D0440200DA80C010B4180808080780B2108200A20074103746A027F20044504404100210341000C010B200520086C20046D2103200620086C20046D22042009417F4A0D001A200541004821094100027F2008B722112004B799A122129944000000000000E0416304402012AA0C010B4180808080780B22046B210820064100482106027F20112003B799A122119944000000000000E0416304402011AA0C010B4180808080780B21052008200420091B2103410020056B200520061B0BAD2003AD42208684370200200741016A22072001470D000B0C040B2001450D0403402002200741066C6A22032E010222052005411F7522066A20067320032E010022062006411F7522046A2004736A20032E010422092009411F7522036A2003736A2104027F20002A020C220D8B430000004F5D0440200DA80C010B4180808080780B2108200A20074103746A027F20044504404100210341000C010B200520086C20046D2103200620086C20046D22042009417F4A0D001A200541004821094100027F2008B722112004B799A122129944000000000000E0416304402012AA0C010B4180808080780B22046B210820064100482106027F20112003B799A122119944000000000000E0416304402011AA0C010B4180808080780B21052008200420091B2103410020056B200520061B0BAD2003AD42208684370200200741016A22072001470D000B0C030B2001450D0303402002200741036C6A22032C000122052005411F7522066A20067320032C000022062006411F7522046A2004736A20032C000222092009411F7522036A2003736A2104027F20002A020C220D8B430000004F5D0440200DA80C010B4180808080780B2108200A20074103746A027F20044504404100210341000C010B200520086C20046D2103200620086C20046D22042009417F4A0D001A200541004821094100027F2008B722112004B799A122129944000000000000E0416304402012AA0C010B4180808080780B22046B210820064100482106027F20112003B799A122119944000000000000E0416304402011AA0C010B4180808080780B21052008200420091B2103410020056B200520061B0BAD2003AD42208684370200200741016A22072001470D000B0C020B100841B40A3602001009000B2001450D01034020022007410C6C6A22032A0200220F8B20032A020422108B9220032A0208220E8B92210D200E43000000005D4101732103027F20002A020C220E8B430000004F5D0440200EA80C010B4180808080780B21052010200D95210E200F200D95210D024020030440200D210F0C010B430000803F200E8B93220E8C200E200F43000000005D1B210F430000803F200D8B93210E201043000000005D4101730D00200E8C210E0B027F200E2005B2220D94220E8B430000004F5D0440200EA80C010B4180808080780BAD422086210C200A20074103746A200C027F200F200D94220D8B430000004F5D0440200DA80C010B4180808080780BAD84370200200741016A22072001470D000B0B41012105200B2802002202280204210720022802002103200141014B0D012007210B200321020C020B200B2802002201280204220B21072001280200220221030C010B200321022007210B0340200A20054103746A220428020422062007200620074A1B2107200428020022042003200420034A1B21032006200B2006200B481B210B2004200220042002481B2102200541016A22052001470D000B0B200041C0002007200B417F736AAC42018879A76B220041C00020032002417F736AAC42018879A76B220120012000481B41016A36021C0B9E0101027F2000280210200028020C22056B4102470440200320046A2104200120026A417F6A220220014B0440034020012D0000410274220520002802246A280200220620032000280230200028021820056A2802006A200610046A2103200141016A22012002470D000B200221010B20032000280230200028021820012D00004102746A2802006A200420036B10041A0F0B200320052D00002004100A1A0BF902010D7F2000280210200028020C6B220641024604402003410036020041000F0B2002410174417F2002417F4A1B1003210920034100360200024020024101480D002006410175210C200041406B280200210F410021060340410021080240200028023C22072002200A6B220D200D20074A1B220B4101480440410021040C010B2001200A6A211041002104034020072008460D01200028024C200820106A2D00006A2D00002004200C6C6A2104200841016A2208200B470D000B0B2007200D4A044003402004200C6C2104200B41016A220B2007480D000B0B027F200F200420056B4102746A280200220541004E04402003200641016A2204360200200620096A20053A0000200028022420054102746A280200200E6B2107200421064100210541000C010B2007200E6A0B210E2007200A6A220A2002480D000B2005417F4A0D00200041406B28020021000340200020054102746B28020022054100480D000B2003200641016A360200200620096A20053A00000B20090B070020002802000B850201047F0240024020002802082204200028020422036B20014F04400340200320022D00003A00002000200028020441016A22033602042001417F6A22010D000C02000B000B2003200028020022056B220620016A2203417F4C0D01027F41002003200420056B2204410174220520052003491B41FFFFFFFF07200441FFFFFFFF03491B2203450D001A200310030B220420036A2105200420066A220421030340200320022D00003A0000200341016A21032001417F6A22010D000B20042000280204200028020022016B22026B2104200241014E044020042001200210041A0B2000200436020020002005360208200020033602042001450D00200110020B0F0B1007000BC805010D7F230041106B2206240002402000280210200028020C22026B22034104480D004101210720034101752104200028023C220541004A04400340200420076C2107200141016A22012005480D000B0B200641003A000F02402000280250200028024C22056B220141FF014D0440200041CC006A41800220016B2006410F6A106D200028020C21020C010B2001418002460D00200020054180026A3602500B200341014E0440410021010340200028024C200220014101746A2D00006A20013A0000200028020C2102200141016A22012004480D000B0B200028020020022D0001480D0020002000280240360244200641FFFFFF07360208200041406B21052007044020052007200641086A101B0B2000280218220B200028021C460D000340410021094100210C03402000280210200028020C6B410175210D200028023C210A4100210402402008410274220320002802246A28020020096B22024101480440410021010C010B20002802302003200B6A28020020096A6A21034100210103402004200A4E0D01200028024C200320046A2D00006A2D00002001200D6C6A2101200441016A22042002470D000B0B200141016A210420022103200A20024A044003402004200D6C21042001200D6C2101200341016A2203200A470D000B0B2002200A4C04402001200448044020052802002102034020022001200C6A4102746A2008360200200141016A22012004470D000B0B200841016A2208200028021C200B6B410275490D02052006200528020022022001200C6A41027422046A22032802002201360204024020014100480D0020034100200028024420026B41027522036B3602002003200320076A220149044020052007200641046A101B2000280218210B200028024021020C010B200320014D0D002000200220014102746A3602440B200028023C20096A21094100200220046A2802006B210C0C010B0B0B0B200641106A24000BBA0101057F02402000280204200028020022046B2205417D4A0440027F41002005410175220641016A2203200028020820046B220220022003491B41FFFFFFFF07200241017541FFFFFFFF03491B2203450D001A2003417F4C0D02200341017410030B2102200220064101746A220620012F00003B0000200541014E044020022004200510041A0B200020023602002000200220034101746A3602082000200641026A36020420040440200410020B0F0B1007000B41F009100C000BEB0101047F230041106B220524002000200028020C36021041800810034100418008100A2106200241004A044003402006200120036A2D00004102746A2204200428020041016A360200200341016A22032002470D000B0B2000410C6A21014100210303400240200620034102746A28020022044101480D00200520033A000E2005200441FF016C20026D3A000F200028021022042000280214490440200420052F010E3B00002000200028021041026A3602100C010B20012005410E6A106F0B200341FF01492104200341016A210320040D000B200028020C2000280210102720061002200541106A24000BB10101067F2000280214220141204704402000280210200174210602402000280200220120002802082202480440200028020421040C010B417F20024103742002410174220341FEFFFFFF03712003471B1003220420002802042205200241027410042102200504402005100220002802084101742103200028020021010B20002003360208200020023602040B2000200141016A360200200420014102746A20063602002000428080808080043702100B0B4801027F2000280244200041406B28020022006B220341004A0440200341047521030340200120024102746A200020024104746A280200360200200241016A22022003480D000B0B0BD10101057F20002802082202200028020422036B41017520014F04402000200320014101746A3602040F0B02402003200028020022036B2205410175220620016A2204417F4A0440027F41002004200220036B220220022004491B41FFFFFFFF07200241017541FFFFFFFF03491B2202450D001A2002417F4C0D02200241017410030B2104200541014E044020042003200510041A0B200020043602002000200420024101746A3602082000200420064101746A20014101746A36020420030440200310020B0F0B1007000B41A908100C000BAD0301057F230041E0006B220224002002420037021C200242003702242002420037022C200242003702342002420037023C200242003703502002420037035820024200370214200242FF8180808001370308200242003703482002410236024420002000280208220341016A22043602082000200420032D0000220341017422056A3602082003047F200241146A2003107320022802140541000B2004200510041A200241086A10372000280208220328000021042000200341046A2203360208024020042001280204200128020022066B22054B04402001200420056B1005200028020821030C010B200420054F0D002001200420066A3602040B2000200341046A2200200328000022036A36020820040440200241086A2000200320012802002004106A0B20022802542200044020022000360258200010020B2002280248220004402002200036024C200010020B2002280238220004402002200036023C200010020B200228022C2200044020022000360230200010020B20022802202200044020022000360224200010020B20022802142200044020022000360218200010020B200241E0006A24000BA40501077F230041E0006B220324002003420037021C200342003702242003420037022C200342003702342003420037023C200342003703502003420037035820034200370214200342FF81808080013703082003420037034820034102360244200341086A200120021070200341086A1037200341086A106E200341086A20012002200341046A106B2108200041046A2106200328021820032802146B410176210402402000280208200028020422016B2205417F470440200641011005200628020021010C010B200020013602080B200120056A20043A000002402000280208200028020422016B220420042003280218200328021422096B22056A2207490440200620051005200628020021010C010B200420074D0D002000200120076A3602080B200120046A2009200510041A02402000280208200028020422016B2204417B4D044020064104100520002802082105200028020421010C010B2000200120046A41046A22053602080B200120046A2002360200200328020421070240200520016B2202417B4D044020064104100520002802082104200028020421010C010B2000200120026A41046A22043602080B200120026A20073602000240200420016B22022002200328020422046A2205490440200620041005200628020021010C010B200220054D0D002000200120056A3602080B200120026A2008200410041A20080440200810020B20032802141A20032802181A20032802041A20032802542200044020032000360258200010020B2003280248220004402003200036024C200010020B2003280238220004402003200036023C200010020B200328022C2200044020032000360230200010020B20032802202200044020032000360224200010020B20032802142200044020032000360218200010020B200341E0006A24000B13002000280244200041406B2802006B4104750B0D00200004402000104610020B0B1700024020002802040440200010440C010B200010430B0B0900200020013602200B230020003F004110746B41FFFF036A4110764000417F46044041000F0B4100100041010B0900200020013602240B3B01017F2002044003402000200120024180202002418020491B22031004210020014180206A210120004180206A2100200220036B22020D000B0B0BE40201027F024020002001460D000240200120026A20004B0440200020026A220420014B0D010B20002001200210041A0F0B20002001734103712103024002402000200149044020030D022000410371450D0103402002450D04200020012D00003A0000200141016A21012002417F6A2102200041016A22004103710D000B0C010B024020030D002004410371044003402002450D0520002002417F6A22026A2203200120026A2D00003A000020034103710D000B0B200241034D0D00034020002002417C6A22026A200120026A280200360200200241034B0D000B0B2002450D02034020002002417F6A22026A200120026A2D00003A000020020D000B0C020B200241034D0D0020022103034020002001280200360200200141046A2101200041046A21002003417C6A220341034B0D000B200241037121020B2002450D000340200020012D00003A0000200041016A2100200141016A21012002417F6A22020D000B0B0B1A00200020012802082005100604402001200220032004103A0B0B3700200020012802082005100604402001200220032004103A0F0B200028020822002001200220032004200520002802002802141109000B0D002000418D082001410610200BA7010020002001280208200410060440024020012802042002470D00200128021C4101460D002001200336021C0B0F0B02402000200128020020041006450D0002402002200128021047044020012802142002470D010B20034101470D01200141013602200F0B20012002360214200120033602202001200128022841016A360228024020012802244101470D0020012802184102470D00200141013A00360B2001410436022C0B0B88020020002001280208200410060440024020012802042002470D00200128021C4101460D002001200336021C0B0F0B02402000200128020020041006044002402002200128021047044020012802142002470D010B20034101470D02200141013602200F0B200120033602200240200128022C4104460D00200141003B01342000280208220020012002200241012004200028020028021411090020012D003504402001410336022C20012D0034450D010C030B2001410436022C0B200120023602142001200128022841016A36022820012802244101470D0120012802184102470D01200141013A00360F0B20002802082200200120022003200420002802002802181106000B0BA10101027F02400340200145044041000F0B200141DC1441EC15100B2202450D012002280208200041086A280200417F73710D0120002201410C6A280200200228020C41001006044041010F0B20002D0008410171450D01200128020C2200450D01200041DC1441EC15100B22000440200228020C21010C010B0B200128020C2200450D00200041DC1441DC16100B2200450D002000200228020C103B21030B20030BE80301047F230041406A22052400024002400240200141C817410010060440200241003602000C010B2000200110850104404101210320022802002200450D03200220002802003602000C030B2001450D01200141DC1441EC15100B2201450D02200228020022040440200220042802003602000B2001280208220420002802082206417F73714107710D022004417F7320067141E000710D0241012103200028020C200128020C410010060D02200028020C41BC17410010060440200128020C2200450D03200041DC1441A016100B4521030C030B200028020C2204450D0141002103200441DC1441EC15100B2204044020002D0008410171450D032004200128020C10830121030C030B200028020C2204450D02200441DC1441DC16100B2204044020002D0008410171450D032004200128020C103B21030C030B200028020C2200450D02200041DC14418C15100B2204450D02200128020C2200450D02200041DC14418C15100B2200450D022005417F360214200520043602102005410036020C20052000360208200541186A41004127100A1A200541013602382000200541086A20022802004101200028020028021C11040020052802204101470D022002280200450D00200220052802183602000B410121030C010B410021030B200541406B240020030B400002402000200120002D0008411871047F410105410021002001450D01200141DC1441BC15100B2201450D0120012D00084118714100470B100621000B20000B310020002001280208410010060440200120022003103C0F0B20002802082200200120022003200028020028021C1104000B180020002001280208410010060440200120022003103C0B0B0A0020002001200210450BA30101017F230041406A22032400027F410120002001410010060D001A41002001450D001A4100200141DC14418C15100B2201450D001A2003417F360214200320003602102003410036020C20032001360208200341186A41004127100A1A200341013602382001200341086A20022802004101200128020028021C110400410020032802204101470D001A2002200328021836020041010B2100200341406B240020000B0A0020002001410010060B4D01027F20012D00002102024020002D00002203450D0020022003470D00034020012D0001210220002D00012203450D01200141016A2101200041016A210020022003460D000B0B200320026B0B0B00200010281A200010020B08002000102810020B2B01017F0240200028020041746A220022012001280208417F6A22013602082001417F4A0D00200010020B0B05004180130B0D0020004180082001410310200BAD0201057F230041106B220724002001417F73416F6A20024F0440027F20002C000B410048044020002802000C010B20000B2109027F41E7FFFFFF0720014B0440200720014101743602082007200120026A36020C027F230041106B220224002007410C6A2208280200200741086A220A28020049210B200241106A2400200A2008200B1B2802002202410B4F0B047F200241106A41707122022002417F6A22022002410B461B05410A0B0C010B416E0B41016A2208103E21022005044020022006200510290B200320046B220322060440200220056A200420096A200610290B2001410A470440200910020B2000200236020020002008418080808078723602082000200320056A2200360204200741003A0007200020026A20072D00073A0000200741106A24000F0B1013000BC60101037F230041106B22042400024020002C000B410048047F200028020841FFFFFFFF0771417F6A05410A0B220320024F0440027F20002C000B410048044020002802000C010B20000B2203210520020440200520012002107D0B200441003A000F200220036A20042D000F3A0000024020002C000B4100480440200020023602040C010B200020023A000B0B0C010B20002003200220036B027F20002C000B410048044020002802040C010B20002D000B0B22002000200220011091010B200441106A24000B990101037F230041106B22042400416F20024F044002402002410A4D0440200020023A000B200021030C010B20002002410B4F047F200241106A41707122032003417F6A22032003410B461B05410A0B41016A2205103E22033602002000200541808080807872360208200020023602040B2003200120021029200441003A000F200220036A20042D000F3A0000200441106A24000F0B1013000B0D0020004180082001410610200B3701027F200110142202410D6A100322034100360208200320023602042003200236020020002003410C6A2001200241016A10043602000BB30602047F027D024020002802042204450D002000280214220241074B0D00200028020820016C210302400240024002400240024002400240200241016B0E0703060200040105070B2003450D072004027F20002A020C20042C0000B29422068B430000004F5D04402006A80C010B4180808080780B3A00004101210220034101460D072000220121040340027F20012A020C200428020420026A22052C0000B29422068B430000004F5D04402006A80C010B4180808080780B2100200520003A0000200241016A22022003470D000B0C070B2003450D06410021010340200420014102746A220220002A020C2002280200B294380200200141016A22012003470D000B0C060B2003450D0520002A020C2107410021010340027F2007200420014101746A22022F0100B3942206430000804F5D20064300000000607104402006A90C010B41000B2100200220003B0100200141016A22012003470D000B0C050B2003450D0420002A020C2107410021010340027F2007200420014102746A2202280200B3942206430000804F5D20064300000000607104402006A90C010B41000B210020022000360200200141016A22012003470D000B0C040B2003450D032004027F20002A020C20042C0000B29422068B430000004F5D04402006A80C010B4180808080780B3A00004101210220034101460D032000220121040340027F20012A020C200428020420026A22052C0000B29422068B430000004F5D04402006A80C010B4180808080780B2100200520003A0000200241016A22022003470D000B0C030B2003450D0220002A020C2106410021010340200420014103746A2006200420014102746A280200B294BB390300200141016A22012003470D000B0C020B2003450D0120002A020C2107410021010340027F2007200420014101746A22022F0100B3942206430000804F5D20064300000000607104402006A90C010B41000B2100200220003B0100200141016A22012003470D000B0C010B2003450D0020002A020C2107410021010340027F2007200420014102746A2202280200B3942206430000804F5D20064300000000607104402006A90C010B41000B210020022000360200200141016A22012003470D000B0B0BAF0301077F024020002802042203450D002002280204200228020022086B2202410C6D210420002D0010410171044020044102490D012000220541086A2802002102410121010340200241014E044020082001410C6C6A220621074100210003402003200120026C20006A4102746A220920092802002003200628020420026C20006A4102746A2802002003200628020020026C20006A4102746A2802006A2003200728020820026C20006A4102746A2802006B6A360200200041016A220020052802082202480D000B0B200141016A22012004490D000B0C010B2002044020044102490D012000220541086A2802002102410121010340200241014E044020082001410C6C6A21064100210003402003200120026C20006A4102746A220720072802002003200628020020026C20006A4102746A2802006A360200200041016A220020052802082202480D000B0B200141016A22012004470D000B0C010B2000220541086A2802002202200120026C4F0D00200221000340200320004102746A220420042802002003200020026B4102746A2802006A360200200041016A22002005280208220220016C490D000B0B0BA30301077F230041306B220324002003420037032820034200370320200342003703182000280208220628000021042000200641046A2205360208200520002802046B410371220604402000200520066B41046A22053602080B2003420037022820034100360220200320043602182003200536021C200320053602242000200028020820044102746A3602082003410036021020034200370308024020024101480D000240200145044003402000200341086A1016200741016A22072002470D000B20032802082104200328020C1A0C010B03402000200341086A101641002105200328020C2208210420032802082206200847044003400240200520066A22092D000022044504402001200220056C20076A4102746A41003602000C010B2001200220056C20076A4102746A4100200341186A200410102204410120092D0000417F6A7422066A6B200420042006481B36020020032802082106200328020C21080B200541016A22052008200622046B490D000B0B200741016A22072002470D000B0B2004450D002003200436020C200410020B200341186A100E200341306A24000B0D0020004190082001410610200B3001017F200028020821012000280204210320002D0010410271044020022003200110311A0F0B2002200320011098010BE60301087F230041306B22092400200941186A2001101C210A200941086A200310252106024020034101480D00200104400340027F02402006280200200B410C6C6A22082205280204200828020022076B220420014F0440200420014D0D012005200120076A36020441000C020B2008200120046B10050B41000B2104034002402002200320046C200B6A4102746A28020022050440200828020020046A41C10020052005411F7522076A200773AD42018879A76B22073A0000200A4100200541012007744101756A6B200520054100481B200710150C010B200828020020046A41003A00000B200441016A22042001470D000B200B41016A220B2003470D000B0C010B2006280200210241002101034020022001410C6C6A2204220528020420042802002204470440200520043602040B200141016A22012003470D000B0B2000200A10194100210120062802002104200341004A04400340200020042001410C6C6A2202280204200228020022026B2002101D20062802002104200141016A22012003470D000B0B20040440027F2004200420062802042200460D001A0340200041746A220128020022020440200041786A2002360200200210020B200122002004470D000B20062802000B210020062004360204200010020B200A100E200941306A24000B6A01027F2002200228020820022802046B36021020002802082103200028022C2104024020002D00104102710440200220012004200310320C010B2002200120042003109B010B200228021021012002200228020820022802046B22023602102000200220016B3602180B8D04010A7F02402000280208220341004C0440200128020021070C010B200028022C210420002802202106200128020021070340200420024102746A2006200728020020036C20026A4102746A280200360200200241016A220220002802082203480D000B0B200128020420076B2201410475220941024F044020014104752109410121010340200720014104746A2204210A024002402004280204220620042802082208460D0020002D0010410171450D0020034101480D01200028022C210B20002802202105410021020340200B200120036C20026A4102746A2005200428020C20036C20026A4102746A2802002005200428020020036C20026A4102746A2802002005200320066C20026A4102746A2802006B2005200320086C20026A4102746A2802006B6A360200200241016A2202200028020822034E0D0220042802082108200A28020421060C00000B000B20034101480D00200028022C2108200028022021054100210203402008200120036C20026A4102746A2005200428020020036C20026A4102746A2802002005200320066C20026A4102746A2802006B360200200241016A2202200028020822034E0D01200A28020421060C00000B000B200141016A22012009490D000B0B200320096C22012000280230200028022C22036B41027522024B04402000412C6A200120026B100D0F0B200120024904402000200320014102746A3602300B0BCD0603087F027D027C200041206A21090240200028020820016C22032000280224200028022022046B41027522014B04402009200320016B100D0C010B200320014F0D002000200420034102746A3602240B024020032000280230200028022C22046B41027522014B04402000412C6A200320016B100D0C010B200320014F0D002000200420034102746A3602300B0240024002400240024002402000280214417F6A220141064B0D000240200141016B0E06010301040500020B2003450D0520002A020CBB210D20002802202104410021010340200420014102746A027F200220014103746A2B0300200DA3220E9944000000000000E041630440200EAA0C010B4180808080780B360200200141016A22012003470D000B0C050B10084199113602001009000B2003450D0320002A020C210B200028022021044100210103402004200141027422056A027F200220056A280200B2200B95220C8B430000004F5D0440200CA80C010B4180808080780B360200200141016A22012003470D000B0C030B2003450D0220002A020C210B20002802202104410021010340200420014102746A027F200220014101746A2E0100B2200B95220C8B430000004F5D0440200CA80C010B4180808080780B360200200141016A22012003470D000B0C020B2003450D0120002A020C210B20002802202104410021010340200420014102746A027F200120026A2C0000B2200B95220C8B430000004F5D0440200CA80C010B4180808080780B360200200141016A22012003470D000B0C010B2003450D0020002A020C210B200028022021044100210103402004200141027422056A027F200220056A2A0200200B95220C8B430000004F5D0440200CA80C010B4180808080780B360200200141016A22012003470D000B0B20002202410036021C20002204280208220541014E044003402009280200220A20064102746A28020021010240200620034F0440200121000C010B20012100200520066A220720034F0D000340200A20074102746A2802002208200020002008481B210020082001200120084A1B2101200520076A22072003490D000B0B2002200228021C220541C00020002001417F736AAC42018879A76B220041016A200520004A1B36021C200641016A220620042802082205480D000B0B0B3A01017F200041FC11360200200028022C2201044020002001360230200110020B20002802202201044020002001360224200110020B200010020B3801017F200041FC11360200200028022C2201044020002001360230200110020B20002802202201044020002001360224200110020B20000BE30301087F024020002802082204200028020422026B41047520014F04400340200241086A22034200370200200220033602042000200028020441106A22023602042001417F6A22010D000C02000B000B027F024002402002200028020022026B410475220520016A2203418080808001490440027F41002003200420026B2202410375220420042003491B41FFFFFFFF00200241047541FFFFFF3F491B2203450D001A20034180808080014F0D02200341047410030B2102200220034104746A2107200220054104746A220521020340200241086A2203420037020020022003360204200241106A21022001417F6A22010D000B2000280204220320002802002204460D020340200541706A2205200341706A220128020036020020052001280204360204200541086A2206200128020822083602002005200128020C220936020C02402009450440200520063602040C010B200820063602082001200341786A2203360204200341003602002001410036020C0B200122032004470D000B2000280204210420002802000C030B1007000B41AD11100C000B20040B2101200020053602002000200736020820002002360204200120044704400340200441746A200441786A2802001018200441706A22042001470D000B0B2001450D00200110020B0B09002000418D0810210B0B004188011003200110490B0B9A1104004180080B6C6E6F726D616C00636F6C6F7200757600706F736974696F6E00556E6B6E6F776E20656E74726F707900616C6C6F6361746F723C543E3A3A616C6C6F636174652873697A655F74206E2920276E272065786365656473206D6178696D756D20737570706F727465642073697A650041F4080BFC080100000003000000070000000F0000001F0000003F0000007F000000FF000000FF010000FF030000FF070000FF0F0000FF1F0000FF3F0000FF7F0000FFFF0000FFFF0100FFFF0300FFFF0700FFFF0F00FFFF1F00FFFF3F00FFFF7F00FFFFFF00FFFFFF01FFFFFF03FFFFFF07FFFFFF0FFFFFFF1FFFFFFF3FFFFFFF7F616C6C6F6361746F723C543E3A3A616C6C6F636174652873697A655F74206E2920276E272065786365656473206D6178696D756D20737570706F727465642073697A6500556E7369676E6564207479706573206E6F7420737570706F7274656420666F72206E6F726D616C73004E6F20706F736974696F6E2061747472696275746520666F756E642E205573652044494646206E6F726D616C20737472617465677920696E73746561642E004E3363727431355665727465784174747269627574654500F80B00009C0500004E33637274313147656E6572696341747472496945450000200C0000BC050000B4050000506F736974696F6E206174747220686173206265656E206F7665726C6F616465642C205573652044494646206E6F726D616C20737472617465677920696E73746561642E00466F726D6174206E6F7420737570706F7274656420666F72206E6F726D616C206174747269627574652028666C6F61742C20696E743136206F6E6C792900466F726D6174206E6F7420737570706F7274656420666F72206E6F726D616C206174747269627574652028666C6F61742C20696E743332206F7220696E743136206F6E6C792900000000000000F406000002000000030000000400000005000000060000000700000008000000090000000A0000000B0000000C0000004E3363727431304E6F726D616C41747472450000200C0000E0060000B4050000616C6C6F6361746F723C543E3A3A616C6C6F636174652873697A655F74206E2920276E272065786365656473206D6178696D756D20737570706F727465642073697A650000556E737570706F7274656420636F6C6F7220696E70757420666F726D61742E00556E737570706F7274656420636F6C6F72206F757470757420666F726D61742E00000000000000F00700000D0000000E0000000F00000010000000110000001200000013000000140000001500000016000000170000004E3363727439436F6C6F724174747245004E33637274313147656E65726963417474724968454500200C0000CD070000B4050000200C0000BC070000E407000000000000E40700000D00000018000000190000001A00000011000000120000001B0000001C00000015000000160000001D000000556E737570706F7274656420666F726D61742E004D656D6F7279206D75737420626520616C69676E65676E6564206F6E20342062797465732E004E6F742061206372742066696C652E00636F6C6F72004465636F64696E6720746F706F6C6F6779206661696C656400556E737570706F7274656420666F726D61742E00616C6C6F6361746F723C543E3A3A616C6C6F636174652873697A655F74206E2920276E272065786365656473206D6178696D756D20737570706F727465642073697A650041F8110B9507D40500001E0000001F00000020000000210000001100000022000000230000002400000025000000160000002600000062617369635F737472696E6700616C6C6F6361746F723C543E3A3A616C6C6F636174652873697A655F74206E2920276E272065786365656473206D6178696D756D20737570706F727465642073697A6500766563746F72007374643A3A657863657074696F6E000000000000B409000028000000290000002A000000537439657863657074696F6E00000000F80B0000A409000000000000E0090000010000002B0000002C000000537431316C6F6769635F6572726F7200200C0000D0090000B409000000000000140A0000010000002D0000002C000000537431326C656E6774685F6572726F7200000000200C0000000A0000E0090000537439747970655F696E666F00000000F80B0000200A00004E31305F5F637878616269763131365F5F7368696D5F747970655F696E666F4500000000200C0000380A0000300A00004E31305F5F637878616269763131375F5F636C6173735F747970655F696E666F45000000200C0000680A00005C0A00004E31305F5F637878616269763131375F5F70626173655F747970655F696E666F45000000200C0000980A00005C0A00004E31305F5F637878616269763131395F5F706F696E7465725F747970655F696E666F4500200C0000C80A0000BC0A00004E31305F5F637878616269763132305F5F66756E6374696F6E5F747970655F696E666F4500000000200C0000F80A00005C0A00004E31305F5F637878616269763132395F5F706F696E7465725F746F5F6D656D6265725F747970655F696E666F45000000200C00002C0B0000BC0A000000000000AC0B00002E0000002F0000003000000031000000320000004E31305F5F637878616269763132335F5F66756E64616D656E74616C5F747970655F696E666F4500200C0000840B00005C0A000076000000700B0000B80B0000446E0000700B0000C40B000063000000700B0000D00B0000504B63007C0C0000DC0B000001000000D40B0000000000008C0A00002E0000003300000030000000310000003400000035000000360000003700000000000000680C00002E00000038000000300000003100000034000000390000003A0000003B0000004E31305F5F637878616269763132305F5F73695F636C6173735F747970655F696E666F4500000000200C0000400C00008C0A000000000000EC0A00002E0000003C00000030000000310000003D0041901D0B02306F";
/*	var wasm_simd = "";
	var detector = new Uint8Array([0,97,115,109,1,0,0,0,1,4,1,96,0,0,3,3,2,0,0,5,3,1,0,1,12,1,0,10,22,2,12,0,65,0,65,0,65,0,252,10,0,0,11,7,0,65,0,253,4,26,11]);

	var wasm = wasm_base;

	if (WebAssembly.validate(detector)) {
		wasm = wasm_simd;
		console.log("Warning: corto is using experimental SIMD support");
	}*/
	var instance, heap;

	var env = {
		emscripten_notify_memory_growth: function(index) {
			heap = new Uint8Array(instance.exports.memory.buffer);
		},
		proc_exit:  function(rval) { return 52; }, //WASI_ENOSYS
	};

	function unhex(data) {
		var bytes = new Uint8Array(data.length / 2);
		for (var i = 0; i < data.length; i += 2) {
			bytes[i / 2] = parseInt(data.substr(i, 2), 16);
		}
		return bytes.buffer;
	}

	var promise =
		WebAssembly.instantiate(unhex(wasm_base), { env:env, wasi_unstable:env })
		.then(function(result) {
			instance = result.instance;
			instance.exports._start();
			env.emscripten_notify_memory_growth(0);
		});

	function pad() {
		return;
		var s = instance.exports.sbrk(0);
		var t = s & 0x3;
		if(t)
			instance.exports.sbrk(4 -t);
	}

	function decode(source, shortIndex = false, shortNormal = false, colorComponents = 4) {
		if(!source.length)
			source = new Uint8Array(source);
		var len = source.length;
		var exports = instance.exports;
		var sbrk = exports.malloc; //yes I am a criminal.
		var free = exports.free;


//copy source to heap. we could use directly source, but that is good only for the first em call.


		//We could use the heap instead of malloc, don't know cost (not much probably), and can't debug properly.
		//set initial heap position, to be restored at the end of the deconding.
		var pos = sbrk(0);

		var sptr = sbrk(len);
		heap.set(source, sptr);

		var decoder = exports.newDecoder(len, sptr);
		var nvert = exports.nvert(decoder);
		var nface = exports.nface(decoder);

		var geometry = {
			nvert: nvert,
			nface: nface,
		}

		var ngroups = exports.ngroups(decoder);
		if(ngroups > 0) {
			pad();
			var gp = sbrk(4*ngroups);
			exports.groups(decoder, gp);
			geometry.groups =  new Uint32Array( ngroups*4);
			geometry.grous.set(gp);
			free(gp);
		}

		var hasNormal = exports.hasNormal(decoder);
		var hasColor = exports.hasColor(decoder);
		var hasUv = exports.hasUv(decoder);

		var iptr = 0, pptr = 0, nptr = 0, cptr = 0, uptr = 0;
		if(nface) {
			pad();  //memory align needed for int, short, floats arrays if using sbrk
			if(shortIndex) {
				iptr = sbrk(nface * 6);
				exports.setIndex16(decoder, iptr);
			} else {
				iptr = sbrk(nface * 12);
				exports.setIndex32(decoder, iptr);
			}
		}

		pptr = sbrk(nvert * 12);
		exports.setPositions(decoder, pptr);

		if(hasUv) {
			pad();
			uptr = sbrk(nvert * 8);
			exports.setUvs(decoder, uptr);
		}

		if(hasNormal) {
			pad();
			if(shortNormal) {
				nptr = sbrk(nvert * 6);
				exports.setNormals16(decoder, nptr);
			} else {
				pptr = sbrk(nvert * 12);
				exports.setNormals32(decoder, nptr);
			}
		}

		if(hasColor) {
			pad();
			cptr = sbrk(nvert * colorComponents);
			exports.setColors(decoder, cptr, colorComponents);
		}
		pad();
		exports.decode(decoder);


		//typed  arrays needs to be created in javascript space, not as views of heap (next call will overwrite them!)
		//hence the double typed array.
		if(nface) {
			if(shortIndex)
				geometry.index = new Uint16Array(new Uint16Array(heap.buffer, iptr, nface*3));
			else
				geometry.index = new Uint32Array(new Uint32Array(heap.buffer, iptr, nface*3));
		}

		geometry.position = new Float32Array(new Float32Array(heap.buffer, pptr, nvert*3));

		if(hasNormal) {
			if(shortNormal)
				geometry.normal = new Int16Array(new Int16Array(heap.buffer, nptr, nvert*3));
			else
				geometry.normal = new Float32Array(new Float32Array(heap.buffer, nptr, nvert*3));
		}

		if(hasColor)
			geometry.color = new Uint8Array(new Uint8Array(heap.buffer, cptr, nvert*colorComponents));

		if(hasUv)
			geometry.uv = new Float32Array(new Float32Array(heap.buffer, uptr, nvert*2));

		exports.deleteDecoder(decoder);

		//restore heap position if using sbrk
		//sbrk(pos - sbrk(0)); 
		free(sptr);
		if(iptr) free(iptr);
		if(pptr) free(pptr);
		if(cptr) free(cptr);
		if(nptr) free(nptr);
		if(uptr) free(uptr);

		return geometry;
	};

	return {
		ready: promise,
		decode: decode
	};
})();

if (typeof exports === 'object' && typeof module === 'object')
	module.exports = CortoDecoder;
else if (typeof define === 'function' && define['amd'])
	define([], function() {
		return CortoDecoder;
	});
else if (typeof exports === 'object')
	exports["CortoDecoder"] = CortoDecoder;
"""
    }