from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
)
from qgis.core import Qgis
from qgis.core import QgsWkbTypes
import uuid
import re
import json
import io
import urllib.parse
from ..util.crsexporttools import ConvertCRS
from ..util.sparqlutils import SPARQLUtils
#from rdflib.tools.rdf2dot import rdf2dot
#from rdflib import Graph

MESSAGE_CATEGORY = 'LayerUtils'

class LayerUtils:

    ## Detects the type of a column which is to be entered into a QGIS vector layer.
    #  @param self The object pointer.
    #  @param table the layer to analyze
    # the column to consider
    @staticmethod
    def detectColumnType(resultmap):
        intcount = 0
        doublecount = 0
        for res in resultmap:
            if resultmap[res] == None or resultmap[res] == "":
                intcount += 1
                doublecount += 1
                continue
            if resultmap[res].isdigit():
                intcount += 1
            try:
                float(resultmap[res])
                doublecount += 1
            except:
                print("")
        QgsMessageLog.logMessage(str(intcount) + " - " + str(doublecount) + " - " + str(len(resultmap)),
                                 MESSAGE_CATEGORY, Qgis.Info)
        if intcount == len(resultmap):
            return QVariant.Int
        if doublecount == len(resultmap):
            return QVariant.Double
        return QVariant.String

    ## Converts a QGIS layer to TTL with or withour a given column mapping.
    #  @param self The object pointer.
    #  @param layer The layer to convert.
    @staticmethod
    def layerToTTLString(layer, prefixes, urilist=None, classurilist=None, includelist=None, proptypelist=None,
                         valuemappings=None, valuequeries=None,exportNameSpace=None,exportIdCol=None,exportSetClass=None):
        fieldnames = [field.name() for field in layer.fields()]
        ttlstring=set()
        ttlstring.add("<http://www.opengis.net/ont/geosparql#Feature> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n")
        ttlstring.add("<http://www.opengis.net/ont/geosparql#SpatialObject> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n")
        ttlstring.add("<http://www.opengis.net/ont/geosparql#Geometry> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n")
        ttlstring.add("<http://www.opengis.net/ont/geosparql#hasGeometry> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty> .\n")
        ttlstring.add("<http://www.opengis.net/ont/geosparql#asWKT> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n")
        ttlstring.add("<http://www.opengis.net/ont/geosparql#Feature> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://www.opengis.net/ont/geosparql#SpatialObject> .\n")
        ttlstring.add("<http://www.opengis.net/ont/geosparql#Geometry> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://www.opengis.net/ont/geosparql#SpatialObject> .\n")
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
        ccrs=ConvertCRS()
        ttlstring=ccrs.convertCRSFromWKTStringSet(layercrs.toWkt(),ttlstring)
        for f in layer.getFeatures():
            geom = f.geometry()
            if not idcol in fieldnames:
                curid = namespace + str(uuid.uuid4())
            elif not str(f[idcol]).startswith("http"):
                curid = namespace + str(f[idcol])
            else:
                curid = f[idcol]
            if not classcol in fieldnames:
                ttlstring.add( "<" + str(
                    curid) + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <" + curclassid + "> .\n")
                if first == 0:
                    ttlstring.add( "<" + str(
                        curclassid) + "> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://www.opengis.net/ont/geosparql#Feature> .\n")
                    ttlstring.add( "<" + str(
                        curclassid) + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n")
            ttlstring.add( "<" + str(
                curid) + "> <http://www.opengis.net/ont/geosparql#hasGeometry> <" + curid + "_geom> .\n")
            ttlstring.add( "<" + str(
                curid) + "_geom> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.opengis.net/ont/geosparql#" + QgsWkbTypes.displayString(
                geom.wkbType()) + "> .\n")
            ttlstring.add( "<http://www.opengis.net/ont/geosparql#" + QgsWkbTypes.displayString(
                geom.wkbType()) + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n")
            ttlstring.add( "<http://www.opengis.net/ont/geosparql#" + QgsWkbTypes.displayString(
                geom.wkbType()) + "> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://www.opengis.net/ont/geosparql#Geometry> .\n")
            ttlstring.add( "<" + str(
                curid) + "_geom> <http://www.opengis.net/ont/geosparql#asWKT> \"" + geom.asWkt() + "\"^^<http://www.opengis.net/ont/geosparql#wktLiteral> .\n")
            fieldcounter = -1
            for propp in fieldnames:
                fieldcounter += 1
                # if fieldcounter>=len(fieldnames):
                #    fieldcounter=0
                if includelist != None and fieldcounter < len(includelist) and includelist[fieldcounter] == False:
                    continue
                prop = propp
                print(str(fieldcounter))
                print(str(urilist) + "\n")
                print(str(classurilist) + "\n")
                print(str(includelist) + "\n")
                if urilist != None and urilist[fieldcounter] != "":
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
                    ttlstring.add( "<" + str(f[propp]) + "> <" + str(prop) + "> <http://www.w3.org/2002/07/owl#Class> .\n")
                    ttlstring.add( "<" + str(f[
                                               propp]) + "> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://www.opengis.net/ont/geosparql#Feature> .\n")

                # elif urilist!=None and fieldcounter<len(urilist) and urilist[fieldcounter]!="":
                #   ttlstring+="<"+curid+"> <"+prop+"> <"+str(f[propp])+"> .\n"
                #    if first<10:
                #       ttlstring+="<"+prop+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty> .\n"
                #       ttlstring+="<"+prop+"> <http://www.w3.org/2000/01/rdf-schema#domain> <"+curclassid+"> .\n"
                #      if classurilist[fieldcounter]!="":
                #           ttlstring+="<"+prop+"> <http://www.w3.org/2000/01/rdf-schema#range> <"+classurilist[fieldcounter]+"> .\n"
                elif prop == "http://www.w3.org/2000/01/rdf-schema#label" or prop == "http://www.w3.org/2000/01/rdf-schema#comment" or (
                        proptypelist != None and proptypelist[fieldcounter] == "AnnotationProperty"):
                    ttlstring.add( "<" + curid + "> <" + prop + "> \"" + str(f[propp]).replace('"',
                                                                                             '\\"') + "\"^^<http://www.w3.org/2001/XMLSchema#string> .\n")
                    if first < 10:
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#AnnotationProperty> .\n")
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#domain> <" + curclassid + "> .\n")
                elif not f[propp] or f[propp] == None or f[propp] == "":
                    continue
                elif proptypelist != None and proptypelist[fieldcounter] == "SubClass":
                    ttlstring.add( "<" + curid + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <" + str(
                        f[propp]) + "> .\n")
                    ttlstring.add( "<" + curid + "> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <" + curclassid + "> .\n")
                    if first < 10:
                        ttlstring.add( "<" + str(f[
                                                   propp]) + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n")
                elif valuequeries != None and propp in valuequeries:
                    #ttlstring += ""
                    results=SPARQLUtils.executeQuery(valuequeries[propp][1],"".join(prefixes + valuequeries[propp][0].replace("%%" + propp + "%%","\"" + str(f[propp]) + "\"")))
                    ttlstring.add( "<" + curid + "> <" + prop + "> <" + results["results"]["bindings"][0]["item"][
                        "value"] + "> .")
                    if first < 10:
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty> .\n")
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#domain> <" + curclassid + "> .\n")
                        if classurilist[fieldcounter] != "":
                            ttlstring.add( "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#range> <" + classurilist[
                                fieldcounter] + "> .\n")
                elif valuemappings != None and propp in valuemappings and f[propp] in valuemappings[propp]:
                    ttlstring.add( "<" + curid + "> <" + prop + "> <" + str(valuemappings[propp][f[propp]]) + "> .\n")
                    if first < 10:
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty> .\n")
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#domain> <" + curclassid + "> .\n")
                        if classurilist[fieldcounter] != "":
                            ttlstring.add( "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#range> <" + classurilist[
                                fieldcounter] + "> .\n")
                elif "http" in str(f[propp]) or (
                        proptypelist != None and proptypelist[fieldcounter] == "ObjectProperty"):
                    ttlstring.add( "<" + curid + "> <" + prop + "> <" + str(f[propp]) + "> .\n")
                    if first < 10:
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty> .\n")
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#domain> <" + curclassid + "> .\n")
                        if classurilist != None and fieldcounter < len(classurilist) and classurilist[
                            fieldcounter] != "":
                            ttlstring.add( "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#range> <" + classurilist[fieldcounter] + "> .\n")
                elif re.match(r'^-?\d+$', str(f[propp])):
                    ttlstring.add( "<" + curid + "> <" + prop + "> \"" + str(
                        f[propp]) + "\"^^<http://www.w3.org/2001/XMLSchema#integer> .\n")
                    if first < 10:
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n")
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#domain> <" + curclassid + "> .\n")
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#range> <http://www.w3.org/2001/XMLSchema#integer> .\n")
                elif re.match(r'^-?\d+(?:\.\d+)?$', str(f[propp])):
                    ttlstring.add( "<" + curid + "> <" + prop + "> \"" + str(
                        f[propp]) + "\"^^<http://www.w3.org/2001/XMLSchema#double> .\n")
                    if first:
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n")
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#domain> <" + curclassid + "> .\n")
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#range> <http://www.w3.org/2001/XMLSchema#double> .\n")
                else:
                    ttlstring.add( "<" + curid + "> <" + prop + "> \"" + str(f[propp]).replace('"',
                                                                                             '\\"') + "\"^^<http://www.w3.org/2001/XMLSchema#string> .\n")
                    if first < 10:
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n")
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#domain> <" + curclassid + "> .\n")
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#range> <http://www.w3.org/2001/XMLSchema#string> .\n")
            if first < 10:
                first = first + 1
        return ccrs.ttlhead+"".join(ttlstring)

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
        result="<?xml version=\"1.0\" encoding=\"UTF-8\">\n"
        result+="<graphml xmlns=\"http://graphml.graphdrawing.org/xmlns\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd\">\n"
        result+="<graph id=\"G\" edgedefault=\"undirected\">\n"
        nodeset=set()
        edgeset=set()
        fidcounter=0
        for f in layer.getFeatures():
            geom = f.geometry()
            nodeset.add("<node id=\"fid_"+str(fidcounter)+"\"/>\n")
            fieldcounter=0
            for propp in fieldnames:
                fieldcounter += 1
                prop = propp
                nodeset.add("<node id=\"" + str(prop) + "\"/>\n")
                edgeset.add("<edge id=\"fid_"+str(fidcounter)+"_"+str(prop)+"\" source=\"fid_"+str(fidcounter)+"\" target=\""+str(prop)+"\"/>\n")
            fidcounter+=1
        result+="".join(nodeset)
        result+="".join(edgeset)
        result+="</graph>\n"
        result+="</graphml>"
        return result

    ## Exports a layer as GeoJSONLD.
    #  @param self The object pointer.
    @staticmethod
    def exportLayerAsGeoJSONLD(layer):
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