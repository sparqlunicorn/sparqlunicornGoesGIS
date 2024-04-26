from qgis.PyQt.QtCore import QVariant,QDateTime
from qgis.core import (
    QgsMessageLog
)
from osgeo import ogr
from qgis.core import QgsFeature, Qgis, QgsWkbTypes, QgsProject, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
import traceback
import json
from .sparqlutils import SPARQLUtils

MESSAGE_CATEGORY = 'LayerUtils'

class LayerUtils:

    subclassThreshold=0.8

    typekeywords=["typ","type"]

    ## Detects the type of a column which is to be entered into a QGIS vector layer.
    #  @param self The object pointer.
    #  @param table the layer to analyze
    # the column to consider
    @staticmethod
    def detectColumnType(resultmap,columnname=""):
        intcount = 0
        doublecount = 0
        datecount=0
        uricount=0
        stringcount=0
        tokencount=0
        uniquestrings=set()
        #QgsMessageLog.logMessage(str(resultmap), MESSAGE_CATEGORY, Qgis.Info)
        for res in resultmap:
            #QgsMessageLog.logMessage(str(resultmap[res]), MESSAGE_CATEGORY, Qgis.Info)
            if resultmap[res] is None or resultmap[res] == "":
                intcount += 1
                doublecount += 1
                continue
            uniquestrings.add(str(resultmap[res]))
            tokencount+=1
            if isinstance(resultmap[res],QDateTime):
                datecount+=1
                continue
            if str(resultmap[res]).isdigit():
                intcount += 1
                continue
            try:
                float(resultmap[res])
                doublecount += 1
                continue
            except:
                print("")
            if str(resultmap[res]).startswith("http"):
                uricount+=1
                continue
            stringcount+=1
        #QgsMessageLog.logMessage(str(stringcount) + " - " + str(len(uniquestrings)) + " - " + str(len(resultmap)),MESSAGE_CATEGORY, Qgis.Info)
        #QgsMessageLog.logMessage(str(intcount) + " - " + str(doublecount) + " - " + str(len(resultmap)),MESSAGE_CATEGORY, Qgis.Info)
        if intcount == len(resultmap):
            return {"type": QVariant.Int, "xsdtype": "xsd:integer", "unique": (tokencount == len(uniquestrings)),"category":False}
        if doublecount == len(resultmap):
            return {"type": QVariant.Double, "xsdtype": "xsd:double", "unique": (tokencount == len(uniquestrings)),"category":False}
        if datecount == len(resultmap):
            return {"type": "xsd:date", "xsdtype": "xsd:date", "unique": (tokencount == len(uniquestrings)),"category":False}
        if uricount == len(resultmap):
           return {"type": "xsd:anyURI", "xsdtype": "xsd:anyURI", "unique": (tokencount == len(uniquestrings)),"category":False}
        return {"type":QVariant.String,"xsdtype":"xsd:string","unique":(stringcount==len(uniquestrings)),"category":(stringcount <= len(uniquestrings))}

    @staticmethod
    def detectLayerColumnType(layer,columnindex):
        features = layer.getFeatures()
        columnmap={}
        counter=0
        for feat in features:
            attrs = feat.attributes()
            #QgsMessageLog.logMessage(str(attrs[0]), MESSAGE_CATEGORY, Qgis.Info)
            columnmap[counter]=attrs[columnindex]
            counter+=1
        return LayerUtils.detectColumnType(columnmap,layer.fields().names()[columnindex])

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
    def findColumnNameProperties(layer,triplestoreconf):
        names=layer.fields().names()


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
    def reprojectGeometry(geom,fromcrs,tocrs="EPSG:4326"):
        sourceCrs = QgsCoordinateReferenceSystem(fromcrs)
        destCrs = QgsCoordinateReferenceSystem.fromOgcWmsCrs(tocrs)
        tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
        #QgsMessageLog.logMessage("FIELDNAMES: " + str(geom.asJson()),
        #                         MESSAGE_CATEGORY, Qgis.Info)
        res=geom.transform(tr)
        #QgsMessageLog.logMessage("FIELDNAMES: " + str(geom.asJson()),
        #                         MESSAGE_CATEGORY, Qgis.Info)
        return geom

    @staticmethod
    def processLiteral(literal, literaltype, reproject, currentlayergeojson=None,triplestoreconf=None, reprojecttask=False):
        geom = None
        if triplestoreconf is not None and "literaltype" in triplestoreconf:
            literaltype = triplestoreconf["literaltype"]
        try:
            if literal.startswith("http"):
                res = SPARQLUtils.handleURILiteral(literal,currentlayergeojson)
                if res is None:
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
                    if reprojecttask:
                        reproject = literal[slashindex:(index - 1)]
                    geom = QgsGeometry.fromWkt(literal[index:])
                    curcrs=literal[slashindex:(index - 1)]
                else:
                    geom = QgsGeometry.fromWkt(literal)
            elif "gml" in literaltype.lower():
                curcrs=None
                if "EPSG" in literal and "http" in literal:
                    srspart=literal[literal.find("srsName="):literal.find(">")]
                    curcrs=srspart.replace("srsName=\"http://www.opengis.net/def/crs/EPSG/0/","")
                    curcrs=curcrs.replace("\"","")
                elif "EPSG" in literal and "http" not in literal:
                    srspart = literal[literal.find("srsName="):literal.find(">")]
                    curcrs=srspart.replace("srsName=\"EPSG:","")
                    curcrs=curcrs.replace("\"", "")
                if reprojecttask and curcrs is not None:
                    reproject = str(curcrs)
                geom=QgsGeometry.fromWkt(ogr.CreateGeometryFromGML(literal).ExportToWkt())
                geom=QgsGeometry(geom)
            elif "geojson" in literaltype.lower():
                return literal
            elif "wkb" in literaltype.lower():
                geom = QgsGeometry.fromWkb(bytes.fromhex(literal))
            if geom is not None and reproject != "":
                geom=LayerUtils.reprojectGeometry(geom,reproject)
            if geom is not None:
                res=json.loads(geom.asJson())
                if currentlayergeojson is not None:
                    currentlayergeojson["geometry"]=res
                    if curcrs is not None:
                        currentlayergeojson["crs"]=curcrs
                    return currentlayergeojson
                if curcrs is not None:
                    res["crs"]=curcrs
                return res
        except Exception as e:
            print("Literal: " + str(literal) + " " + str(literaltype))
            print(e)
            print(traceback.format_exc())
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
            ttlstring.add("<" + str(curid) + "> <http://www.opengis.net/ont/geosparql#hasGeometry> <" + str(curid) + "_geom> .\n")
            ttlstring.add("<" + str(curid) + "_geom> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.opengis.net/ont/geosparql#" + QgsWkbTypes.displayString(
                geom.wkbType()) + "> .\n")
            ttlstring.add("<http://www.opengis.net/ont/geosparql#" + QgsWkbTypes.displayString(
                geom.wkbType()) + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n")
            ttlstring.add("<http://www.opengis.net/ont/geosparql#" + QgsWkbTypes.displayString(
                geom.wkbType()) + "> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://www.opengis.net/ont/geosparql#Geometry> .\n")
            if "WKT" in literaltype:
                ttlstring.add("<" + str(curid) + "_geom> <http://www.opengis.net/ont/geosparql#asWKT> \"" + geom.asWkt() + "\"^^<http://www.opengis.net/ont/geosparql#wktLiteral> .\n")
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
            ttlstring.add("<" + str(curid) + "> <http://www.w3.org/2003/01/geo/wgs84_pos#lat> \""+str(geom.centroid().vertexAt(0).x())+"\"^^<http://www.w3.org/2001/XMLSchema#double> .\n")
            ttlstring.add("<" + str(curid) + "> <http://www.w3.org/2003/01/geo/wgs84_pos#long> \""+str(geom.centroid().vertexAt(0).y())+"\"^^<http://www.w3.org/2001/XMLSchema#double> .\n")
        elif "Schema.org" in vocab:
            if init:
                ttlstring.add(
                    "<http://schema.org/geo> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty> .\n")
                ttlstring.add(
                    "<http://schema.org/latitude> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n")
                ttlstring.add(
                    "<http://schema.org/longitude> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#DatatypeProperty> .\n")
            ttlstring.add("<" + str(
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
            ttlstring.add("<" + str(curid) + "> <http://geovocab.org/geometry#geometry> <" + str(curid) + "_geom> .\n")
            ttlstring.add("<" + str(curid) + "_geom> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://geovocab.org/geometry#" + QgsWkbTypes.displayString(
                geom.wkbType()) + "> .\n")
            ttlstring.add("<http://geovocab.org/geometry#" + QgsWkbTypes.displayString(
                geom.wkbType()) + "> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n")
            ttlstring.add("<http://geovocab.org/geometry#" + QgsWkbTypes.displayString(
                geom.wkbType()) + "> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://geovocab.org/geometry#Geometry> .\n")
            ttlstring.add("<" + str(curid) + "_geom> <http://geovocab.org/geometry#asWKT> \"" + geom.asWkt() + "\"^^<http://www.opengis.net/ont/geosparql#wktLiteral> .\n")
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
