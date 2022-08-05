from qgis.PyQt.QtCore import QVariant,QDateTime
from qgis.core import (
    QgsMessageLog
)
from osgeo import ogr
from qgis.core import QgsFeature, Qgis, QgsWkbTypes, QgsProject, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
import uuid
import re
import json
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
        datecount=0
        uricount=0
        stringcount=0
        for res in resultmap:
            if resultmap[res] == None or resultmap[res] == "":
                intcount += 1
                doublecount += 1
                continue
            if isinstance(resultmap[res],QDateTime):
                datecount+=1
                continue
            if resultmap[res].isdigit():
                intcount += 1
                continue
            try:
                float(resultmap[res])
                doublecount += 1
                continue
            except:
                print("")
            if resultmap[res].startswith("http"):
                uricount+=1
                continue
            stringcount+=1
        QgsMessageLog.logMessage(str(intcount) + " - " + str(doublecount) + " - " + str(len(resultmap)),
                                 MESSAGE_CATEGORY, Qgis.Info)
        if intcount == len(resultmap):
            return QVariant.Int
        if doublecount == len(resultmap):
            return QVariant.Double
        if datecount == len(resultmap):
            return "xsd:date"
        if uricount == len(resultmap):
            return "xsd:anyURI"
        return QVariant.String

    @staticmethod
    def detectLayerColumnType(layer,columnindex):
        features = layer.getFeatures()
        columnmap={}
        counter=0
        for feat in features:
            attrs = feat.attributes()
            columnmap[counter]=attrs[columnindex]
            counter+=1
        return LayerUtils.detectColumnType(columnmap)

    @staticmethod
    def getLayerColumnAsList(layer,columnindex):
        features = layer.getFeatures()
        result=[]
        counter=0
        for feat in features:
            attrs = feat.attributes()
            result.append(attrs[columnindex])
        return result

    @staticmethod
    def detectLayerColumnTypes(layer):
        features = layer.getFeatures()
        columnmap={}
        feature = QgsFeature()
        features.nextFeature(feature)
        attrs = feature.attributes()
        for i in range(0, len(attrs)):
            columnmap[i]=LayerUtils.detectLayerColumnType(layer,i)
        return LayerUtils.detectColumnType(columnmap)

    @staticmethod
    def processLiteral(literal, literaltype, reproject,currentlayergeojson=None,triplestoreconf=None):
        QgsMessageLog.logMessage("Process literal: " + str(literal) + " --- " + str(literaltype))
        geom = None
        if triplestoreconf!=None and "literaltype" in triplestoreconf:
            literaltype = triplestoreconf["literaltype"]
        if literal.startswith("http"):
            res = SPARQLUtils.handleURILiteral(literal,currentlayergeojson)
            if res == None:
                return json.loads("{\"geometry\":{}}")
            return res[0]
        if literaltype == "":
            literaltype = SPARQLUtils.detectGeoLiteralType(literal)
        curcrs=None
        if "wkt" in literaltype.lower() or literaltype=="http://www.openlinksw.com/schemas/virtrdf#Geometry":
            literal = literal.strip()
            if literal.startswith("<http"):
                index = literal.index(">") + 1
                slashindex = literal.rfind("/") + 1
                reproject = literal[slashindex:(index - 1)]
                geom = QgsGeometry.fromWkt(literal[index:])
                curcrs=literal[slashindex:(index - 1)]
            else:
                geom = QgsGeometry.fromWkt(literal)
        elif "gml" in literaltype.lower():
            if "EPSG" in literal and "http" in literal:
                srspart=literal[literal.find("srsName="):literal.find(">")]
                curcrs=srspart.replace("srsName=\"http://www.opengis.net/def/crs/EPSG/0/","")
                curcrs=curcrs.replace("\"","")
            elif "EPSG" in literal and "http" not in literal:
                srspart = literal[literal.find("srsName="):literal.find(">")]
                curcrs=srspart.replace("srsName=\"EPSG:","")
                curcrs=curcrs.replace("\"", "")
            geom=QgsGeometry.fromWkt(ogr.CreateGeometryFromGML(literal).ExportToWkt())
        elif "geojson" in literaltype.lower():
            return literal
        elif "wkb" in literaltype.lower():
            geom = QgsGeometry.fromWkb(bytes.fromhex(literal))
        if geom != None and reproject != "":
            sourceCrs = QgsCoordinateReferenceSystem(reproject)
            destCrs = QgsCoordinateReferenceSystem.fromOgcWmsCrs("EPSG:4326")
            tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
            geom.transform(tr)
        if geom != None:
            res=json.loads(geom.asJson())
            if currentlayergeojson!=None:
                currentlayergeojson["geometry"]=res
                if curcrs != None:
                    currentlayergeojson["crs"]=curcrs
                return currentlayergeojson
            if curcrs!=None:
                res["crs"]=curcrs
            return res
        return None


    @staticmethod
    def exportGeometryType(curid,geom,vocab,literaltype,init,ttlstring):
        if "GeoSPARQL" in vocab:
            if init:
                ttlstring.add(
                    "<http://www.opengis.net/ont/geosparql#Feature> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n")
                ttlstring.add(
                    "<http://www.opengis.net/ont/geosparql#SpatialObject> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n")
                ttlstring.add(
                    "<http://www.opengis.net/ont/geosparql#Geometry> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n")
                ttlstring.add(
                    "<http://www.opengis.net/ont/geosparql#hasGeometry> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty> .\n")
                ttlstring.add(
                    "<http://www.opengis.net/ont/geosparql#asWKT> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n")
                ttlstring.add(
                    "<http://www.opengis.net/ont/geosparql#Feature> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://www.opengis.net/ont/geosparql#SpatialObject> .\n")
                ttlstring.add(
                    "<http://www.opengis.net/ont/geosparql#Geometry> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://www.opengis.net/ont/geosparql#SpatialObject> .\n")
            ttlstring.add( "<" + str(curid) + "> <http://www.opengis.net/ont/geosparql#hasGeometry> <" + str(curid) + "_geom> .\n")
            ttlstring.add( "<" + str(curid) + "_geom> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.opengis.net/ont/geosparql#" + QgsWkbTypes.displayString(
                geom.wkbType()) + "> .\n")
            ttlstring.add( "<http://www.opengis.net/ont/geosparql#" + QgsWkbTypes.displayString(
                geom.wkbType()) + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n")
            ttlstring.add( "<http://www.opengis.net/ont/geosparql#" + QgsWkbTypes.displayString(
                geom.wkbType()) + "> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://www.opengis.net/ont/geosparql#Geometry> .\n")
            if "WKT" in literaltype:
                ttlstring.add( "<" + str(curid) + "_geom> <http://www.opengis.net/ont/geosparql#asWKT> \"" + geom.asWkt() + "\"^^<http://www.opengis.net/ont/geosparql#wktLiteral> .\n")
            if literaltype == "GeoJSON":
                ttlstring.add("<" + str(curid) + "_geom> <http://www.opengis.net/ont/geosparql#asGeoJSON> \"" + geom.asJson() + "\"^^<http://www.opengis.net/ont/geosparql#geoJSONLiteral> .\n")
            if literaltype == "WKB":
                ttlstring.add("<" + str(curid) + "_geom> <http://www.opengis.net/ont/geosparql#asWKB> \"" + geom.asWkb() + "\"^^<http://www.opengis.net/ont/geosparql#wkbLiteral> .\n")
        elif "W3C" in vocab and "Geo" in vocab:
            if init:
                ttlstring.add(
                    "<http://www.w3.org/2003/01/geo/wgs84_pos#lat> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n")
                ttlstring.add(
                    "<http://www.w3.org/2003/01/geo/wgs84_pos#long> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n")
            ttlstring.add( "<" + str(curid) + "> <http://www.w3.org/2003/01/geo/wgs84_pos#lat> \""+str(geom.centroid().vertexAt(0).x())+"\"^^<http://www.w3.org/2001/XMLSchema#double> .\n")
            ttlstring.add( "<" + str(curid) + "> <http://www.w3.org/2003/01/geo/wgs84_pos#long> \""+str(geom.centroid().vertexAt(0).y())+"\"^^<http://www.w3.org/2001/XMLSchema#double> .\n")
        elif "Schema.org" in vocab:
            if init:
                ttlstring.add(
                    "<http://schema.org/geo> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty> .\n")
                ttlstring.add(
                    "<http://schema.org/latitude> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n")
                ttlstring.add(
                    "<http://schema.org/longitude> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n")
            ttlstring.add( "<" + str(
                curid) + "> <http://schema.org/geo> <" + str(curid) + "_geom> .\n")
            ttlstring.add("<" + str(
                curid) + "_geom> <http://schema.org/latitude> \"" + str(
                geom.centroid().vertexAt(0).x()) + "\"^^<http://www.w3.org/2001/XMLSchema#double> .\n")
            ttlstring.add("<" + str(
                curid) + "_geom> <http://schema.org/longitude> \"" + str(
                geom.centroid().vertexAt(0).y()) + "\"^^<http://www.w3.org/2001/XMLSchema#double> .\n")
        elif "OSMRDF" in vocab:
            if init:
                ttlstring.add(
                    "<https://www.openstreetmap.org/meta/loc> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n")
            ttlstring.add("<" + str(
                curid) + "> <https://www.openstreetmap.org/meta/loc> \"" + geom.asWkt() + "\" .\n")
        elif "NeoGeo" in vocab:
            if init:
                ttlstring.add(
                    "<http://geovocab.org/spatial#Feature> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n")
                ttlstring.add(
                    "<http://geovocab.org/geometry#Geometry> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n")
                ttlstring.add(
                    "<http://geovocab.org/geometry#geometry> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty> .\n")
                ttlstring.add(
                    "<http://geovocab.org/geometry#asWKT> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n")
            ttlstring.add( "<" + str(curid) + "> <http://geovocab.org/geometry#geometry> <" + str(curid) + "_geom> .\n")
            ttlstring.add( "<" + str(curid) + "_geom> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://geovocab.org/geometry#" + QgsWkbTypes.displayString(
                geom.wkbType()) + "> .\n")
            ttlstring.add( "<http://geovocab.org/geometry#" + QgsWkbTypes.displayString(
                geom.wkbType()) + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n")
            ttlstring.add( "<http://geovocab.org/geometry#" + QgsWkbTypes.displayString(
                geom.wkbType()) + "> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://geovocab.org/geometry#Geometry> .\n")
            ttlstring.add( "<" + str(curid) + "_geom> <http://geovocab.org/geometry#asWKT> \"" + geom.asWkt() + "\"^^<http://www.opengis.net/ont/geosparql#wktLiteral> .\n")
        elif "OrdnanceUK" in vocab:
            if init:
                ttlstring.add(
                    "<http://data.ordnancesurvey.co.uk/ontology/spatialrelations/easting> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n")
                ttlstring.add(
                    "<http://data.ordnancesurvey.co.uk/ontology/spatialrelations/northing> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n")
            ttlstring.add("<" + str(
                curid) + "> <http://data.ordnancesurvey.co.uk/ontology/spatialrelations/easting> \"" + str(
                geom.centroid().vertexAt(0).x()) + "\" .\n")
            ttlstring.add("<" + str(
                curid) + "> <http://data.ordnancesurvey.co.uk/ontology/spatialrelations/northing> \"" + str(
                geom.centroid().vertexAt(0).y()) + "\" .\n")
        return ttlstring



    ## Converts a QGIS layer to TTL with or without a given column mapping.
    #  @param self The object pointer.
    #  @param layer The layer to convert.
    @staticmethod
    def layerToTTLString(layer, prefixes,vocab="GeoSPARQL",literaltype=["WKT"], urilist=None, classurilist=None, includelist=None, proptypelist=None,
                         valuemappings=None, valuequeries=None,exportNameSpace=None,exportIdCol=None,exportSetClass=None):
        fieldnames = [field.name() for field in layer.fields()]
        QgsMessageLog.logMessage("FIELDNAMES: "+str(fieldnames),
                                 MESSAGE_CATEGORY, Qgis.Info)
        QgsMessageLog.logMessage("FIELDNAMES: "+str(vocab),
                                 MESSAGE_CATEGORY, Qgis.Info)
        ttlstring=set()
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
        ttlstring.add("<http://www.opengis.net/ont/crs/" + str(layercrs.authid()).replace(" ","_") + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.opengis.net/ont/crs/SpatialReferenceSystem> .\n")
        ttlstring.add("<http://www.opengis.net/ont/crs/" + str(layercrs.authid()).replace(" ","_") + "> <http://www.opengis.net/ont/crs/asWKT> \"" + str(
            layercrs.toWkt()).replace("\"", "\\\"") + "\"^^<http://www.opengis.net/ont/crs/wktLiteral> .\n")
        ttlstring.add("<http://www.opengis.net/ont/crs/" + str(layercrs.authid()).replace(" ","_") + "> <http://www.opengis.net/ont/crs/asProj> \"" + str(
            layercrs.toProj4()) + "\"^^<http://www.opengis.net/ont/crs/proj4Literal> .\n")
        ccrs=ConvertCRS()
        ttlstring=ccrs.convertCRSFromWKTStringSet(layercrs.toWkt(),ttlstring)
        init=True
        for f in layer.getFeatures():
            geom = f.geometry()
            if idcol not in fieldnames:
                curid = namespace + str(uuid.uuid4())
            elif not str(f[idcol]).startswith("http"):
                curid = namespace + str(f[idcol])
            else:
                curid = f[idcol]
            if classcol not in fieldnames:
                ttlstring.add( "<" + str(curid) + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <" + curclassid + "> .\n")
                if first == 0:
                    ttlstring.add( "<" + str(curclassid) + "> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://www.opengis.net/ont/geosparql#Feature> .\n")
                    ttlstring.add( "<" + str(curclassid) + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n")
            else:
                curclassid=f["http://www.w3.org/1999/02/22-rdf-syntax-ns#type"]
            ttlstring=LayerUtils.exportGeometryType(curid, geom, vocab, literaltype, init, ttlstring)
            if init:
                init=False
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
                    ttlstring.add( "<" + str(f[propp]) + "> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://www.opengis.net/ont/geosparql#Feature> .\n")
                    ttlstring.add("<" + str(curid) + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <"+str(f[propp])+"> .\n")
                # elif urilist!=None and fieldcounter<len(urilist) and urilist[fieldcounter]!="":
                #   ttlstring+="<"+curid+"> <"+prop+"> <"+str(f[propp])+"> .\n"
                #    if first<10:
                #       ttlstring+="<"+prop+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty> .\n"
                #       ttlstring+="<"+prop+"> <http://www.w3.org/2000/01/rdf-schema#domain> <"+curclassid+"> .\n"
                #      if classurilist[fieldcounter]!="":
                #           ttlstring+="<"+prop+"> <http://www.w3.org/2000/01/rdf-schema#range> <"+classurilist[fieldcounter]+"> .\n"
                elif prop == "http://www.w3.org/2000/01/rdf-schema#label" or prop == "http://www.w3.org/2000/01/rdf-schema#comment" or (
                        proptypelist != None and proptypelist[fieldcounter] == "AnnotationProperty"):
                    ttlstring.add( "<" + curid + "> <" + prop + "> \"" + str(f[propp]).replace('"','\\"') + "\"^^<http://www.w3.org/2001/XMLSchema#string> .\n")
                    if first < 10:
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#AnnotationProperty> .\n")
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#domain> <" + curclassid + "> .\n")
                elif not f[propp] or f[propp] == None or f[propp] == "":
                    continue
                elif proptypelist != None and proptypelist[fieldcounter] == "SubClass":
                    ttlstring.add( "<" + curid + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <" + str(f[propp]) + "> .\n")
                    ttlstring.add( "<" + curid + "> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <" + curclassid + "> .\n")
                    if first < 10:
                        ttlstring.add( "<" + str(f[propp]) + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n")
                elif valuequeries != None and propp in valuequeries:
                    #ttlstring += ""
                    results=SPARQLUtils.executeQuery(valuequeries[propp][1],"".join(prefixes + valuequeries[propp][0].replace("%%" + propp + "%%","\"" + str(f[propp]) + "\"")))
                    ttlstring.add( "<" + curid + "> <" + prop + "> <" + results["results"]["bindings"][0]["item"]["value"] + "> .")
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
                            ttlstring.add( "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#range> <" + classurilist[fieldcounter] + "> .\n")
                elif "http" in str(f[propp]) or (
                        proptypelist != None and proptypelist[fieldcounter] == "ObjectProperty"):
                    ttlstring.add( "<" + curid + "> <" + prop + "> <" + str(f[propp]) + "> .\n")
                    if first < 10:
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty> .\n")
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#domain> <" + curclassid + "> .\n")
                        if classurilist != None and fieldcounter < len(classurilist) and classurilist[fieldcounter] != "":
                            ttlstring.add( "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#range> <" + classurilist[fieldcounter] + "> .\n")
                elif re.match(r'^-?\d+$', str(f[propp])):
                    ttlstring.add( "<" + curid + "> <" + prop + "> \"" + str(f[propp]) + "\"^^<http://www.w3.org/2001/XMLSchema#integer> .\n")
                    if first < 10:
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n")
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#domain> <" + curclassid + "> .\n")
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#range> <http://www.w3.org/2001/XMLSchema#integer> .\n")
                elif re.match(r'^-?\d+(?:\.\d+)?$', str(f[propp])):
                    ttlstring.add( "<" + curid + "> <" + prop + "> \"" + str(f[propp]) + "\"^^<http://www.w3.org/2001/XMLSchema#double> .\n")
                    if first:
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n")
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#domain> <" + curclassid + "> .\n")
                        ttlstring.add( "<" + prop + "> <http://www.w3.org/2000/01/rdf-schema#range> <http://www.w3.org/2001/XMLSchema#double> .\n")
                else:
                    ttlstring.add( "<" + curid + "> <" + prop + "> \"" + str(f[propp]).replace('"','\\"') + "\"^^<http://www.w3.org/2001/XMLSchema#string> .\n")
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
        result="<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        result+="<graphml xmlns=\"http://graphml.graphdrawing.org/xmlns\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:y=\"http://www.yworks.com/xml/graphml\" xsi:schemaLocation=\"http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd\">\n"
        result+="<key for=\"node\" id=\"nodekey\" yfiles.type=\"nodegraphics\"></key>\n<key for=\"edge\" id=\"edgekey\" yfiles.type=\"edgegraphics\"></key><graph id=\"G\" edgedefault=\"undirected\">\n"
        nodeset=set()
        edgeset=set()
        fidcounter=0
        edgecounter=0
        literalcounter=1
        nodeset.add(
            "<node id=\"geo:SpatialObject\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#ff8800\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" autoSizePolicy=\"content\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">geo:SpatialObject</y:NodeLabel></y:ShapeNode></data></node>\n")

        nodeset.add("<node id=\"geo:Feature\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#ff8800\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" autoSizePolicy=\"content\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">geo:Feature</y:NodeLabel></y:ShapeNode></data></node>\n")
        nodeset.add(
            "<node id=\"geo:Geometry\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#ff8800\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" autoSizePolicy=\"content\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">geo:Geometry</y:NodeLabel></y:ShapeNode></data></node>\n")
        edgeset.add("<edge id=\"eFeature\" source=\"geo:Feature\" target=\"geo:SpatialObject\">\n<data key=\"edgekey\">\n<y:PolyLineEdge>\n<y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hastext=\"true\" visible=\"true\" width=\"4.0\">" + str(
            "rdfs:subClassOf") + "</y:EdgeLabel>\n</y:PolyLineEdge>\n</data>\n</edge>\n")
        edgeset.add("<edge id=\"eGeometry\" source=\"geo:Geometry\" target=\"geo:SpatialObject\">\n<data key=\"edgekey\">\n<y:PolyLineEdge>\n<y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hastext=\"true\" visible=\"true\" width=\"4.0\">" + str(
            "rdfs:subClassOf") + "</y:EdgeLabel>\n</y:PolyLineEdge>\n</data>\n</edge>\n")
        for f in layer.getFeatures():
            geom = f.geometry()
            nodeset.add("<node id=\"fid_"+str(fidcounter)+"\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#800080\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" autoSizePolicy=\"content\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">fid_"+str(fidcounter)+"</y:NodeLabel></y:ShapeNode></data></node>\n")
            fieldcounter=0
            for propp in fieldnames:
                fieldcounter += 1
                prop = propp
                if prop.startswith("http"):
                    toadd="<node id=\"" + str(prop) + "\" uri=\""+str(prop)+"\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#800080\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" autoSizePolicy=\"content\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">"
                    if f[propp].startswith("http"):
                        toadd += SPARQLUtils.labelFromURI(str(f[propp]).replace("<", "").replace(">","")) + "</y:NodeLabel></y:ShapeNode></data></node>\n"
                    else:
                        toadd+="<!CDATA["+str(f[propp]).replace("<","").replace(">","")+"]]></y:NodeLabel></y:ShapeNode></data></node>\n"
                    nodeset.add(toadd)
                    edgeset.add("<edge id=\"e" + str(edgecounter)+"\" uri=\""+str(propp)+"\" source=\"fid_" + str(
                        fidcounter) + "\" target=\"" + str(prop) + "\"><data key=\"edgekey\"><y:PolyLineEdge><y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hastext=\"true\" visible=\"true\" width=\"4.0\">"+str(propp)+"</y:EdgeLabel>\n</y:PolyLineEdge>\n</data>\n</edge>\n")
                    edgecounter+=1
                else:
                    nodeset.add("<node id=\"literal" + str(literalcounter) + "\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#008000\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" autoSizePolicy=\"content\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">"+str(f[propp]).replace("<","").replace(">","")[0:10]+"</y:NodeLabel></y:ShapeNode></data></node>\n")
                    edgeset.add("<edge id=\"e" + str(edgecounter)+"\" uri=\""+str(propp)+"\" source=\"fid_" + str(
                        fidcounter) + "\" target=\"literal" + str(literalcounter) + "\">\n<data key=\"edgekey\">\n<y:PolyLineEdge>\n<y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hastext=\"true\" visible=\"true\" width=\"4.0\">"+str(propp)+"</y:EdgeLabel>\n</y:PolyLineEdge>\n</data>\n</edge>\n")
                    literalcounter+=1
                    edgecounter+=1
            nodeset.add("<node id=\"fid_" + str(fidcounter
                ) + "_geom\"><data key=\"nodekey\"><y:ShapeNode><y:Shape shape=\"ellipse\"></y:Shape><y:Fill color=\"#800080\" transparent=\"false\"></y:Fill><y:NodeLabel alignment=\"center\" autoSizePolicy=\"content\" fontSize=\"12\" fontStyle=\"plain\" hasText=\"true\" visible=\"true\" width=\"4.0\">fid_" + str(fidcounter) + "_geom</y:NodeLabel></y:ShapeNode></data></node>\n")
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
            edgecounter+=1
            edgeset.add("<edge id=\"e" + str(edgecounter) + "\" source=\"fid_" + str(
                fidcounter) + "\" target=\"geo:Feature\">\n<data key=\"edgekey\">\n<y:PolyLineEdge>\n<y:EdgeLabel alignment=\"center\" configuration=\"AutoFlippingLabel\" fontSize=\"12\" fontStyle=\"plain\" hastext=\"true\" visible=\"true\" width=\"4.0\">" + str(
                "rdf:type") + "</y:EdgeLabel>\n</y:PolyLineEdge>\n</data>\n</edge>\n")
            literalcounter += 1
            edgecounter+=1
            fidcounter+=1
        result+="".join(nodeset)
        result+="".join(edgeset)
        result+="</graph>\n"
        result+="</graphml>"
        return result


    ## Fetch the currently loaded layers.
    @staticmethod
    def loadLayerList(target):
        layers = QgsProject.instance().layerTreeRoot().children()
        if not isinstance(target, list):
            target=[target]
        for elem in target:
            elem.clear()
        for layer in layers:
            for elem in target:
                elem.addItem(layer.name())

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