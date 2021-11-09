from SPARQLWrapper import SPARQLWrapper, JSON, GET, POST
import urllib
import json
from qgis.core import Qgis, QgsGeometry
from qgis.core import QgsMessageLog
from qgis.PyQt.QtCore import QSettings
from rdflib import Graph

MESSAGE_CATEGORY="SPARQLUtils"

class SPARQLUtils:
    
    supportedLiteralTypes = {"http://www.opengis.net/ont/geosparql#wktLiteral":"wkt","http://www.opengis.net/ont/geosparql#gmlLiteral":"gml","http://www.opengis.net/ont/geosparql#wkbLiteral":"wkb","http://www.opengis.net/ont/geosparql#geoJSONLiteral":"geojson","http://www.opengis.net/ont/geosparql#kmlLiteral":"kml","http://www.opengis.net/ont/geosparql#dggsLiteral":"dggs"}

    @staticmethod
    def executeQuery(triplestoreurl,query):
        s = QSettings()  # getting proxy from qgis options settings
        proxyEnabled = s.value("proxy/proxyEnabled")
        proxyType = s.value("proxy/proxyType")
        proxyHost = s.value("proxy/proxyHost")
        proxyPort = s.value("proxy/proxyPort")
        proxyUser = s.value("proxy/proxyUser")
        proxyPassword = s.value("proxy/proxyPassword")
        if proxyHost != None and proxyHost != "" and proxyPort != None and proxyPort != "":
            QgsMessageLog.logMessage('Proxy? ' + str(proxyHost), MESSAGE_CATEGORY, Qgis.Info)
            proxy = urllib.request.ProxyHandler({'http': proxyHost})
            opener = urllib.request.build_opener(proxy)
            urllib.request.install_opener(opener)
        QgsMessageLog.logMessage('Started task "{}"'.format(query), MESSAGE_CATEGORY, Qgis.Info)
        sparql = SPARQLWrapper(triplestoreurl,
                               agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
        sparql.setQuery(query)
        QgsMessageLog.logMessage('Proxy? ' + str(proxyHost), MESSAGE_CATEGORY, Qgis.Info)
        sparql.setMethod(GET)
        sparql.setReturnFormat(JSON)
        try:
            results = sparql.query().convert()
            if "status_code" in results:
                raise Exception
        except Exception as e:
            try:
                sparql = SPARQLWrapper(triplestoreurl,
                                       agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
                sparql.setQuery(query)
                sparql.setMethod(POST)
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                if "status_code" in results:
                    raise Exception
            except:
                QgsMessageLog.logMessage("Exception: " + str(e), MESSAGE_CATEGORY, Qgis.Info)
                return False
        return results

    @staticmethod
    def loadGraph(graphuri):
        s = QSettings()  # getting proxy from qgis options settings
        proxyEnabled = s.value("proxy/proxyEnabled")
        proxyType = s.value("proxy/proxyType")
        proxyHost = s.value("proxy/proxyHost")
        proxyPort = s.value("proxy/proxyPort")
        proxyUser = s.value("proxy/proxyUser")
        proxyPassword = s.value("proxy/proxyPassword")            
        if proxyHost != None and proxyHost != "" and proxyPort != None and proxyPort != "":
            QgsMessageLog.logMessage('Proxy? ' + str(proxyHost), MESSAGE_CATEGORY, Qgis.Info)
            proxy = urllib.request.ProxyHandler({'http': proxyHost})
            opener = urllib.request.build_opener(proxy)
            urllib.request.install_opener(opener)
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        graph = Graph()
        try:
            if self.filename.startswith("http"):
                graph.load(self.filename)
            else:
                filepath = self.filename.split(".")
                result = graph.parse(self.filename, format=filepath[len(filepath) - 1])
        except Exception as e:
            QgsMessageLog.logMessage('Failed "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
            self.exception = str(e)
            return None
        return graph

    @staticmethod
    def detectLiteralType(literal):
        try:
            geom = QgsGeometry.fromWkt(literal)
            return "wkt"
        except:
            print("no wkt")
        try:
            geom = QgsGeometry.fromWkb(bytes.fromhex(literal))
            return "wkb"
        except:
            print("no wkb")
        try:
            json.loads(literal)
            return "geojson"
        except:
            print("no geojson")
        return ""
    
    @staticmethod
    def handleURILiteral(uri):
        result = []
        if uri.startswith("http") and uri.endswith(".map"):
            try:
                f = urlopen(uri)
                myjson = json.loads(f.read())
                if "data" in myjson and "type" in myjson["data"] and myjson["data"]["type"] == "FeatureCollection":
                    features = myjson["data"]["features"]
                    for feat in features:
                        result.append(feat["geometry"])
                return result
            except:
                QgsMessageLog.logMessage("Error getting geoshape " + str(uri) + " - " + str(sys.exc_info()[0]))
        return None
