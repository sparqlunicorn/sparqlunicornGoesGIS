import json
import urllib
import os
from qgis.PyQt.QtCore import QSettings
from qgis.utils import iface
from qgis.core import Qgis, QgsApplication
from qgis.PyQt.QtWidgets import QListWidgetItem, QMessageBox, QProgressDialog
from SPARQLWrapper import SPARQLWrapper, JSON
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
)

MESSAGE_CATEGORY = 'DetectTripleStoreTask'


class DetectTripleStoreTask(QgsTask):
    """This shows how to subclass QgsTask"""

    def __init__(self, description, triplestoreconf, endpoint, triplestorename, testURL, testConfiguration, prefixes,
                 prefixstore, tripleStoreChooser, comboBox, permanentAdd, parentdialog, progress):
        super().__init__(description, QgsTask.CanCancel)
        self.description = description
        self.exception = None
        self.prefixes = prefixes
        self.prefixstore = prefixstore
        self.permanentAdd = permanentAdd
        self.progress = progress
        self.triplestorename = triplestorename
        self.tripleStoreChooser = tripleStoreChooser
        self.comboBox = comboBox
        self.parentdialog = parentdialog
        self.triplestoreurl = endpoint
        self.triplestoreconf = triplestoreconf
        self.testURL = testURL
        self.configuration = {}
        self.testConfiguration = testConfiguration
        self.message = ""
        self.feasibleConfiguration = False
        s = QSettings()  # getting proxy from qgis options settings
        self.proxyEnabled = s.value("proxy/proxyEnabled")
        self.proxyType = s.value("proxy/proxyType")
        self.proxyHost = s.value("proxy/proxyHost")
        self.proxyPort = s.value("proxy/proxyPort")
        self.proxyUser = s.value("proxy/proxyUser")
        self.proxyPassword = s.value("proxy/proxyPassword")

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description), MESSAGE_CATEGORY, Qgis.Info)
        if self.testURL and not self.testConfiguration:
            self.testTripleStoreConnection()
            return True
        if self.testConfiguration and not self.testURL:
            res = self.detectTripleStoreConfiguration()
        return True

    def testTripleStoreConnection(self, query="SELECT ?a ?b ?c WHERE { ?a ?b ?c .} LIMIT 1"):
        if self.proxyHost != None and self.proxyHost != "" and self.proxyPort != None and self.proxyPort != "":
            QgsMessageLog.logMessage('Proxy? ' + str(self.proxyHost), MESSAGE_CATEGORY, Qgis.Info)
            proxy = urllib.request.ProxyHandler({'http': self.proxyHost})
            opener = urllib.request.build_opener(proxy)
            urllib.request.install_opener(opener)
        sparql = SPARQLWrapper(self.triplestoreurl,
                               agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        print("now sending query")
        try:
            results = sparql.query().convert()
            if self.testURL and not self.testConfiguration:
                self.message = "URL depicts a valid SPARQL Endpoint!"
            if "ASK" in query:
                return results["boolean"]
            self.feasibleConfiguration = True
            return True
        except:
            self.message = "URL does not depict a valid SPARQL Endpoint!"
            self.feasibleConfiguration = False
            return False

    def detectNamespaces(self, subpredobj):
        if subpredobj < 0 or subpredobj == None:
            query = "select distinct ?ns where { ?s ?p ?o . bind( replace( str(?s), \"(#|/)[^#/]*$\", \"$1\" ) as ?ns )} limit 10"
        elif subpredobj == 0:
            query = "select distinct ?ns where { ?s ?p ?o . bind( replace( str(?p), \"(#|/)[^#/]*$\", \"$1\" ) as ?ns )} limit 10"
        else:
            query = "select distinct ?ns where { ?s ?p ?o . bind( replace( str(?o), \"(#|/)[^#/]*$\", \"$1\" ) as ?ns )} limit 10"
        if self.proxyHost != None and self.proxyHost != "" and self.proxyPort != None and self.proxyPort != "":
            QgsMessageLog.logMessage('Proxy? ' + str(self.proxyHost), MESSAGE_CATEGORY, Qgis.Info)
            proxy = urllib.request.ProxyHandler({'http': self.proxyHost})
            opener = urllib.request.build_opener(proxy)
            urllib.request.install_opener(opener)
        sparql = SPARQLWrapper(self.triplestoreurl,
                               agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        print("now sending query")
        try:
            results = sparql.query().convert()
            reslist = []
            for nss in results["results"]["bindings"]:
                if "ns" in nss:
                    reslist.append(nss["ns"]["value"])
            return reslist
        except:
            return []

    ## Detects default configurations of common geospatial triple stores.
    #  @param self The object pointer.
    def detectTripleStoreConfiguration(self):
        self.configuration = {}
        self.configuration["name"] = self.triplestorename
        self.configuration["endpoint"] = self.triplestoreurl
        self.configuration["geoconceptlimit"] = 500
        self.configuration["crs"] = 4326
        self.configuration["staticconcepts"] = []
        self.configuration["active"] = True
        self.configuration["prefixes"] = {"owl": "http://www.w3.org/2002/07/owl#",
                                          "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                                          "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                                          "geosparql": "http://www.opengis.net/ont/geosparql#",
                                          "geof": "http://www.opengis.net/def/function/geosparql/",
                                          "geor": "http://www.opengis.net/def/rule/geosparql/",
                                          "sf": "http://www.opengis.net/ont/sf#",
                                          "wgs84_pos": "http://www.w3.org/2003/01/geo/wgs84_pos#"}
        testQueries = {
            "geosparql": "PREFIX geof:<http://www.opengis.net/def/function/geosparql/> SELECT ?a ?b ?c WHERE { BIND( \"POINT(1 1)\"^^<http://www.opengis.net/ont/geosparql#wktLiteral> AS ?a) BIND( \"POINT(1 1)\"^^<http://www.opengis.net/ont/geosparql#wktLiteral> AS ?b) FILTER(geof:sfIntersects(?a,?b))}",
            "available": "SELECT ?a ?b ?c WHERE { ?a ?b ?c .} LIMIT 1",
            "hasRDFSLabel": "PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> ASK { ?a rdfs:label ?c . }",
            "hasRDFType": "PREFIX rdf:<http:/www.w3.org/1999/02/22-rdf-syntax-ns#> ASK { ?a <http:/www.w3.org/1999/02/22-rdf-syntax-ns#type> ?c . }",
            "hasWKT": "PREFIX geosparql:<http://www.opengis.net/ont/geosparql#> ASK { ?a geosparql:asWKT ?c .}",
            "hasGML": "PREFIX geosparql:<http://www.opengis.net/ont/geosparql#> ASK { ?a geosparql:asGML ?c .}",
            "hasGeoJSON": "PREFIX geosparql:<http://www.opengis.net/ont/geosparql#> ASK { ?a geosparql:asGeoJSON ?c .}",
            "hasLatLon": "PREFIX geo:<http://www.w3.org/2003/01/geo/wgs84_pos#> ASK { ?a geo:lat ?c . ?a geo:long ?d . }",
            "namespaceQuery": "select distinct ?ns where {  ?s ?p ?o . bind( replace( str(?s), \"(#|/)[^#/]*$\", \"$1\" ) as ?ns )} limit 10"}
        if self.testTripleStoreConnection(testQueries["available"]):
            if self.testTripleStoreConnection(testQueries["hasWKT"]):
                if self.testTripleStoreConnection(testQueries["geosparql"]):
                    self.configuration["bboxquery"] = {}
                    self.configuration["bboxquery"]["type"] = "geosparql"
                    self.configuration["bboxquery"][
                        "query"] = "FILTER(<http://www.opengis.net/def/function/geosparql/sfIntersects>(?geo,\"POLYGON((%%x1%% %%y1%%, %%x1%% %%y2%%, %%x2%% %%y2%%, %%x2%% %%y1%%, %%x1%% %%y1%%))\"^^<http://www.opengis.net/ont/geosparql#wktLiteral>))"
                    self.message = "URL depicts a valid GeoSPARQL Endpoint and contains WKT Literals!\nWould you like to add this SPARQL endpoint?"
                else:
                    self.message = "URL depicts a valid SPARQL Endpoint and contains WKT Literals!\nWould you like to add this SPARQL endpoint?"
                self.configuration["mandatoryvariables"] = ["item", "geo"]
                self.configuration["querytemplate"] = []
                self.configuration["querytemplate"].append({"label": "10 Random Geometries",
                                                            "query": "SELECT ?item ?geo WHERE {\n ?item <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <%%concept%%>.\n ?item <http://www.opengis.net/ont/geosparql#hasGeometry> ?geom_obj .\n ?geom_obj <http://www.opengis.net/ont/geosparql#asWKT> ?geo .\n } LIMIT 10"})
                self.configuration["featurecollectionclasses"] = [
                    "http://www.opengis.net/ont/geosparql#FeatureCollection"]
                self.configuration["geometrycollectionclasses"] = [
                    "http://www.opengis.net/ont/geosparql#GeometryCollection"]
                self.configuration[
                    "geoconceptquery"] = "SELECT DISTINCT ?class WHERE { ?a <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?class . ?a <http://www.opengis.net/ont/geosparql#hasGeometry> ?a_geom . ?a_geom <http://www.opengis.net/ont/geosparql#asWKT> ?wkt .}"
                self.configuration[
                    "geocollectionquery"] = "SELECT DISTINCT ?colinstance ?label  WHERE { ?colinstance rdf:type %%concept%% . OPTIONAL { ?colinstance rdfs:label ?label . } }"
                self.configuration["subclassquery"]="SELECT DISTINCT ?subclass ?label WHERE { ?a <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?subclass . ?a ?rel ?a_geom . ?a_geom <http://www.opengis.net/ont/geosparql#asWKT> ?wkt . OPTIONAL { ?subclass rdfs:label ?label . } ?subclass rdfs:subClassOf %%concept%% . }"
                res = set(self.detectNamespaces(-1) + self.detectNamespaces(0) + self.detectNamespaces(1))
                i = 0
                for ns in res:
                    if ns != "http://" and ns.startswith("http://"):
                        if ns in self.prefixstore["reversed"]:
                            self.configuration["prefixes"][self.prefixstore["reversed"][ns]] = ns
                        else:
                            self.configuration["prefixes"]["ns" + str(i)] = ns
                            i = i + 1
                self.feasibleConfiguration = True
                QgsMessageLog.logMessage(str(self.configuration))
            elif self.testTripleStoreConnection(testQueries["hasLatLon"]):
                self.message = "URL depicts a valid SPARQL Endpoint and contains Lat/long!\nWould you like to add this SPARQL endpoint?"
                self.configuration["mandatoryvariables"] = ["item", "lat", "lon"]
                self.configuration["querytemplate"] = []
                self.configuration["querytemplate"].append({"label": "10 Random Geometries",
                                                            "query": "SELECT ?item ?lat ?lon WHERE {\n ?item <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> .\n ?item <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?lat .\n ?item <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?lon .\n } LIMIT 10"})
                self.configuration["featurecollectionclasses"] = [
                    "http://www.opengis.net/ont/geosparql#FeatureCollection"]
                self.configuration["geometrycollectionclasses"] = [
                    "http://www.opengis.net/ont/geosparql#GeometryCollection"]
                self.configuration[
                    "geoconceptquery"] = "SELECT DISTINCT ?class WHERE { ?a <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?class . ?a <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?lat . ?a <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?lon .}"
                self.configuration[
                    "geocollectionquery"] = "SELECT DISTINCT ?colinstance ?label  WHERE { ?colinstance rdf:type %%concept%% . OPTIONAL { ?colinstance rdfs:label ?label . } }"
                self.configuration[
                    "subclassquery"] = "SELECT DISTINCT ?subclass ?label WHERE { ?a <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?subclass . ?a <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?lat . ?a <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?lon . OPTIONAL { ?subclass rdfs:label ?label . } ?subclass rdfs:subClassOf %%concept%% . }"
                res = set(self.detectNamespaces(-1) + self.detectNamespaces(0) + self.detectNamespaces(1))
                i = 0
                for ns in res:
                    if ns != "http://" and ns.startswith("http://"):
                        if ns in self.prefixstore["reversed"]:
                            self.configuration["prefixes"][self.prefixstore["reversed"][ns]] = ns
                        else:
                            self.configuration["prefixes"]["ns" + str(i)] = ns
                            i = i + 1
                self.feasibleConfiguration = True
                QgsMessageLog.logMessage(str(self.configuration))
            elif self.testTripleStoreConnection(testQueries["hasGeoJSON"]):
                if self.testTripleStoreConnection(testQueries["geosparql"]):
                    self.configuration["bboxquery"] = {}
                    self.configuration["bboxquery"]["type"] = "geosparql"
                    self.configuration["bboxquery"][
                        "query"] = "FILTER(<http://www.opengis.net/def/function/geosparql/sfIntersects>(?geo,\"POLYGON((%%x1%% %%y1%%, %%x1%% %%y2%%, %%x2%% %%y2%%, %%x2%% %%y1%%, %%x1%% %%y1%%))\"^^<http://www.opengis.net/ont/geosparql#geoJSONLiteral>))"
                    self.message = "URL depicts a valid GeoSPARQL Endpoint and contains GeoJSON Literals!\nWould you like to add this SPARQL endpoint?"
                else:
                    self.message = "URL depicts a valid SPARQL Endpoint and contains GeoJSON Literals!\nWould you like to add this SPARQL endpoint?"
                self.configuration["mandatoryvariables"] = ["item", "geo"]
                self.configuration["featurecollectionclasses"] = [
                    "http://www.opengis.net/ont/geosparql#FeatureCollection"]
                self.configuration["geometrycollectionclasses"] = [
                    "http://www.opengis.net/ont/geosparql#GeometryCollection"]
                self.configuration["querytemplate"] = []
                self.configuration["querytemplate"].append({"label": "10 Random Geometries",
                                                            "query": "SELECT ?item ?geo WHERE {\n ?item a <%%concept%%>.\n ?item <http://www.opengis.net/ont/geosparql#hasGeometry> ?geom_obj .\n ?geom_obj <http://www.opengis.net/ont/geosparql#asGeoJSON> ?geo .\n } LIMIT 10"})
                self.configuration["querytemplate"].append({"label": "10 Random Geometries (All Attributes",
                                                            "query": "SELECT DISTINCT ?item ?rel ?val ?geo WHERE {\n ?item rdf:type <%%concept%%> .\n ?item ?rel ?val . \n ?val <http://www.opengis.net/ont/geosparql#asGeoJSON> ?geo .\n}\n LIMIT 100"})
                self.configuration[
                    "geoconceptquery"] = "SELECT DISTINCT ?class WHERE { ?a <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?class . ?a ?rel ?a_geom . ?a_geom <http://www.opengis.net/ont/geosparql#asGeoJSON> ?wkt .}"
                self.configuration[
                    "geocollectionquery"] = "SELECT DISTINCT ?colinstance ?label  WHERE { ?colinstance rdf:type %%concept%% . OPTIONAL { ?colinstance rdfs:label ?label . } }"
                self.configuration[
                    "subclassquery"] = "SELECT DISTINCT ?subclass ?label WHERE { ?a <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?subclass . ?a ?rel ?a_geom . ?a_geom <http://www.opengis.net/ont/geosparql#asGeoJSON> ?wkt . OPTIONAL { ?subclass rdfs:label ?label . } ?subclass rdfs:subClassOf %%concept%% . }"
                res = set(self.detectNamespaces(-1) + self.detectNamespaces(0) + self.detectNamespaces(1))
                i = 0
                for ns in res:
                    if ns != "http://" and ns.startswith("http://"):
                        if ns in self.prefixstore["reversed"]:
                            self.configuration["prefixes"][self.prefixstore["reversed"][ns]] = ns
                        else:
                            self.configuration["prefixes"]["ns" + str(i)] = ns
                            i = i + 1
                self.feasibleConfiguration = True
                QgsMessageLog.logMessage(str(self.configuration))
            else:
                self.message = "SPARQL endpoint does not seem to include the following geometry relations: geo:asWKT, geo:asGeoJSON, geo:lat, geo:long.\nA manual configuration is probably necessary to include this SPARQL endpoint"
                self.feasibleConfiguration = False
                return False
        else:
            self.message = "URL does not depict a valid SPARQL Endpoint!"
            self.feasibleConfiguration = False
            return False
        if self.testTripleStoreConnection(testQueries["hasRDFSLabel"]) and self.testTripleStoreConnection(
                testQueries["hasRDFType"]):
            self.configuration[
                "classfromlabelquery"] = "SELECT DISTINCT ?class ?label { ?class <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Class> . ?class <http://www.w3.org/2000/01/rdf-schema#label> ?label . FILTER(CONTAINS(?label,\"%%label%%\"))} LIMIT 100 "
            self.configuration[
                "propertyfromlabelquery"] = "SELECT DISTINCT ?class ?label { ?class <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#ObjectProperty> . ?class <http://www.w3.org/2000/01/rdf-schema#label> ?label . FILTER(CONTAINS(?label,\"%%label%%\"))} LIMIT 100 "
            self.configuration[
                "whattoenrichquery"] = "SELECT DISTINCT (COUNT(distinct ?con) AS ?countcon) (COUNT(?rel) AS ?countrel) ?rel WHERE { ?con <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> %%concept%% . ?con ?rel ?val . } GROUP BY ?rel ORDER BY DESC(?countrel)"
        return True

    def finished(self, result):
        self.progress.close()
        if self.feasibleConfiguration and self.testConfiguration:
            msgBox = QMessageBox()
            msgBox.setStandardButtons(QMessageBox.Yes)
            msgBox.addButton(QMessageBox.No)
            msgBox.setWindowTitle("Automatic Detection Successful")
            msgBox.setText(self.message)
            if msgBox.exec() != QMessageBox.Yes:
                return
            else:
                self.comboBox.addItem(self.triplestorename)
                if self.tripleStoreChooser != None:
                    self.tripleStoreChooser.addItem(self.triplestorename)
                index = len(self.triplestoreconf)
                self.triplestoreconf.append({})
                self.triplestoreconf[index] = self.configuration
                self.addTripleStore = False
                self.prefixes.append("")
                for prefix in self.configuration["prefixes"]:
                    self.prefixes[index] += "PREFIX " + prefix + ":<" + self.configuration["prefixes"][prefix] + ">\n"
                if self.permanentAdd != None and self.permanentAdd:
                    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
                    f = open(os.path.join(__location__, 'triplestoreconf_personal.json'), "w")
                    f.write(json.dumps(self.triplestoreconf, indent=2))
                    f.close()
                if self.parentdialog != None:
                    self.parentdialog.close()
        elif self.feasibleConfiguration:
            msgBox = QMessageBox()
            msgBox.setText(self.message)
            msgBox.setWindowTitle("Automatic Detection Successful")
            msgBox.exec()
        else:
            msgBox = QMessageBox()
            msgBox.setText(self.message)
            msgBox.setWindowTitle("Automatic Detection Failed")
            msgBox.exec()
        iface.messageBar().pushMessage("Detect Triple Store Configuration", "OK", level=Qgis.Success)
