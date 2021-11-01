import urllib
from qgis.core import Qgis
from qgis.PyQt.QtCore import QSettings, QItemSelectionModel
from SPARQLWrapper import SPARQLWrapper, JSON, GET
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog
)

MESSAGE_CATEGORY = 'InstanceAmountQueryTask'

class InstanceAmountQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl,dlg,treeNode):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.dlg=dlg
        self.treeNode=treeNode
        self.geoTreeViewModel=self.dlg.geoTreeViewModel
        self.amount=-1
        s = QSettings()  # getting proxy from qgis options settings
        self.proxyEnabled = s.value("proxy/proxyEnabled")
        self.proxyType = s.value("proxy/proxyType")
        self.proxyHost = s.value("proxy/proxyHost")
        self.proxyPort = s.value("proxy/proxyPort")
        self.proxyUser = s.value("proxy/proxyUser")
        self.proxyPassword = s.value("proxy/proxyPassword")

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        if self.proxyHost != None and self.proxyHost != "" and self.proxyPort != None and self.proxyPort != "":
            QgsMessageLog.logMessage('Proxy? ' + str(self.proxyHost), MESSAGE_CATEGORY, Qgis.Info)
            proxy = urllib.request.ProxyHandler({'http': self.proxyHost})
            opener = urllib.request.build_opener(proxy)
            urllib.request.install_opener(opener)
        sparql = SPARQLWrapper(self.triplestoreurl,
                               agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
        if "wikidata" in self.triplestoreurl:
            wikicon=self.treeNode.data(256).split("(")[1].replace(" ","_").replace(")", "")
            QgsMessageLog.logMessage('Started task "{}"'.format(
                "WIKIDATA: SELECT (COUNT(?con) as ?amount) WHERE { ?con http://www.wikidata.org/prop/direct/P31 http://www.wikidata.org/entity/" + str(
                    wikicon) + " . }"), MESSAGE_CATEGORY, Qgis.Info)
            sparql.setQuery(
                "SELECT (COUNT(?con) as ?amount) WHERE { ?con <http://www.wikidata.org/prop/direct/P31> <http://www.wikidata.org/entity/" + str(
                    wikicon) + "> . }")
        else:
            QgsMessageLog.logMessage('Started task "{}"'.format(
                "SELECT (COUNT(?con) as ?amount) WHERE { ?con http://www.w3.org/1999/02/22-rdf-syntax-ns#type " + str(
                    self.treeNode.data(256)) + " . }"), MESSAGE_CATEGORY, Qgis.Info)
            sparql.setQuery(
                "SELECT (COUNT(?con) as ?amount) WHERE { ?con <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <" + str(
                    self.treeNode.data(256)) + "> . }")
        sparql.setMethod(GET)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        self.amount = results["results"]["bindings"][0]["amount"]["value"]
        return True

    def finished(self, result):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.treeNode.text()+" ["+str(self.amount)+"]"), MESSAGE_CATEGORY, Qgis.Info)
        if self.amount!=-1:
            self.treeNode.setText(self.treeNode.text()+" ["+str(self.amount)+"]")