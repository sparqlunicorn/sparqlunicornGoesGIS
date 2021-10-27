from time import sleep
from rdflib import *
import json
import requests
import urllib
from qgis.PyQt.QtCore import QSettings
from qgis.utils import iface
from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QListWidgetItem,QMessageBox,QProgressDialog, QFileDialog
from rdflib.plugins.sparql import prepareQuery
from SPARQLWrapper import SPARQLWrapper, JSON, POST, GET
from qgis.core import QgsProject,QgsGeometry,QgsVectorLayer,QgsExpression,QgsFeatureRequest,QgsCoordinateReferenceSystem,QgsCoordinateTransform,QgsApplication,QgsWkbTypes,QgsField
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
    )

MESSAGE_CATEGORY = 'ConvertCRSTask'

class ConvertCRSTask(QgsTask):
    """This shows how to subclass QgsTask"""

    def __init__(self, description,filename,crsdef,dialog,progress):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress=progress
        self.filename=filename
        self.crsdef=crsdef
        self.dialog=dialog
        s = QSettings() #getting proxy from qgis options settings
        self.proxyEnabled = s.value("proxy/proxyEnabled")
        self.proxyType = s.value("proxy/proxyType")
        self.proxyHost = s.value("proxy/proxyHost")
        self.proxyPort = s.value("proxy/proxyPort")
        self.proxyUser = s.value("proxy/proxyUser")
        self.proxyPassword = s.value("proxy/proxyPassword")

    def detectLiteralType(self,literal):
        try:
            geom=QgsGeometry.fromWkt(literal)
            return "wkt"
        except:
            print("no wkt")
        try:
            geom=QgsGeometry.fromWkb(bytes.fromhex(literal))
            return "wkb"
        except:
            print("no wkb")
        try:
            json.loads(literal)
            return "geojson"
        except:
            print("no geojson")
        return ""

    def processLiteral(self,literal,literaltype,reproject):
        QgsMessageLog.logMessage("Process literal: "+str(literal)+" "+str(literaltype))
        geom=None
        if literaltype=="" or literaltype==None:
            literaltype=self.detectLiteralType(literal)
        if "wkt" in literaltype.lower():
            literal=literal.strip()
            if literal.startswith("<http"):
                index=literal.index(">")+1
                slashindex=literal.rfind("/")+1
                reproject=literal[slashindex:(index-1)]
                geom=QgsGeometry.fromWkt(literal[index:])
            else:
                geom=QgsGeometry.fromWkt(literal)
        #elif "gml" in literaltype.lower():
        #    geom=QgsGeometry.fromWkb(ogr.CreateGeometryFromGML(literal).ExportToWkb())
        elif "geojson" in literaltype.lower():
            return literal
        elif "wkb" in literaltype.lower():
            geom=QgsGeometry.fromWkb(bytes.fromhex(literal))
        if geom!=None and reproject!="":
            sourceCrs = QgsCoordinateReferenceSystem(reproject)
            destCrs = QgsCoordinateReferenceSystem(4326)
            tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
            geom.transform(tr)
        if geom!=None:
            return geom.asJson()
        return None

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(
                                     self.description()),
                                 MESSAGE_CATEGORY, Qgis.Info)
        if self.proxyHost!=None and self.proxyHost!="" and self.proxyPort!=None and self.proxyPort!="":
            QgsMessageLog.logMessage('Proxy? '+str(self.proxyHost), MESSAGE_CATEGORY, Qgis.Info)
            proxy = urllib.request.ProxyHandler({'http': self.proxyHost})
            opener = urllib.request.build_opener(proxy)
            urllib.request.install_opener(opener)
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()),MESSAGE_CATEGORY, Qgis.Info)
        self.graph = Graph()
        try:
            if self.filename.startswith("http"):
                self.graph.load(self.filename)
            else:
                filepath=self.filename.split(".")
                result = self.graph.parse(self.filename, format=filepath[len(filepath)-1])
        except Exception as e:
            QgsMessageLog.logMessage('Failed "{}"'.format(self.description()),MESSAGE_CATEGORY, Qgis.Info)
            self.exception=str(e)
            return False
        self.geoconcepts=[]
        if self.graph!=None:
            print("WE HAVE A GRAPH")
            for s, p, o in self.graph:
                if isinstance(o,Literal):
                    QgsMessageLog.logMessage('BEFORE "{}"'.format(o)+" - "+str(o.datatype),MESSAGE_CATEGORY, Qgis.Info)
                    self.graph.remove((s,p,o))
                    self.graph.add((s,p,Literal(self.processLiteral(o,o.datatype,""),datatype=o.datatype)))
                    QgsMessageLog.logMessage('AFTER "{}"'.format(o)+" - "+str(o.datatype),MESSAGE_CATEGORY, Qgis.Info)
        return True

    ## Processes query results and reformats them to a QGIS layer.
    #  @param self The object pointer.
    #  @param results The query results
    #  @param reproject The crs from which to reproject to WGS84
    #  @param mandatoryvars mandatoryvariables to find in the query result
    #  @param geooptional indicates if a geometry is mandatory
    def processResults(self,results,reproject,mandatoryvars,geooptional):
        latval=mandatoryvars[0]
        lonval=""
        if len(mandatoryvars)>1:
            lonval=mandatoryvars[1]
        features = []
        first=True
        newobject=True
        item=""
        for result in results["results"]["bindings"]:
            if "item" in result and "rel" in result and "val" in result and (item=="" or result["item"]["value"]!=item) and "geo" in mandatoryvars:
                if item!="":
                    myGeometryInstanceJSON=self.processLiteral(result["geo"]["value"],"wkt",reproject)
                    feature = { 'type': 'Feature', 'properties': properties, 'geometry':  json.loads(myGeometryInstanceJSON) }
                    features.append(feature)
                properties = {}
                item=result["item"]["value"]
            if "item" in result and "rel" in result and "val" in result and "lat" in result and "lon" in result and (item=="" or result["item"]["value"]!=item) and "lat" in mandatoryvars and "lon" in mandatoryvars:
                if item!="":
                    myGeometryInstanceJSON=self.processLiteral("POINT("+str(float(result[lonval]["value"]))+" "+str(float(result[latval]["value"]))+")","wkt",reproject)
                    feature = { 'type': 'Feature', 'properties': properties, 'geometry':  json.loads(myGeometryInstanceJSON) }
                    features.append(feature)
                properties = {}
                item=result["item"]["value"]
            #if not "rel" in result and not "val" in result:
            properties = {}
            for var in results["head"]["vars"]:
                if var in result:
                    if var=="rel" and "val" in result:
                        properties[result[var]["value"]] = result["val"]["value"]
                    elif var!="val":
                        properties[var] = result[var]["value"]
            if not "rel" in result and not "val" in result and "geo" in result:
                myGeometryInstanceJSON=self.processLiteral(result["geo"]["value"],"wkt",reproject)
                feature = { 'type': 'Feature', 'properties': properties, 'geometry':  json.loads(myGeometryInstanceJSON) }
                features.append(feature)
            elif not "rel" in result and not "val" in result and latval in result and lonval in result and reproject==27700:
                myGeometryInstanceJSON=self.processLiteral("POINT("+str(float(result[latval]["value"]))+" "+str(float(result[lonval]["value"]))+")","wkt",reproject)
                feature = { 'type': 'Feature', 'properties': properties, 'geometry':  json.loads(myGeometryInstanceJSON) }
                features.append(feature)
            elif not "rel" in result and not "val" in result and latval in result and lonval in result and reproject!=27700:
                myGeometryInstanceJSON=self.processLiteral("POINT("+str(float(result[lonval]["value"]))+" "+str(float(result[latval]["value"]))+")","wkt",reproject)
                feature = { 'type': 'Feature', 'properties': properties, 'geometry':  json.loads(myGeometryInstanceJSON) }
                features.append(feature)
            elif not "rel" in result and not "val" in result and not "geo" in result and geooptional:
                feature = { 'type': 'Feature', 'properties': properties, 'geometry':  {} }
                features.append(feature)
        if "rel" in results["results"]["bindings"] and "val" in results["results"]["bindings"]:
            myGeometryInstanceJSON=self.processLiteral(result["geo"]["value"],"wkt",reproject)
            feature = { 'type': 'Feature', 'properties': properties, 'geometry':  json.loads(myGeometryInstanceJSON) }
            features.append(feature)		
        if features==[] and len(results["results"]["bindings"])==0:
            return None
        if features==[] and len(results["results"]["bindings"])>0:
            return len(results["results"]["bindings"])
        geojson = {'type': 'FeatureCollection', 'features': features }
        return geojson


    def finished(self, result):
        self.progress.close()
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self.dialog,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.ttl)", options=options)
        if fileName:
            fo = open(fileName, "w")
            fo.write(self.graph.serialize(format="turtle").decode())
            fo.close()
        iface.messageBar().pushMessage("Save converted file", "OK", level=Qgis.Success)

 
