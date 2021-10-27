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

    supportedLiteralTypes={"http://www.opengis.net/ont/geosparql#wktLiteral"}

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

    def processLiteral(self,literal,literaltype,reproject,projectto):
        QgsMessageLog.logMessage("Process literal: "+str(literal)+" "+str(literaltype)+" "+str(reproject))
        QgsMessageLog.logMessage("REPROJECT: "+str(reproject))
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
                reproject="CRS84"
                geom=QgsGeometry.fromWkt(literal)
        #elif "gml" in literaltype.lower():
        #    geom=QgsGeometry.fromWkb(ogr.CreateGeometryFromGML(literal).ExportToWkb())
        elif "wkb" in literaltype.lower():
            geom=QgsGeometry.fromWkb(bytes.fromhex(literal))
        if geom!=None and projectto!=None:
            if reproject!="CRS84":
                sourceCrs = QgsCoordinateReferenceSystem("EPSG:"+str(reproject))
            else:
                sourceCrs = QgsCoordinateReferenceSystem("CRS:84")
            destCrs = QgsCoordinateReferenceSystem(projectto)
            QgsMessageLog.logMessage('PROJECTIT '+str(sourceCrs.description())+" "+str(projectto.description()),MESSAGE_CATEGORY, Qgis.Info)
            tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
            geom.transform(tr)
        if geom!=None and "wkt" in literaltype.lower():
            return "<http://www.opengis.net/def/crs/EPSG/0/"+str(str(projectto.authid())[str(projectto.authid()).rfind(':')+1:])+"> "+geom.asWkt()
        if geom!=None and "wkb" in literaltype.lower():
            return geom.asWkb()
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
                QgsMessageLog.logMessage('BEFORE "{}"'.format(o),MESSAGE_CATEGORY, Qgis.Info)
                if isinstance(o,Literal):
                    QgsMessageLog.logMessage('ISLITERAL "{}"'.format(o)+" - "+str(o.datatype),MESSAGE_CATEGORY, Qgis.Info)
                    QgsMessageLog.logMessage(str(o.datatype),MESSAGE_CATEGORY, Qgis.Info)
                    if str(o.datatype) in self.supportedLiteralTypes:
                        QgsMessageLog.logMessage('ISGEOLITERAL "{}"'.format(self.graph),MESSAGE_CATEGORY, Qgis.Info)
                        newliteral=Literal(self.processLiteral(o,o.datatype,"",self.crsdef),datatype=o.datatype)
                        self.graph.set((s,p,newliteral))
                        QgsMessageLog.logMessage('AFTER "{}"'.format(newliteral)+" - "+str(newliteral.datatype),MESSAGE_CATEGORY, Qgis.Info)
        return True

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
        self.dialog.close()

 
