from ..util.sparqlutils import SPARQLUtils
from qgis.core import Qgis
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog
)
from qgis.PyQt.QtWidgets import QTableWidgetItem

MESSAGE_CATEGORY = 'InstanceQueryTask'

class InstanceQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl, searchTerm, prefixes, searchResult, graph=None):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.searchTerm=searchTerm
        self.searchResult = searchResult
        self.prefixes=prefixes
        self.graph=graph
        self.queryresult={}

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        thequery=""
        if "wikidata" in self.triplestoreurl:
            QgsMessageLog.logMessage('Started task "{}"'.format(
                "WIKIDATA: SELECT ?con ?rel ?val WHERE { http://www.wikidata.org/entity/" + str(
                    self.searchTerm) + " ?rel ?val . }"), MESSAGE_CATEGORY, Qgis.Info)
            thequery="SELECT ?con ?rel ?val WHERE { <http://www.wikidata.org/entity/" + str(
                    self.searchTerm) + ">  ?rel ?val . }"
        else:
            QgsMessageLog.logMessage('Started task "{}"'.format(
                "SELECT ?con ?rel ?val WHERE { "+ str(
                    self.searchTerm) + " ?rel ?val . }"), MESSAGE_CATEGORY, Qgis.Info)
            thequery="SELECT ?rel ?val WHERE { <" + str(
                    self.searchTerm) + ">  ?rel ?val . }"
        if self.graph==None:
            results = SPARQLUtils.executeQuery(self.triplestoreurl,thequery)
        else:
            results=self.graph.query(thequery)
        QgsMessageLog.logMessage("Query results: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
        for result in results["results"]["bindings"]:
            if "rel" in result and "val" in result:
                self.queryresult[result["rel"]["value"]]=result["val"]["value"]
        return True

    def finished(self, result):
        while self.searchResult.rowCount()>0:
            self.searchResult.removeRow(0)
        self.searchResult.setHorizontalHeaderLabels(["Attribute", "Value"])
        counter=0
        for rel in self.queryresult:
            self.searchResult.insertRow(counter)
            item = QTableWidgetItem()
            item.setText(SPARQLUtils.labelFromURI(rel))
            item.setData(256, rel)
            self.searchResult.setItem(counter, 0, item)
            itembutton = QTableWidgetItem()
            item.setText(self.queryresult[rel])
            item.setData(256, self.queryresult[rel])
            self.searchResult.setItem(counter, 1, itembutton)
            counter+=1
