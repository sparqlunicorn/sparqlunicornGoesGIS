from SPARQLWrapper import SPARQLWrapper, JSON, GET, POST
import urllib
from qgis.core import Qgis
from qgis.core import QgsMessageLog
from qgis.PyQt.QtCore import QSettings

MESSAGE_CATEGORY="SPARQLUtils"

class SPARQLUtils:

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
