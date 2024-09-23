from qgis.PyQt.QtCore import QVariant,QDateTime
from qgis.core import (
    QgsMessageLog
)
from osgeo import ogr
from qgis.core import QgsFeature, Qgis, QgsWkbTypes, QgsProject, QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform
import traceback
import json
from .sparqlutils import SPARQLUtils
from rdflib import Graph,URIRef, Literal
from rdflib.namespace import OWL, GEO, RDF,RDFS, SDO,XSD
from ..util.doc.docconfig import DocConfig



MESSAGE_CATEGORY = 'LayerUtils'

class LayerUtils:

    subclassThreshold=0.8

    typekeywords=["typ","type"]


    @staticmethod
    def dropUnwantedKeys(properties):
        properties.pop("item", None)
        properties.pop("geo", None)
        properties.pop("lat", None)
        properties.pop("lon", None)
        properties.pop("item2", None)
        properties.pop("rel", None)
        properties.pop("val", None)
        properties.pop("rel2", None)
        properties.pop("val2", None)
        return properties

    @staticmethod
    def addFeatureToCorrectCollection(feature,features,nongeofeatures,crsset):
        if feature["geometry"] is None:
            nongeofeatures.append(feature)
        else:
            features.append(feature)
        if feature is not None and "crs" in feature:
            crsset.add(feature["crs"])
            del feature["crs"]

    @staticmethod
    def queryResultToLayer(results, reproject, triplestoreconf, mandatoryvars, geooptional, shortenURIs):
        latval = "lat"
        lonval = "lon"
        features = []
        nongeofeatures = []
        properties = {}
        first = True
        newobject = True
        item = ""
        relval = False
        crsset = set()
        QgsMessageLog.logMessage('Processing results....',MESSAGE_CATEGORY, Qgis.Info)
        for result in results["results"]["bindings"]:
            if self.concept is not None and "item" not in result:
                result["item"] = {}
                result["item"]["value"] = self.concept
            if "item" in result and "rel" in result and "val" in result and "geo" in result and (
                    item == "" or result["item"]["value"] != item) and "geo" in mandatoryvars:
                relval = True
                if item != "":
                    self.addFeatureToCorrectCollection(LayerUtils.processLiteral(result["geo"]["value"], (
                        result["geo"]["datatype"] if "datatype" in result["geo"] else ""), reproject,
                                                                                 {'id': result["item"]["value"],
                                                                                  'type': 'Feature',
                                                                                  'properties': LayerUtils.dropUnwantedKeys(
                                                                                      properties),
                                                                                  'geometry': {}},
                                                                                 triplestoreconf), features,
                                                       nongeofeatures, crsset)
                properties = {}
                item = result["item"]["value"]
            if "item" in result and "rel" in result and "val" in result and "lat" in result and "lon" in result and (
                    item == "" or result["item"][
                "value"] != item) and "lat" in mandatoryvars and "lon" in mandatoryvars:
                relval = True
                if item != "":
                    self.addFeatureToCorrectCollection(LayerUtils.processLiteral(
                        "POINT(" + str(float(result[lonval]["value"])) + " " + str(
                            float(result[latval]["value"])) + ")", "wkt", reproject,
                        {'id': result["item"]["value"], 'type': 'Feature',
                         'properties': LayerUtils.dropUnwantedKeys(properties),
                         'geometry': {}}, triplestoreconf), features, nongeofeatures, crsset)
                properties = {}
                item = result["item"]["value"]
            if "item" in result and "rel" in result and "val" in result and geooptional and (
                    item == "" or result["item"]["value"] != item):
                relval = True
                if item != "":
                    self.addFeatureToCorrectCollection({'id': result["item"]["value"], 'type': 'Feature',
                                                        'properties': LayerUtils.dropUnwantedKeys(properties),
                                                        'geometry': {}}, features, nongeofeatures, crsset)
                properties = {}
                item = result["item"]["value"]
            if "rel" not in result and "val" not in result:
                properties = {}
            for var in results["head"]["vars"]:
                if var in result:
                    if var == "rel" and "val" in result:
                        if shortenURIs:
                            properties[SPARQLUtils.labelFromURI(result[var]["value"])] = result["val"]["value"]
                        elif shortenURIs == 1:
                            properties[SPARQLUtils.labelFromURI(result[var]["value"])] = SPARQLUtils.labelFromURI(
                                result["val"]["value"])
                        else:
                            properties[result[var]["value"]] = result["val"]["value"]
                    if var == "rel2" in result and "val2" != triplestoreconf[
                        "typeproperty"] and "val2" in result:
                        if shortenURIs:
                            properties["_" + SPARQLUtils.labelFromURI(result["rel2"]["value"])] = result["val2"][
                                "value"]
                        elif shortenURIs == 1:
                            properties[SPARQLUtils.labelFromURI(result[var]["value"])] = SPARQLUtils.labelFromURI(
                                result["val"]["value"])
                        else:
                            properties["_" + result[var]["value"]] = result["val2"]["value"]
                    elif var != "val" and var != "val2":
                        if shortenURIs:
                            properties[SPARQLUtils.labelFromURI(var)] = result[var]["value"]
                        elif shortenURIs == 1:
                            properties[SPARQLUtils.labelFromURI(result[var]["value"])] = SPARQLUtils.labelFromURI(
                                result["val"]["value"])
                        else:
                            properties[var] = result[var]["value"]
            if not "rel" in result and not "val" in result and "geo" in result:
                self.addFeatureToCorrectCollection(LayerUtils.processLiteral(result["geo"]["value"], (
                    result["geo"]["datatype"] if "datatype" in result["geo"] else ""), reproject,
                                                                             {'id': result["item"]["value"],
                                                                              'type': 'Feature',
                                                                              'properties': LayerUtils.dropUnwantedKeys(
                                                                                  properties), 'geometry': {}},
                                                                             triplestoreconf), features,
                                                   nongeofeatures, crsset)
            elif not "rel" in result and not "val" in result and latval in result and lonval in result:
                self.addFeatureToCorrectCollection(LayerUtils.processLiteral(
                    "POINT(" + str(float(result[lonval]["value"])) + " " + str(
                        float(result[latval]["value"])) + ")",
                    "wkt", reproject,
                    {'id': result["item"]["value"], 'type': 'Feature',
                     'properties': LayerUtils.dropUnwantedKeys(properties),
                     'geometry': {}},
                    triplestoreconf), features, nongeofeatures, crsset)
            elif not "rel" in result and not "val" in result and not "geo" in result and geooptional:
                self.addFeatureToCorrectCollection({'id': result["item"]["value"], 'type': 'Feature',
                                                    'properties': LayerUtils.dropUnwantedKeys(properties),
                                                    'geometry': {}}, features, nongeofeatures, crsset)
            # if relval and not geooptional and "lat" not in result and "lon" not in result:
            #    self.addFeatureToCorrectCollection(LayerUtils.processLiteral(result["geo"]["value"], (
            #        result["geo"]["datatype"] if "datatype" in result["geo"] else ""), reproject,
            #        { 'id':result["item"]["value"],'type': 'Feature', 'properties': self.dropUnwantedKeys(properties), 'geometry': {}},self.triplestoreconf),features,nongeofeatures,crsset)
        # if relval and geooptional:
        #    #myGeometryInstanceJSON = LayerUtils.processLiteral(result["geo"]["value"], (
        #    #    result["geo"]["datatype"] if "datatype" in result["geo"] else ""), reproject,self.triplestoreconf)
        #    feature = {'type': 'Feature', 'properties': self.dropUnwantedKeys(properties), 'geometry': {}}#json.loads(myGeometryInstanceJSON)}
        #    features.append(feature)
        # if len(features)==0:
        if "geo" in properties:
            self.addFeatureToCorrectCollection(LayerUtils.processLiteral(result["geo"]["value"], (
                result["geo"]["datatype"] if "datatype" in result["geo"] else ""), reproject,
                                                                         {'id': result["item"]["value"],
                                                                          'type': 'Feature',
                                                                          'properties': LayerUtils.dropUnwantedKeys(
                                                                              properties), 'geometry': {}},
                                                                         triplestoreconf), features,
                                               nongeofeatures, crsset)
        elif "lat" in properties and "lon" in properties:
            self.addFeatureToCorrectCollection(
                LayerUtils.processLiteral("POINT(" + str(float(result[lonval]["value"]))
                                          + " " + str(float(result[latval]["value"])) + ")",
                                          "wkt", reproject, {'id': result["item"]["value"], 'type': 'Feature',
                                                             'properties': LayerUtils.dropUnwantedKeys(properties),
                                                             'geometry': {}}, triplestoreconf), features,
                nongeofeatures, crsset)
        else:
            self.addFeatureToCorrectCollection(
                {'id': result["item"]["value"], 'type': 'Feature', 'properties': LayerUtils.dropUnwantedKeys(properties),
                 'geometry': {}}, features, nongeofeatures, crsset)
        QgsMessageLog.logMessage('Number of features ' + str(len(features)),
                                 MESSAGE_CATEGORY, Qgis.Info)
        if features == [] and len(results["results"]["bindings"]) == 0:
            return [None, None, None]
        # if features == [] and len(results["results"]["bindings"]) > 0:
        #    return len(results["results"]["bindings"])
        geojson = {'type': 'FeatureCollection', 'features': features}
        if len(nongeofeatures) > 0:
            geojsonnongeo = {'type': 'FeatureCollection', 'features': nongeofeatures}
        else:
            geojsonnongeo = None
        if len(crsset) > 0:
            return [geojson, geojsonnongeo, crsset.pop()]
        return [geojson, geojsonnongeo, None]

    @staticmethod
    def resolveGeoLiterals(pred, object, graph, geojsonrep, nonns, subject=None):
        if subject != None and isinstance(object, Literal) and (str(pred) in DocConfig.geopairproperties):
            pairprop = DocConfig.geopairproperties[str(pred)]["pair"]
            latorlong = DocConfig.geopairproperties[str(pred)]["islong"]
            othervalue = ""
            for obj in graph.objects(subject, URIRef(pairprop)):
                othervalue = str(obj)
            if latorlong:
                geojsonrep = {"type": "Point", "coordinates": [float(str(othervalue)), float(str(object))]}
            else:
                geojsonrep = {"type": "Point", "coordinates": [float(str(object)), float(str(othervalue))]}
        elif isinstance(object, Literal) and (
                str(pred) in DocConfig.geoproperties or str(object.datatype) in DocConfig.geoliteraltypes):
            geojsonrep = LayerUtils.processLiteral(str(object), str(object.datatype), "")
        elif isinstance(object, URIRef):
            for pobj in graph.predicate_objects(object):
                if isinstance(pobj[1], Literal) and (
                        str(pobj[0]) in DocConfig.geoproperties or str(
                    pobj[1].datatype) in DocConfig.geoliteraltypes):
                    geojsonrep = LayerUtils.processLiteral(str(pobj[1]), str(pobj[1].datatype), "")
        return geojsonrep

    @staticmethod
    def subGraphToLayer(graph,reproject, triplestoreconf, geooptional, shortenURIs):
        featcoll = {"type":"FeatureCollection","features":[]}
        nongeofeatures = []
        properties = {}
        for sub in graph.subjects(None,None,True):
            curfeat={"type":"Feature","properties":{},"geometry":{}}
            hasgeo=False
            for predobj in graph.predicate_objects(sub):
                if isinstance(predobj[1],Literal) or str(predobj[0]) in DocConfig.geoproperties:
                    curfeat["geometry"]=LayerUtils.resolveGeoLiterals(predobj[0],predobj[1],graph,{},False,sub)
                    #curfeat["geometry"]=LayerUtils.processLiteral(str(predobj[1]), (
                    #    predobj[1]["datatype"] if "datatype" in predobj[1] else ""), reproject,
                     #                                                            None,
                     #                                                            triplestoreconf)
                    print("geo")
                    hasgeo=True
                else:
                    if shortenURIs:
                        if isinstance(predobj[1],URIRef):
                            curfeat["properties"][SPARQLUtils.labelFromURI(str(predobj[0]))] = SPARQLUtils.labelFromURI(str(predobj[1]))
                        else:
                            curfeat["properties"][SPARQLUtils.labelFromURI(str(predobj[0]))] = str(predobj[1])
                    else:
                        curfeat["properties"][str(predobj[0])] = str(predobj[1])
            featcoll["features"].append(curfeat)
        return [featcoll,nongeofeatures,None]







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
    def findColumnNameProperties(layer,triplestoreconf,prefixes):
        names=layer.fields().names()
        columnprops=[]
        for name in names:
            if name.startswith("http:"):
                columnprops.append(name)
            elif ":" in name:
                splitted=name.split(":")
                if splitted[0] in prefixes:
                    columnprops.append(prefixes[splitted[0]]+splitted[1])
            else:
                columnprops.append("suni:"+name)
        return columnprops

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
        geom.transform(tr)
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
    def exportGeometryType(curid,geom,vocab,literaltype,init,graph):
        if "GeoSPARQL" in vocab:
            if init:
                graph.add((GEO.Feature,RDF.type,OWL.Class))
                graph.add((GEO.SpatialObject, RDF.type, OWL.Class))
                graph.add((GEO.Geometry, RDF.type, OWL.Class))
                graph.add((GEO.hasGeometry, RDF.type, OWL.ObjectProperty))
                graph.add((GEO.asWKT, RDF.type, OWL.DatatypeProperty))
                graph.add((GEO.Feature, RDFS.subClassOf, GEO.SpatialObject))
                graph.add((GEO.Geometry, RDFS.subClassOf, GEO.SpatialObject))
            graph.add((URIRef(str(curid)),GEO.hasGeometry,URIRef(str(curid) + "_geom")))
            graph.add((URIRef(str(curid) + "_geom"),RDF.type,URIRef("http://www.opengis.net/ont/sf#" + QgsWkbTypes.displayString(geom.wkbType()))))
            graph.add((URIRef("http://www.opengis.net/ont/sf#" + QgsWkbTypes.displayString(geom.wkbType())),RDF.type,OWL.Class))
            graph.add((URIRef("http://www.opengis.net/ont/sf#" + QgsWkbTypes.displayString(geom.wkbType())),RDFS.subClassOf,GEO.Geometry))
            if "WKT" in literaltype:
                graph.add((URIRef(str(curid) + "_geom"),GEO.asWKT,Literal(geom.asWkt(),datatype=GEO.wktLiteral)))
            if literaltype == "GeoJSON":
                graph.add((URIRef(str(curid) + "_geom"), URIRef("http://www.opengis.net/ont/geosparql#asGeoJSON"),
                          Literal(geom.asJson(),datatype="http://www.opengis.net/ont/geosparql#geoJSONLiteral")))
            if literaltype == "WKB":
                graph.add((URIRef(str(curid) + "_geom"), URIRef("http://www.opengis.net/ont/geosparql#asWKB"),
                          Literal(geom.asWkb(),datatype="http://www.opengis.net/ont/geosparql#wkbLiteral")))
        if "CIDOC" in vocab:
            if init:
                graph.add((GEO.Feature, RDF.type, OWL.Class))
                graph.add((URIRef("http://www.cidoc-crm.org/cidoc-crm/SP2_Phenomenal_Place"),RDFS.subClassOf,GEO.Feature))
                graph.add((GEO.SpatialObject, RDF.type, OWL.Class))
                graph.add((GEO.Geometry, RDF.type, OWL.Class))
                graph.add((URIRef("http://www.cidoc-crm.org/cidoc-crm/SP15_Geometry"),RDFS.subClassOf,GEO.Geometry))
                graph.add((URIRef("http://www.cidoc-crm.org/cidoc-crm/approximates"), RDF.type, OWL.ObjectProperty))
                graph.add((GEO.hasGeometry, RDF.type, OWL.ObjectProperty))
                graph.add((GEO.asWKT, RDF.type, OWL.DatatypeProperty))
                graph.add((GEO.Feature, RDFS.subClassOf, GEO.SpatialObject))
                graph.add((GEO.Geometry, RDFS.subClassOf, GEO.SpatialObject))
            graph.add(URIRef(str(curid)), GEO.hasGeometry, URIRef(str(curid) + "_geom"))
            graph.add((URIRef(str(curid) + "_geom"), RDF.type,
                      URIRef("http://www.opengis.net/ont/sf#" + QgsWkbTypes.displayString(geom.wkbType()))))
            graph.add((URIRef("http://www.opengis.net/ont/sf#" + QgsWkbTypes.displayString(geom.wkbType())), RDF.type,
                      OWL.Class))
            graph.add((URIRef("http://www.opengis.net/ont/sf#" + QgsWkbTypes.displayString(geom.wkbType())),
                      RDF.subClassOf, GEO.Geometry))
            if "WKT" in literaltype:
                graph.add((URIRef(str(curid) + "_geom"), GEO.asWKT, Literal(geom.asWkt(), datatype=GEO.wktLiteral)))
            if literaltype == "GeoJSON":
                graph.add((URIRef(str(curid) + "_geom"), URIRef("http://www.opengis.net/ont/geosparql#asGeoJSON"),
                          Literal(geom.asJson(), datatype="http://www.opengis.net/ont/geosparql#geoJSONLiteral")))
            if literaltype == "WKB":
                graph.add((URIRef(str(curid) + "_geom"), URIRef("http://www.opengis.net/ont/geosparql#asWKB"),
                          Literal(geom.asWkb(), datatype="http://www.opengis.net/ont/geosparql#wkbLiteral")))
        elif "Juso" in vocab:
            if init:
                graph.add((URIRef("http://rdfs.co/juso/Feature"),RDF.type,OWL.Class))
                graph.add((URIRef("http://rdfs.co/juso/SpatialThing"), RDF.type, OWL.Class))
                graph.add((URIRef("http://rdfs.co/juso/Geometry"), RDF.type, OWL.Class))
                graph.add((URIRef("http://rdfs.co/juso/geometry"), RDF.type, OWL.ObjectProperty))
                graph.add((URIRef("http://rdfs.co/juso/wgs84_lat"), RDF.type, OWL.DatatypeProperty))
                graph.add((URIRef("http://rdfs.co/juso/wgs84_long"), RDF.type, OWL.DatatypeProperty))
            graph.add((URIRef(str(curid)),URIRef("http://rdfs.co/juso/geometry"),URIRef(str(curid) + "_geom")))
            graph.add((URIRef(str(curid) + "_geom"),RDF.type,URIRef("http://www.opengis.net/ont/sf#" + QgsWkbTypes.displayString(geom.wkbType()))))
            graph.add((URIRef("http://www.opengis.net/ont/sf#" + QgsWkbTypes.displayString(geom.wkbType())),RDF.type,OWL.Class))
            graph.add((URIRef("http://www.opengis.net/ont/sf#" + QgsWkbTypes.displayString(geom.wkbType())),RDFS.subClassOf,GEO.Geometry))
            graph.add((URIRef(str(curid)), URIRef("http://rdfs.co/juso/wgs84_lat"), Literal(str(geom.centroid().vertexAt(0).x()),datatype=XSD.double)))
            graph.add((URIRef(str(curid)), URIRef("http://rdfs.co/juso/wgs84_long"),Literal(str(geom.centroid().vertexAt(0).y()), datatype=XSD.double)))
        elif "W3C" in vocab and "Geo" in vocab:
            if init:
                graph.add((URIRef("http://www.w3.org/2003/01/geo/wgs84_pos#lat"), RDF.type, OWL.DatatypeProperty))
                graph.add((URIRef("http://www.w3.org/2003/01/geo/wgs84_pos#long"), RDF.type, OWL.DatatypeProperty))
            graph.add((URIRef(str(curid)), URIRef("http://www.w3.org/2003/01/geo/wgs84_pos#lat"), Literal(str(geom.centroid().vertexAt(0).x()),datatype=XSD.double)))
            graph.add((URIRef(str(curid)), URIRef("http://www.w3.org/2003/01/geo/wgs84_pos#long"),Literal(str(geom.centroid().vertexAt(0).y()), datatype=XSD.double)))
        elif "Schema.org" in vocab:
            if init:
                graph.add((SDO.geo, RDF.type, OWL.ObjectProperty))
                graph.add((SDO.latitude, RDF.type, OWL.DatatypeProperty))
                graph.add((SDO.longitude, RDF.type, OWL.DatatypeProperty))
            graph.add((URIRef(str(curid)), SDO.geo, URIRef(str(curid) + "_geom")))
            graph.add((URIRef(str(curid) + "_geom"), SDO.latitude, Literal(str(geom.centroid().vertexAt(0).x()),datatype=XSD.double)))
            graph.add((URIRef(str(curid) + "_geom"), SDO.longitude, Literal(str(geom.centroid().vertexAt(0).y()), datatype=XSD.double)))
        elif "OSMRDF" in vocab:
            if init:
                graph.add((URIRef("https://www.openstreetmap.org/meta/loc"), RDF.type, OWL.DatatypeProperty))
            graph.add((URIRef(str(curid)),URIRef("https://www.openstreetmap.org/meta/loc"), Literal(geom.asWkt())))
        elif "NeoGeo" in vocab:
            if init:
                graph.add((URIRef("http://geovocab.org/spatial#Feature"), RDF.type, OWL.Class))
                graph.add((URIRef("http://geovocab.org/spatial#Geometry"), RDF.type, OWL.Class))
                graph.add((URIRef("http://geovocab.org/spatial#geometry"), RDF.type, OWL.ObjectProperty))
                graph.add((URIRef("http://geovocab.org/spatial#asWKT"), RDF.type, OWL.DatatypeProperty))
            graph.add((URIRef(str(curid)), URIRef("http://geovocab.org/geometry#geometry"), URIRef(str(curid) + "_geom")))
            graph.add((URIRef(str(curid)+"_geom"), RDF.type, URIRef("http://geovocab.org/geometry#" + QgsWkbTypes.displayString(geom.wkbType()))))
            graph.add((URIRef("http://geovocab.org/geometry#" + QgsWkbTypes.displayString(geom.wkbType())), RDF.type,OWL.Class))
            graph.add((URIRef(str(curid) + "_geom"), GEO.asWKT,Literal(geom.asWkt(),datatype=GEO.wktLiteral)))
        elif "OrdnanceUK" in vocab:
            if init:
                graph.add((URIRef("http://data.ordnancesurvey.co.uk/ontology/spatialrelations/easting"), RDF.type, OWL.DatatypeProperty))
                graph.add((URIRef("http://data.ordnancesurvey.co.uk/ontology/spatialrelations/northing"), RDF.type, OWL.DatatypeProperty))
            graph.add((URIRef(str(curid)),URIRef("http://data.ordnancesurvey.co.uk/ontology/spatialrelations/easting"), Literal(str(
                geom.centroid().vertexAt(0).x()),datatype=XSD.double)))
            graph.add((URIRef(str(curid)),URIRef("http://data.ordnancesurvey.co.uk/ontology/spatialrelations/northing"), Literal(str(
                geom.centroid().vertexAt(0).y()),datatype=XSD.double)))
        return graph
