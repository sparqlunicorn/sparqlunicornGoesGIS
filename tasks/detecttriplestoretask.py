import json
import os
from ..util.sparqlutils import SPARQLUtils
from qgis.utils import iface
from qgis.core import Qgis, QgsApplication
from qgis.PyQt.QtWidgets import QListWidgetItem, QMessageBox, QProgressDialog
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
)

MESSAGE_CATEGORY = 'DetectTripleStoreTask'

class DetectTripleStoreTask(QgsTask):
    """This shows how to subclass QgsTask"""

    def __init__(self, description, triplestoreconf, endpoint, triplestorename, credentialUserName, credentialPassword,authmethod, testURL, testConfiguration, prefixes,
                 prefixstore, tripleStoreChooser, comboBox, permanentAdd, parentdialog, progress):
        super().__init__(description, QgsTask.CanCancel)
        self.description = description
        self.exception = None
        self.prefixes = prefixes
        self.prefixstore = prefixstore
        self.permanentAdd = permanentAdd
        self.progress = progress
        self.credentialUserName=credentialUserName
        self.credentialPassword=credentialPassword
        self.authmethod=authmethod
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

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description+" "+str(self.testURL)+" "+str(self.testConfiguration)), MESSAGE_CATEGORY, Qgis.Info)
        if self.testURL and not self.testConfiguration:
            self.testTripleStoreConnection()
            return True
        if self.testConfiguration and not self.testURL:
            res = self.detectTripleStoreConfiguration()
        return True

    def testTripleStoreConnection(self, query="SELECT ?a ?b ?c WHERE { ?a ?b ?c .} LIMIT 1"):
        QgsMessageLog.logMessage("Execute query: "+str(query), MESSAGE_CATEGORY, Qgis.Info)
        results=SPARQLUtils.executeQuery(self.triplestoreurl,query,{"auth":{"method":self.authmethod,"userCredential":self.credentialUserName,"userPassword":self.credentialPassword}})
        QgsMessageLog.logMessage("Query results: "+str(results), MESSAGE_CATEGORY, Qgis.Info)
        if results!=False:
            if self.testURL and not self.testConfiguration:
                self.message = "URL depicts a valid SPARQL Endpoint!"
            if "ASK" in query:
                QgsMessageLog.logMessage("Result: "+str(results["boolean"]), MESSAGE_CATEGORY, Qgis.Info)
                return results["boolean"]
            self.feasibleConfiguration = True
            return True
        return results

    def detectNamespaces(self, subpredobj):
        if subpredobj < 0 or subpredobj == None:
            query = "select distinct ?ns where { ?s ?p ?o . bind( replace( str(?s), \"(#|/)[^#/]*$\", \"$1\" ) as ?ns )} limit 10"
        elif subpredobj == 0:
            query = "select distinct ?ns where { ?s ?p ?o . bind( replace( str(?p), \"(#|/)[^#/]*$\", \"$1\" ) as ?ns )} limit 10"
        else:
            query = "select distinct ?ns where { ?s ?p ?o . bind( replace( str(?o), \"(#|/)[^#/]*$\", \"$1\" ) as ?ns )} limit 10"
        results=SPARQLUtils.executeQuery(self.triplestoreurl,query,{"auth":{"method":self.authmethod,"userCredential":self.credentialUserName,"userPassword":self.credentialPassword}})
        if results==False:
            return []
        reslist = []
        for nss in results["results"]["bindings"]:
            if "ns" in nss:
                reslist.append(nss["ns"]["value"])
        return reslist

    ## Detects default configurations of common geospatial triple stores.
    #  @param self The object pointer.
    def detectTripleStoreConfiguration(self):
        self.configuration = {}
        self.configuration["name"] = self.triplestorename
        self.configuration["endpoint"] = self.triplestoreurl
        self.configuration["geoconceptlimit"] = 500
        self.configuration["crs"] = 4326
        if self.credentialUserName!=None and self.credentialUserName!="" and self.credentialPassword!=None and self.credentialPassword!=None:
            self.configuration["auth"]={}
            self.configuration["auth"]["userCredential"] = self.credentialUserName
            self.configuration["auth"]["userPassword"] = self.credentialPassword
            self.configuration["auth"]["method"]=self.authmethod
        self.configuration["typeproperty"] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        self.configuration["labelproperty"] = "http://www.w3.org/2000/01/rdf-schema#label"
        self.configuration["subclassproperty"] = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
        self.configuration["whattoenrichquery"] = "SELECT DISTINCT (COUNT(distinct ?con) AS ?countcon) (COUNT(?rel) AS ?countrel) ?rel WHERE { ?con <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> %%concept%% . ?con ?rel ?val . } GROUP BY ?rel ORDER BY DESC(?countrel)"
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
            "hasKML": "PREFIX geosparql:<http://www.opengis.net/ont/geosparql#> ASK { ?a geosparql:asKML ?c .}",
            "hasGeoJSON": "PREFIX geosparql:<http://www.opengis.net/ont/geosparql#> ASK { ?a geosparql:asGeoJSON ?c .}",
            "hasWgs84LatLon": "PREFIX geo:<http://www.w3.org/2003/01/geo/wgs84_pos#> ASK { ?a geo:lat ?c . ?a geo:long ?d . }",
            "hasSchemaOrgGeo": "PREFIX schema:<http://schema.org/> ASK { ?a schema:geo ?c . }",
            "namespaceQuery": "select distinct ?ns where {  ?s ?p ?o . bind( replace( str(?s), \"(#|/)[^#/]*$\", \"$1\" ) as ?ns )} limit 10"}
        if self.testTripleStoreConnection(testQueries["available"]):
            QgsMessageLog.logMessage("Triple Store "+str(self.triplestoreurl)+" is available!", MESSAGE_CATEGORY, Qgis.Info)
            if self.testTripleStoreConnection(testQueries["hasWKT"]):
                QgsMessageLog.logMessage("Triple Store " + str(self.triplestoreurl) + " contains WKT literals!", MESSAGE_CATEGORY,
                                         Qgis.Info)
                self.configuration["geometryproperty"] = "http://www.opengis.net/ont/geosparql#hasGeometry"
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
                self.configuration[
                    "whattoenrichquery"] = "SELECT DISTINCT (COUNT(distinct ?con) AS ?countcon) (COUNT(?rel) AS ?countrel) ?rel WHERE { ?con <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> %%concept%% . ?con ?rel ?val . } GROUP BY ?rel ORDER BY DESC(?countrel)"
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
            elif self.testTripleStoreConnection(testQueries["hasWgs84LatLon"]):
                QgsMessageLog.logMessage("Triple Store " + str(self.triplestoreurl) + " contains WGS84 Lat/Lon properties!",
                                         MESSAGE_CATEGORY,
                                         Qgis.Info)
                self.configuration["geometryproperty"] = "http://www.w3.org/2003/01/geo/wgs84_pos#lat"
                self.message = "URL depicts a valid SPARQL Endpoint and contains Lat/long!\nWould you like to add this SPARQL endpoint?"
                self.configuration["mandatoryvariables"] = ["item", "lat", "lon"]
                self.configuration["querytemplate"] = []
                self.configuration["querytemplate"].append({"label": "10 Random Geometries",
                                                            "query": "SELECT ?item ?lat ?lon WHERE {\n ?item <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <%%concept%%> .\n ?item <http://www.w3.org/2003/01/geo/wgs84_pos#lat> ?lat .\n ?item <http://www.w3.org/2003/01/geo/wgs84_pos#long> ?lon .\n } LIMIT 10"})
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
                self.configuration[
                    "whattoenrichquery"] = "SELECT DISTINCT (COUNT(distinct ?con) AS ?countcon) (COUNT(?rel) AS ?countrel) ?rel WHERE { ?con <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> %%concept%% . ?con ?rel ?val . } GROUP BY ?rel ORDER BY DESC(?countrel)"
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
            elif self.testTripleStoreConnection(testQueries["hasSchemaOrgGeo"]):
                QgsMessageLog.logMessage("Triple Store " + str(self.triplestoreurl) + " contains Schema.org Lat/Lon properties!",
                                         MESSAGE_CATEGORY,
                                         Qgis.Info)
                self.configuration["geometryproperty"] = "https://schema.org/geo"
                self.message = "URL depicts a valid SPARQL Endpoint and contains Schema.org Lat/long!\nWould you like to add this SPARQL endpoint?"
                self.configuration["mandatoryvariables"] = ["item", "lat", "lon"]
                self.configuration["querytemplate"] = []
                self.configuration["querytemplate"].append({"label": "10 Random Geometries",
                                                            "query": "SELECT ?item ?lat ?lon WHERE {\n ?item <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <%%concept%%> .\n ?item <http://schema.org/geo> ?itemgeo . ?itemgeo <http://schema.org/latitude> ?lat .\n ?itemgeo <http://schema.org/longitude> ?lon .\n } LIMIT 10"})
                self.configuration["featurecollectionclasses"] = [
                    "http://www.opengis.net/ont/geosparql#FeatureCollection"]
                self.configuration["geometrycollectionclasses"] = [
                    "http://www.opengis.net/ont/geosparql#GeometryCollection"]
                self.configuration[
                    "geoconceptquery"] = "SELECT DISTINCT ?class WHERE { ?a <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?class . ?a <http://schema.org/latitude> ?lat . ?a <http://schema.org/longitude> ?lon .}"
                self.configuration[
                    "geocollectionquery"] = "SELECT DISTINCT ?colinstance ?label  WHERE { ?colinstance rdf:type %%concept%% . OPTIONAL { ?colinstance rdfs:label ?label . } }"
                self.configuration[
                    "subclassquery"] = "SELECT DISTINCT ?subclass ?label WHERE { ?a <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?subclass . ?a <http://schema.org/latitude> ?lat . ?a <http://schema.org/longitude> ?lon . OPTIONAL { ?subclass rdfs:label ?label . } ?subclass rdfs:subClassOf %%concept%% . }"
                self.configuration[
                    "whattoenrichquery"] = "SELECT DISTINCT (COUNT(distinct ?con) AS ?countcon) (COUNT(?rel) AS ?countrel) ?rel WHERE { ?con <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> %%concept%% . ?con ?rel ?val . } GROUP BY ?rel ORDER BY DESC(?countrel)"
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
                QgsMessageLog.logMessage("Triple Store " + str(self.triplestoreurl) + " contains GeoJSON literals!",
                                         MESSAGE_CATEGORY,
                                         Qgis.Info)
                if self.testTripleStoreConnection(testQueries["geosparql"]):
                    self.configuration["geometryproperty"] = "http://www.opengis.net/ont/geosparql#hasGeometry"
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
                self.configuration[
                    "whattoenrichquery"] = "SELECT DISTINCT (COUNT(distinct ?con) AS ?countcon) (COUNT(?rel) AS ?countrel) ?rel WHERE { ?con <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> %%concept%% . ?con ?rel ?val . } GROUP BY ?rel ORDER BY DESC(?countrel)"
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
                self.message = "SPARQL endpoint does not seem to include the following geometry relations: geo:asWKT, geo:asGeoJSON, geo:lat, geo:long.\nA manual configuration is probably necessary to include this SPARQL endpoint if it contains geometries\nDo you still want to add this SPARQL endpoint?"
                self.feasibleConfiguration = True
                return True
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
