
import json
import uuid
import re

import urllib.parse
from ...export.srs.crsexporttools import ConvertCRS
from ..exporterutils import ExporterUtils
from ...layerutils import LayerUtils
from ...sparqlutils import SPARQLUtils

from rdflib import Graph


class LayerExporter:

    @staticmethod
    def exportToFormat(layerOrTTLString,file,filename,format,prefixes):
        if isinstance(layerOrTTLString, str):
            layerToTTL=layerOrTTLString
        else:
            layerToTTL=LayerExporter.layerToTTLString(layerOrTTLString,prefixes)
        #QgsMessageLog.logMessage(str(layerToTTL),"LayerExporter", Qgis.Info)
        #QgsMessageLog.logMessage("Format: "+str(format), "LayerExporter", Qgis.Info)
        #QgsMessageLog.logMessage("File: " + str(file), "LayerExporter", Qgis.Info)
        g=Graph()
        g.parse(data=layerToTTL)
        g.bind("suni","http://www.github.com/sparqlunicorn#")
        if format in ExporterUtils.exportToFunction:
            if format not in ExporterUtils.rdfformats:
                ExporterUtils.exportToFunction[format](g,file,None,None,format.lower())
            else:
                ExporterUtils.exportToFunction[format](g,filename,None,None,format.lower())

    @staticmethod
    def layerToTTLString(layer, prefixes, vocab="GeoSPARQL", literaltype=["WKT"],columntypes=None):
        if columntypes==None:
            LayerExporter.layerToTTLString(layer, prefixes, vocab, literaltype)
            return
        if "namespace" not in columntypes or columntypes["namespace"]==None or columntypes["namespace"]=="":
            namespace = "http://www.github.com/sparqlunicorn#"
        else:
            namespace = columntypes["namespace"]
        if  "indid" not in columntypes or columntypes["indid"]==None or columntypes["indid"]=="":
            idcol = "id"
        else:
            idcol = columntypes["indid"]
        urilist=[]
        classurilist=[]
        proptypelist=[]
        for col in columntypes:
            if "propiri" in col:
                urilist.append(col["propiri"])
            else:
                urilist.append(None)
            if "concept" in col:
                classurilist.append(col["concept"])
            else:
                classurilist.append(None)
            if "prop" in col:
                proptypelist.append(col["concept"])
            else:
                proptypelist.append(None)
        LayerExporter.layerToTTLString(layer, prefixes, vocab, literaltype, urilist, classurilist,
                     list(columntypes["columns"].keys()), proptypelist,
                     None, None, namespace, idcol,
                     None)



    ## Converts a QGIS layer to TTL with or without a given column mapping.
    #  @param self The object pointer.
    #  @param layer The layer to convert.
    @staticmethod
    def layerToTTLString(layer, prefixes, vocab="GeoSPARQL", literaltype=["WKT"], urilist=None, classurilist=None,
                         includelist=None, proptypelist=None,
                         valuemappings=None, valuequeries=None, exportNameSpace=None, exportIdCol=None,
                         exportSetClass=None):
        fieldnames = [field.name() for field in layer.fields()]
        # QgsMessageLog.logMessage("FIELDNAMES: "+str(fieldnames),
        #                         MESSAGE_CATEGORY, Qgis.Info)
        # QgsMessageLog.logMessage("FIELDNAMES: "+str(vocab),
        #                         MESSAGE_CATEGORY, Qgis.Info)
        ttlstring = set()
        first = 0
        if exportNameSpace == None or exportNameSpace == "":
            namespace = "http://www.github.com/sparqlunicorn#"
        else:
            namespace = exportNameSpace
        if exportIdCol == "":
            idcol = "id"
        else:
            idcol = exportIdCol
        classcol = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        curid = ""
        if exportSetClass == None or exportSetClass == "":
            curclassid = namespace + str(uuid.uuid4())
        elif exportSetClass.startswith("http"):
            curclassid = exportSetClass
        else:
            curclassid = urllib.parse.quote(exportSetClass)
        layercrs = layer.crs()
        ttlstring.add("<http://www.opengis.net/ont/crs/" + str(layercrs.authid()).replace(" ",
                                                                                          "_") + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.opengis.net/ont/crs/SpatialReferenceSystem> .\n")
        ttlstring.add("<http://www.opengis.net/ont/crs/" + str(layercrs.authid()).replace(" ",
                                                                                          "_") + "> <http://www.opengis.net/ont/crs/asWKT> \"" + str(
            layercrs.toWkt()).replace("\"", "\\\"") + "\"^^<http://www.opengis.net/ont/crs/wktLiteral> .\n")
        ttlstring.add("<http://www.opengis.net/ont/crs/" + str(layercrs.authid()).replace(" ",
                                                                                          "_") + "> <http://www.opengis.net/ont/crs/asProj> \"" + str(
            layercrs.toProj4()) + "\"^^<http://www.opengis.net/ont/crs/proj4Literal> .\n")
        ccrs = ConvertCRS()
        ttlstring = ccrs.convertCRSFromWKTStringSet(layercrs.toWkt(), ttlstring)
        init = True
        for f in layer.getFeatures():
            geom = f.geometry()
            if idcol not in fieldnames:
                curid = namespace + str(uuid.uuid4())
            elif not str(f[idcol]).startswith("http"):
                curid = namespace + str(f[idcol])
            else:
                curid = f[idcol]
            if classcol not in fieldnames:
                ttlstring.add(
                    "<" + str(curid) + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <" + curclassid + "> .\n")
                if first == 0:
                    ttlstring.add("<" + str(
                        curclassid) + "> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://www.opengis.net/ont/geosparql#Feature> .\n")
                    ttlstring.add("<" + str(
                        curclassid) + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n")
            else:
                curclassid = f["http://www.w3.org/1999/02/22-rdf-syntax-ns#type"]
            ttlstring = LayerUtils.exportGeometryType(curid, geom, vocab, literaltype, init, ttlstring)
            if init:
                init = False
            fieldcounter = -1
            for propp in fieldnames:
                fieldcounter += 1
                # if fieldcounter>=len(fieldnames):
                #    fieldcounter=0
                if includelist is not None and fieldcounter < len(includelist) and includelist[fieldcounter] == False:
                    continue
                prop = propp
                print(str(fieldcounter))
                print(str(urilist) + "\n")
                print(str(classurilist) + "\n")
                print(str(includelist) + "\n")
                if urilist is not None and fieldcounter in urilist and urilist[fieldcounter] != "":
                    print(urilist)
                    if not urilist[fieldcounter].startswith("http"):
                        print("Does not start with http")
                        prop = urllib.parse.quote(urilist[fieldcounter])
                    else:
                        prop = urilist[fieldcounter]
                    print("New Prop from list: " + str(prop))
                if prop == "id":
                    continue
                if not prop.startswith("http"):
                    prop = namespace + prop
                if prop == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and "http" in str(f[propp]):
                    ttlstring.add(
                        "<" + str(f[propp]) + "> <" + str(prop) + "> <http://www.w3.org/2002/07/owl#Class> .\n")
                    ttlstring.add("<" + str(f[
                                                propp]) + "> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://www.opengis.net/ont/geosparql#Feature> .\n")
                    ttlstring.add("<" + str(curid) + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <" + str(
                        f[propp]) + "> .\n")
                # elif urilist!=None and fieldcounter<len(urilist) and urilist[fieldcounter]!="":
                #   ttlstring+="<"+curid+"> <"+prop+"> <"+str(f[propp])+"> .\n"
                #    if first<10:
                #       ttlstring+="<"+prop+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty> .\n"
                #       ttlstring+="<"+prop+"> <http://www.w3.org/2000/01/rdf-schema#domain> <"+curclassid+"> .\n"
                #      if classurilist[fieldcounter]!="":
                #           ttlstring+="<"+prop+"> <http://www.w3.org/2000/01/rdf-schema#range> <"+classurilist[fieldcounter]+"> .\n"
                elif prop == "http://www.w3.org/2000/01/rdf-schema#label" or prop == "http://www.w3.org/2000/01/rdf-schema#comment" or (
                        proptypelist is not None and proptypelist[fieldcounter] == "AnnotationProperty"):
                    ttlstring.add("<" + curid + "> <" + prop + "> \"" + str(f[propp]).replace('"',
                                                                                              '\\"') + "\"^^<http://www.w3.org/2001/XMLSchema#string> .\n")
                    if first < 10:
                        ttlstring.add(
                            "<" + prop + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#AnnotationProperty> .\n")
                        ttlstring.add(
                            "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#domain> <" + curclassid + "> .\n")
                elif not f[propp] or f[propp] is None or f[propp] == "":
                    continue
                elif proptypelist is not None and proptypelist[fieldcounter] == "SubClass":
                    ttlstring.add(
                        "<" + curid + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <" + str(f[propp]) + "> .\n")
                    ttlstring.add(
                        "<" + curid + "> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <" + curclassid + "> .\n")
                    if first < 10:
                        ttlstring.add("<" + str(f[
                                                    propp]) + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n")
                elif valuequeries is not None and propp in valuequeries:
                    # ttlstring += ""
                    results = SPARQLUtils.executeQuery(valuequeries[propp][1], "".join(
                        prefixes + valuequeries[propp][0].replace("%%" + propp + "%%", "\"" + str(f[propp]) + "\"")))
                    ttlstring.add(
                        "<" + curid + "> <" + prop + "> <" + results["results"]["bindings"][0]["item"]["value"] + "> .")
                    if first < 10:
                        ttlstring.add(
                            "<" + prop + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty> .\n")
                        ttlstring.add(
                            "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#domain> <" + curclassid + "> .\n")
                        if classurilist[fieldcounter] != "":
                            ttlstring.add(
                                "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#range> <" + classurilist[
                                    fieldcounter] + "> .\n")
                elif valuemappings is not None and propp in valuemappings and f[propp] in valuemappings[propp]:
                    ttlstring.add("<" + curid + "> <" + prop + "> <" + str(valuemappings[propp][f[propp]]) + "> .\n")
                    if first < 10:
                        ttlstring.add(
                            "<" + prop + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty> .\n")
                        ttlstring.add(
                            "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#domain> <" + curclassid + "> .\n")
                        if classurilist[fieldcounter] != "":
                            ttlstring.add(
                                "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#range> <" + classurilist[
                                    fieldcounter] + "> .\n")
                elif "http" in str(f[propp]) or (
                        proptypelist is not None and proptypelist[fieldcounter] == "ObjectProperty"):
                    ttlstring.add("<" + curid + "> <" + prop + "> <" + str(f[propp]) + "> .\n")
                    if first < 10:
                        ttlstring.add(
                            "<" + prop + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty> .\n")
                        ttlstring.add(
                            "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#domain> <" + curclassid + "> .\n")
                        if classurilist is not None and fieldcounter < len(classurilist) and classurilist[
                            fieldcounter] != "":
                            ttlstring.add(
                                "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#range> <" + classurilist[
                                    fieldcounter] + "> .\n")
                elif re.match(r'^-?\d+$', str(f[propp])):
                    ttlstring.add("<" + curid + "> <" + prop + "> \"" + str(
                        f[propp]) + "\"^^<http://www.w3.org/2001/XMLSchema#integer> .\n")
                    if first < 10:
                        ttlstring.add(
                            "<" + prop + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n")
                        ttlstring.add(
                            "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#domain> <" + curclassid + "> .\n")
                        ttlstring.add(
                            "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#range> <http://www.w3.org/2001/XMLSchema#integer> .\n")
                elif re.match(r'^-?\d+(?:\.\d+)?$', str(f[propp])):
                    ttlstring.add("<" + curid + "> <" + prop + "> \"" + str(
                        f[propp]) + "\"^^<http://www.w3.org/2001/XMLSchema#double> .\n")
                    if first:
                        ttlstring.add(
                            "<" + prop + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n")
                        ttlstring.add(
                            "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#domain> <" + curclassid + "> .\n")
                        ttlstring.add(
                            "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#range> <http://www.w3.org/2001/XMLSchema#double> .\n")
                else:
                    ttlstring.add("<" + curid + "> <" + prop + "> \"" + str(f[propp]).replace('"',
                                                                                              '\\"') + "\"^^<http://www.w3.org/2001/XMLSchema#string> .\n")
                    if first < 10:
                        ttlstring.add(
                            "<" + prop + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n")
                        ttlstring.add(
                            "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#domain> <" + curclassid + "> .\n")
                        ttlstring.add(
                            "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#range> <http://www.w3.org/2001/XMLSchema#string> .\n")
            if first < 10:
                first = first + 1
        return ccrs.ttlhead + "".join(ttlstring)


    @staticmethod
    def layerToDot(layer, prefixes, urilist=None, classurilist=None, includelist=None, proptypelist=None,
                         valuemappings=None, valuequeries=None,exportNameSpace=None,exportIdCol=None,exportSetClass=None):
        ttlstring=LayerUtils.layerToTTLString(layer, prefixes, urilist, classurilist, includelist, proptypelist,
                         valuemappings, valuequeries,exportNameSpace,exportIdCol,exportSetClass)
        #g=Graph()
        #g.parse(data=ttlstring,format="ttl")
        #stream = io.StringIO()
        #rdf2dot(g, stream)
        return ""#stream.getvalue()

    @staticmethod
    def layerToGraphML(layer):
        fieldnames = [field.name() for field in layer.fields()]
        result = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        result += "<graphml xmlns=\"http://graphml.graphdrawing.org/xmlns\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:y=\"http://www.yworks.com/xml/graphml\" xsi:schemaLocation=\"http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd\">\n"
        result += "<key for=\"node\" id=\"nodekey\" yfiles.type=\"nodegraphics\"></key>\n<key for=\"edge\" id=\"edgekey\" yfiles.type=\"edgegraphics\"></key><graph id=\"G\" edgedefault=\"undirected\">\n"
        nodeset = set()
        edgeset = set()
        fidcounter = 0
        edgecounter = 0
        literalcounter = 1
        nodeset.add(
            "<node id=\"geo:SpatialObject\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#ff8800\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" autoSizePolicy=\"content\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">geo:SpatialObject</y:NodeLabel></y:ShapeNode></data></node>\n")

        nodeset.add(
            "<node id=\"geo:Feature\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#ff8800\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" autoSizePolicy=\"content\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">geo:Feature</y:NodeLabel></y:ShapeNode></data></node>\n")
        nodeset.add(
            "<node id=\"geo:Geometry\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#ff8800\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" autoSizePolicy=\"content\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">geo:Geometry</y:NodeLabel></y:ShapeNode></data></node>\n")
        edgeset.add(
            "<edge id=\"eFeature\" source=\"geo:Feature\" target=\"geo:SpatialObject\">\n<data key=\"edgekey\">\n<y:PolyLineEdge>\n<y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hastext=\"true\" visible=\"true\" width=\"4.0\">" + str(
                "rdfs:subClassOf") + "</y:EdgeLabel>\n</y:PolyLineEdge>\n</data>\n</edge>\n")
        edgeset.add(
            "<edge id=\"eGeometry\" source=\"geo:Geometry\" target=\"geo:SpatialObject\">\n<data key=\"edgekey\">\n<y:PolyLineEdge>\n<y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hastext=\"true\" visible=\"true\" width=\"4.0\">" + str(
                "rdfs:subClassOf") + "</y:EdgeLabel>\n</y:PolyLineEdge>\n</data>\n</edge>\n")
        for f in layer.getFeatures():
            geom = f.geometry()
            nodeset.add("<node id=\"fid_" + str(
                fidcounter) + "\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#800080\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" autoSizePolicy=\"content\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">fid_" + str(
                fidcounter) + "</y:NodeLabel></y:ShapeNode></data></node>\n")
            fieldcounter = 0
            for propp in fieldnames:
                fieldcounter += 1
                prop = propp
                if prop.startswith("http"):
                    toadd = "<node id=\"" + str(prop) + "\" uri=\"" + str(
                        prop) + "\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#800080\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" autoSizePolicy=\"content\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">"
                    if f[propp].startswith("http"):
                        toadd += SPARQLUtils.labelFromURI(str(f[propp]).replace("<", "").replace(">",
                                                                                                 "")) + "</y:NodeLabel></y:ShapeNode></data></node>\n"
                    else:
                        toadd += "<!CDATA[" + str(f[propp]).replace("<", "").replace(">",
                                                                                     "") + "]]></y:NodeLabel></y:ShapeNode></data></node>\n"
                    nodeset.add(toadd)
                    edgeset.add(
                        "<edge id=\"e" + str(edgecounter) + "\" uri=\"" + str(propp) + "\" source=\"fid_" + str(
                            fidcounter) + "\" target=\"" + str(
                            prop) + "\"><data key=\"edgekey\"><y:PolyLineEdge><y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hastext=\"true\" visible=\"true\" width=\"4.0\">" + str(
                            propp) + "</y:EdgeLabel>\n</y:PolyLineEdge>\n</data>\n</edge>\n")
                    edgecounter += 1
                else:
                    nodeset.add("<node id=\"literal" + str(
                        literalcounter) + "\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#008000\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" autoSizePolicy=\"content\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">" + str(
                        f[propp]).replace("<", "").replace(">", "")[
                                                                                                                                                                                                                                                                                                                                    0:10] + "</y:NodeLabel></y:ShapeNode></data></node>\n")
                    edgeset.add(
                        "<edge id=\"e" + str(edgecounter) + "\" uri=\"" + str(propp) + "\" source=\"fid_" + str(
                            fidcounter) + "\" target=\"literal" + str(
                            literalcounter) + "\">\n<data key=\"edgekey\">\n<y:PolyLineEdge>\n<y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hastext=\"true\" visible=\"true\" width=\"4.0\">" + str(
                            propp) + "</y:EdgeLabel>\n</y:PolyLineEdge>\n</data>\n</edge>\n")
                    literalcounter += 1
                    edgecounter += 1
            nodeset.add("<node id=\"fid_" + str(fidcounter
                                                ) + "_geom\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#800080\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" autoSizePolicy=\"content\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">fid_" + str(
                fidcounter) + "_geom</y:NodeLabel></y:ShapeNode></data></node>\n")
            nodeset.add("<node id=\"literal" + str(
                literalcounter) + "\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#008000\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" autoSizePolicy=\"content\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">" + str(
                geom.asWkt())[0:10] + "</y:NodeLabel></y:ShapeNode></data></node>\n")
            edgeset.add("<edge id=\"e" + str(edgecounter) + "\" source=\"fid_" + str(
                fidcounter) + "\" target=\"fid_" + str(
                fidcounter) + "_geom\">\n<data key=\"edgekey\">\n<y:PolyLineEdge>\n<y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hastext=\"true\" visible=\"true\" width=\"4.0\">" + str(
                "geom:asWkt") + "</y:EdgeLabel>\n</y:PolyLineEdge>\n</data>\n</edge>\n")
            edgeset.add("<edge id=\"e" + str(edgecounter) + "type\" source=\"fid_" + str(
                fidcounter) + "_geom\" target=\"geo:Geometry\">\n<data key=\"edgekey\">\n<y:PolyLineEdge>\n<y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hastext=\"true\" visible=\"true\" width=\"4.0\">" + str(
                "rdf:type") + "</y:EdgeLabel>\n</y:PolyLineEdge>\n</data>\n</edge>\n")
            edgeset.add("<edge id=\"e" + str(edgecounter) + "\" source=\"fid_" + str(
                fidcounter) + "_geom\" target=\"literal" + str(
                literalcounter) + "\">\n<data key=\"edgekey\">\n<y:PolyLineEdge>\n<y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hastext=\"true\" visible=\"true\" width=\"4.0\">" + str(
                "geom:asWkt") + "</y:EdgeLabel>\n</y:PolyLineEdge>\n</data>\n</edge>\n")
            edgecounter += 1
            edgeset.add("<edge id=\"e" + str(edgecounter) + "\" source=\"fid_" + str(
                fidcounter) + "\" target=\"geo:Feature\">\n<data key=\"edgekey\">\n<y:PolyLineEdge>\n<y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hastext=\"true\" visible=\"true\" width=\"4.0\">" + str(
                "rdf:type") + "</y:EdgeLabel>\n</y:PolyLineEdge>\n</data>\n</edge>\n")
            literalcounter += 1
            edgecounter += 1
            fidcounter += 1
        result += "".join(nodeset)
        result += "".join(edgeset)
        result += "</graph>\n"
        result += "</graphml>"
        return result

    @staticmethod
    def layerAsGeoJSONLD(layer):
        context = {
            "geojson": "https://purl.org/geojson/vocab#",
            "Feature": "geojson:Feature",
            "FeatureCollection": "geojson:FeatureCollection",
            "GeometryCollection": "geojson:GeometryCollection",
            "LineString": "geojson:LineString",
            "MultiLineString": "geojson:MultiLineString",
            "MultiPoint": "geojson:MultiPoint",
            "MultiPolygon": "geojson:MultiPolygon",
            "Point": "geojson:Point",
            "Polygon": "geojson:Polygon",
            "bbox": {
                "@container": "@list",
                "@id": "geojson:bbox"
            },
            "coordinates": {
                "@container": "@list",
                "@id": "geojson:coordinates"
            },
            "features": {
                "@container": "@set",
                "@id": "geojson:features"
            },
            "geometry": "geojson:geometry",
            "id": "@id",
            "properties": "geojson:properties",
            "type": "@type",
            "description": "http://purl.org/dc/terms/description",
            "title": "http://purl.org/dc/terms/title"
        }
        fieldnames = [field.name() for field in layer.fields()]
        currentgeo = {}
        geos = []
        for f in layer.getFeatures():
            geom = f.geometry()
            currentgeo = {'id': "", 'geometry': json.loads(geom.asJson()), 'properties': {}}
            for prop in fieldnames:
                if prop == "id":
                    currentgeo["id"] = f[prop]
                else:
                    currentgeo["properties"][prop] = f[prop]
            geos.append(currentgeo)
        featurecollection = {"@context": context, "type": "FeatureCollection",
                             "@id": "http://example.com/collections/1", "features": geos}
        return featurecollection