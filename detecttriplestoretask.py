from time import sleep
from rdflib import *
import json
import requests
import urllib
import sys
from qgis.PyQt.QtCore import QSettings
from qgis.utils import iface
from qgis.core import Qgis,QgsApplication
from qgis.PyQt.QtWidgets import QListWidgetItem,QMessageBox,QProgressDialog
from rdflib.plugins.sparql import prepareQuery
from SPARQLWrapper import SPARQLWrapper, JSON, POST, GET
from qgis.core import QgsProject,QgsGeometry,QgsVectorLayer,QgsExpression,QgsFeatureRequest,QgsCoordinateReferenceSystem,QgsCoordinateTransform,QgsApplication,QgsWkbTypes,QgsField
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
    )

MESSAGE_CATEGORY = 'DetectTripleStoreTask'

class DetectTripleStoreTask(QgsTask):
    """This shows how to subclass QgsTask"""

    def __init__(self, description, triplestoreconf,endpoint,triplestorename, testURL, testConfiguration,prefixes,prefixstore,tripleStoreChooser,comboBox,permanentAdd,parentdialog,progress):
        super().__init__(description, QgsTask.CanCancel)
        self.description=description
        self.exception = None
        self.prefixes=prefixes
        self.prefixstore=prefixstore
        self.permanentAdd=permanentAdd
        self.progress=progress
        self.triplestorename=triplestorename
        self.tripleStoreChooser=tripleStoreChooser
        self.comboBox=comboBox
        self.parentdialog=parentdialog
        self.triplestoreurl=endpoint
        self.triplestoreconf=triplestoreconf
        self.testURL=testURL
        self.configuration={}
        self.testConfiguration=testConfiguration
        self.message=""
        self.feasibleConfiguration=False
        s = QSettings() #getting proxy from qgis options settings
        self.proxyEnabled = s.value("proxy/proxyEnabled")
        self.proxyType = s.value("proxy/proxyType")
        self.proxyHost = s.value("proxy/proxyHost")
        self.proxyPort = s.value("proxy/proxyPort")
        self.proxyUser = s.value("proxy/proxyUser")
        self.proxyPassword = s.value("proxy/proxyPassword")

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description),MESSAGE_CATEGORY, Qgis.Info)
        if self.testURL and not self.testConfiguration:
            self.testTripleStoreConnection()
            return True
        if self.testConfiguration and not self.testURL:
            res=self.detectTripleStoreConfiguration()
        return True

    def testTripleStoreConnection(self,query="SELECT ?a ?b ?c WHERE { ?a ?b ?c .} LIMIT 1"):	
        if self.proxyHost!=None and self.ProxyPort!=None:
            proxy = urllib.ProxyHandler({'http': proxyHost})
            opener = urllib.build_opener(proxy)
            urllib.install_opener(opener)
        sparql = SPARQLWrapper(self.triplestoreurl, agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")	
        sparql.setQuery(query)	
        sparql.setReturnFormat(JSON)	
        print("now sending query")	
        try:	
            results = sparql.query().convert()	
            if self.testURL and not self.testConfiguration:
                self.message="URL depicts a valid SPARQL Endpoint!"
            if "ASK" in query:
                return results["boolean"]
            self.feasibleConfiguration=True
            return True	
        except:	
            self.message="URL does not depict a valid SPARQL Endpoint!"
            self.feasibleConfiguration=False
            return False
			
    def detectNamespaces(self,subpredobj):	
        if subpredobj<0 or subpredobj==None:
            query="select distinct ?ns where { ?s ?p ?o . bind( replace( str(?s), \"(#|/)[^#/]*$\", \"$1\" ) as ?ns )} limit 10"
        elif subpredobj==0:
            query="select distinct ?ns where { ?s ?p ?o . bind( replace( str(?p), \"(#|/)[^#/]*$\", \"$1\" ) as ?ns )} limit 10"
        else:
            query="select distinct ?ns where { ?s ?p ?o . bind( replace( str(?o), \"(#|/)[^#/]*$\", \"$1\" ) as ?ns )} limit 10"
        if self.proxyHost!=None and self.ProxyPort!=None:
            proxy = urllib.ProxyHandler({'http': proxyHost})
            opener = urllib.build_opener(proxy)
            urllib.install_opener(opener)
        sparql = SPARQLWrapper(self.triplestoreurl, agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")	
        sparql.setQuery(query)	
        sparql.setReturnFormat(JSON)	
        print("now sending query")	
        try:	
            results = sparql.query().convert()
            reslist=[]
            for nss in results["results"]["bindings"]:
                if "ns" in nss:
                    reslist.append(nss["ns"]["value"])
            return reslist
        except:	
            return []


    ## Detects default configurations of common geospatial triple stores.
    #  @param self The object pointer.
    def detectTripleStoreConfiguration(self):	
        self.configuration={}
        self.configuration["name"]=self.triplestorename
        self.configuration["endpoint"]=self.triplestoreurl
        self.configuration["geoconceptlimit"]=500
        self.configuration["crs"]=4326
        self.configuration["staticconcepts"]=[]
        self.configuration["active"]=True
        self.configuration["prefixes"]={"owl": "http://www.w3.org/2002/07/owl#","rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdfs": "http://www.w3.org/2000/01/rdf-schema#","geosparql": "http://www.opengis.net/ont/geosparql#","wgs84_pos": "http://www.w3.org/2003/01/geo/wgs84_pos#"}
        testQueries={"geosparql":"PREFIX geof:<http://www.opengis.net/def/function/geosparql/> SELECT ?a ?b ?c WHERE { BIND( \"POINT(1 1)\"^^<http://www.opengis.net/ont/geosparql#wktLiteral> AS ?a) BIND( \"POINT(1 1)\"^^<http://www.opengis.net/ont/geosparql#wktLiteral> AS ?b) FILTER(geof:sfIntersects(?a,?b))}","available":"SELECT ?a ?b ?c WHERE { ?a ?b ?c .} LIMIT 1","hasRDFSLabel":"PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> ASK { ?a rdfs:label ?c . }","hasRDFType":"PREFIX rdf:<http:/www.w3.org/1999/02/22-rdf-syntax-ns#> ASK { ?a <http:/www.w3.org/1999/02/22-rdf-syntax-ns#type> ?c . }","hasWKT":"PREFIX geosparql:<http://www.opengis.net/ont/geosparql#> ASK { ?a geosparql:asWKT ?c .}","hasGML":"PREFIX geosparql:<http://www.opengis.net/ont/geosparql#> ASK { ?a geosparql:asGML ?c .}","hasGeoJSON":"PREFIX geosparql:<http://www.opengis.net/ont/geosparql#> ASK { ?a geosparql:asGeoJSON ?c .}","hasLatLon":"PREFIX geo:<http://www.w3.org/2003/01/geo/wgs84_pos#> ASK { ?a geo:lat ?c . ?a geo:long ?d . }","namespaceQuery":"select distinct ?ns where {  ?s ?p ?o . bind( replace( str(?s), \"(#|/)[^#/]*$\", \"$1\" ) as ?ns )} limit 10"}
        if self.testTripleStoreConnection(testQueries["available"]):
            if self.testTripleStoreConnection(testQueries["hasWKT"]):
                if self.testTripleStoreConnection(testQueries["geosparql"]):
                    self.configuration["bboxquery"]={}
                    self.configuration["bboxquery"]["type"]="geosparql"
                    self.configuration["bboxquery"]["query"]="FILTER(<http://www.opengis.net/def/function/geosparql/sfIntersects>(?geo,\"POLYGON((%%x1%% %%y1%%, %%x1%% %%y2%%, %%x2%% %%y2%%, %%x2%% %%y1%%, %%x1%% %%y1%%))\"^^<http://www.opengis.net/ont/geosparql#wktLiteral>))"
                    self.message="URL depicts a valid GeoSPARQL Endpoint and contains WKT Literals!\nWould you like to add this SPARQL endpoint?"
                else:
                    self.message="URL depicts a valid SPARQL Endpoint and contains WKT Literals!\nWould you like to add this SPARQL endpoint?"
                self.configuration["mandatoryvariables"]=["item","geo"]	
                self.configuration["querytemplate"]=[]
                self.configuration["querytemplate"].append({"label":"10 Random Geometries","query": "SELECT ?item ?geo WHERE {\n ?item <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <%%concept%%>.\n ?item <http://www.opengis.net/ont/geosparql#hasGeometry> ?geom_obj .\n ?geom_obj <http://www.opengis.net/ont/geosparql#asWKT> ?geo .\n } LIMIT 10"})	
                self.configuration["geoconceptquery"]="SELECT DISTINCT ?class WHERE { ?a <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?class . ?a <http://www.opengis.net/ont/geosparql#hasGeometry> ?a_geom . ?a_geom <http://www.opengis.net/ont/geosparql#asWKT> ?wkt .}"
                res=set(self.detectNamespaces(-1)+self.detectNamespaces(0)+self.detectNamespaces(1))
                i=0
                for ns in res:
                    if ns!="http://" and ns.startswith("http://"):
                        if ns in self.prefixstore["reversed"]:
                            self.configuration["prefixes"][self.prefixstore["reversed"][ns]]=ns
                        else:
                            self.configuration["prefixes"]["ns"+str(i)]=ns
                            i=i+1
                self.feasibleConfiguration=True
            elif self.testTripleStoreConnection(testQueries["hasLatLon"]):
                self.message="URL depicts a valid SPARQL Endpoint and contains Lat/long!\nWould you like to add this SPARQL endpoint?"
                self.configuration["mandatoryvariables"]=["item","lat", "lon"]	
                self.configuration["querytemplate"]=[]			
                self.configuration["querytemplate"].append({"label":"10 Random Geometries","query": "SELECT ?item ?lat ?lon WHERE {\n ?item <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n ?item <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?lat .\n ?item <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?lon .\n } LIMIT 10"})								
                self.configuration["geoconceptquery"]="SELECT DISTINCT ?class WHERE { ?a <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?class . ?a <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?lat . ?a <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?lon .}"
                res=set(self.detectNamespaces(-1)+self.detectNamespaces(0)+self.detectNamespaces(1))
                i=0
                for ns in res:
                    if ns!="http://" and ns.startswith("http://"):
                        if ns in self.prefixstore["reversed"]:
                            self.configuration["prefixes"][self.prefixstore["reversed"][ns]]=ns
                        else:
                            self.configuration["prefixes"]["ns"+str(i)]=ns
                            i=i+1
                self.feasibleConfiguration=True
            elif self.testTripleStoreConnection(testQueries["hasGeoJSON"]):
                if self.testTripleStoreConnection(testQueries["geosparql"]):
                    self.configuration["bboxquery"]={}
                    self.configuration["bboxquery"]["type"]="geosparql"
                    self.configuration["bboxquery"]["query"]="FILTER(<http://www.opengis.net/def/function/geosparql/sfIntersects>(?geo,\"POLYGON((%%x1%% %%y1%%, %%x1%% %%y2%%, %%x2%% %%y2%%, %%x2%% %%y1%%, %%x1%% %%y1%%))\"^^<http://www.opengis.net/ont/geosparql#wktLiteral>))"
                    self.message="URL depicts a valid GeoSPARQL Endpoint and contains GeoJSON Literals!\nWould you like to add this SPARQL endpoint?"
                else:
                    self.message="URL depicts a valid SPARQL Endpoint and contains GeoJSON Literals!\nWould you like to add this SPARQL endpoint?"
                self.configuration["mandatoryvariables"]=["item","geo"]	
                self.configuration["querytemplate"]=[]
                self.configuration["querytemplate"].append({"label":"10 Random Geometries","query": "SELECT ?item ?geo WHERE {\n ?item a <%%concept%%>.\n ?item <http://www.opengis.net/ont/geosparql#hasGeometry> ?geom_obj .\n ?geom_obj <http://www.opengis.net/ont/geosparql#asGeoJSON> ?geo .\n } LIMIT 10"})	
                self.configuration["querytemplate"].append({"label":"10 Random Geometries (All Attributes","query": "SELECT DISTINCT ?item ?rel ?val ?geo WHERE {\n ?item rdf:type <%%concept%%> .\n ?item ?rel ?val . \n ?val <http://www.opengis.net/ont/geosparql#asGeoJSON> ?geo .\n}\n LIMIT 100"})	
                self.configuration["geoconceptquery"]="SELECT DISTINCT ?class WHERE { ?a <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?class . ?a ?rel ?a_geom . ?a_geom <http://www.opengis.net/ont/geosparql#asGeoJSON> ?wkt .}"
                res=set(self.detectNamespaces(-1)+self.detectNamespaces(0)+self.detectNamespaces(1))
                i=0
                for ns in res:
                    if ns!="http://" and ns.startswith("http://"):
                        if ns in self.prefixstore["reversed"]:
                            self.configuration["prefixes"][self.prefixstore["reversed"][ns]]=ns
                        else:
                            self.configuration["prefixes"]["ns"+str(i)]=ns
                            i=i+1
                self.feasibleConfiguration=True
            else:
                self.message="SPARQL endpoint does not seem to include the following geometry relations: geo:asWKT, geo:asGeoJSON, geo:lat, geo:long.\nA manual configuration is probably necessary to include this SPARQL endpoint"
                self.feasibleConfiguration=False
                return False
        else:	
            self.message="URL does not depict a valid SPARQL Endpoint!"
            self.feasibleConfiguration=False
            return False
        if self.testTripleStoreConnection(testQueries["hasRDFSLabel"]) and self.testTripleStoreConnection(testQueries["hasRDFType"]):
            self.configuration["classfromlabelquery"]="SELECT DISTINCT ?class { ?class <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> . ?class <http://www.w3.org/2000/01/rdf-schema#label> ?label . FILTER(CONTAINS(?label,\"%%label%%\"))} LIMIT 100 "
            self.configuration["whattoenrichquery"]="SELECT DISTINCT (COUNT(distinct ?con) AS ?countcon) (COUNT(?rel) AS ?countrel) ?rel WHERE { ?con <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> %%concept%% . ?con ?rel ?val . } GROUP BY ?rel ORDER BY DESC(?countrel)"
        return True


    def finished(self, result):
        self.progress.close()
        if self.feasibleConfiguration and self.testConfiguration:
            msgBox=QMessageBox()	
            msgBox.setStandardButtons(QMessageBox.Yes)
            msgBox.addButton(QMessageBox.No)
            msgBox.setWindowTitle("Automatic Detection Successful")
            msgBox.setText(self.message)
            if msgBox.exec()!=QMessageBox.Yes:
                return
            else:
                self.comboBox.addItem(self.triplestorename)
                if self.tripleStoreChooser!=None:
                    self.tripleStoreChooser.addItem(self.triplestorename)
                index=len(self.triplestoreconf)
                self.triplestoreconf.append({})
                self.triplestoreconf[index]=self.configuration
                self.addTripleStore=False
                self.prefixes.append("")
                for prefix in self.configuration["prefixes"]:                 
                    self.prefixes[index]+="PREFIX "+prefix+":<"+self.configuration["prefixes"][prefix]+">\n"
                if self.permanentAdd!=None and self.permanentAdd:
                    f = open("triplestoreconf_personal.json", "w")
                    f.write(json.dumps(self.triplestoreconf,indent=2))
                    f.close()
                if self.parentdialog!=None:
                    self.parentdialog.close()
        elif self.feasibleConfiguration:
            msgBox=QMessageBox()
            msgBox.setText(self.message)
            msgBox.setWindowTitle("Automatic Detection Successful")
            msgBox.exec()
        else:
            msgBox=QMessageBox()
            msgBox.setText(self.message)
            msgBox.setWindowTitle("Automatic Detection Failed")
            msgBox.exec()
        iface.messageBar().pushMessage("Detect Triple Store Configuration", "OK", level=Qgis.Success)

