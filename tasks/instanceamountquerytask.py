from ..util.sparqlutils import SPARQLUtils
from qgis.core import Qgis
from qgis.PyQt.QtCore import QSettings, QItemSelectionModel
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
        if "wikidata" in self.triplestoreurl:
            wikicon=self.treeNode.data(256).split("(")[1].replace(" ","_").replace(")", "")
            QgsMessageLog.logMessage('Started task "{}"'.format(
                "WIKIDATA: SELECT (COUNT(?con) as ?amount) WHERE { ?con http://www.wikidata.org/prop/direct/P31 http://www.wikidata.org/entity/" + str(
                    wikicon) + " . }"), MESSAGE_CATEGORY, Qgis.Info)
            results = SPARQLUtils.executeQuery(self.proxyHost, self.proxyPort, self.triplestoreurl, "SELECT (COUNT(?con) as ?amount) WHERE { ?con <http://www.wikidata.org/prop/direct/P31> <http://www.wikidata.org/entity/" + str(
                    wikicon) + "> . }")
        else:
            QgsMessageLog.logMessage('Started task "{}"'.format(
                "SELECT (COUNT(?con) as ?amount) WHERE { ?con http://www.w3.org/1999/02/22-rdf-syntax-ns#type " + str(
                    self.treeNode.data(256)) + " . }"), MESSAGE_CATEGORY, Qgis.Info)
            results = SPARQLUtils.executeQuery(self.proxyHost, self.proxyPort, self.triplestoreurl, "SELECT (COUNT(?con) as ?amount) WHERE { ?con <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <" + str(
                    self.treeNode.data(256)) + "> . }")
        QgsMessageLog.logMessage("Query results: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
        if results != False:
            self.amount = results["results"]["bindings"][0]["amount"]["value"]
        else:
            self.amount=0
        return True

    def finished(self, result):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.treeNode.text()+" ["+str(self.amount)+"]"), MESSAGE_CATEGORY, Qgis.Info)
        if self.amount!=-1:
            self.treeNode.setText(self.treeNode.text()+" ["+str(self.amount)+"]")