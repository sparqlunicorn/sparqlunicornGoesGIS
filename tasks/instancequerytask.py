from ..util.sparqlutils import SPARQLUtils
from qgis.core import Qgis
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog
)
from qgis.PyQt.QtWidgets import QTableWidgetItem

MESSAGE_CATEGORY = 'InstanceQueryTask'

class InstanceQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl, searchTerm, triplestoreconf, searchResult, graph=None):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.searchTerm=searchTerm
        self.searchResult = searchResult
        self.prefixes= SPARQLUtils.invertPrefixes(triplestoreconf["prefixes"])
        self.triplestoreconf=triplestoreconf
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
            results = SPARQLUtils.executeQuery(self.triplestoreurl,thequery,self.triplestoreconf)
        else:
            results=self.graph.query(thequery)
        QgsMessageLog.logMessage("Query results: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
        for result in results["results"]["bindings"]:
            if "rel" in result and "val" in result:
                #QgsMessageLog.logMessage("Query results: " + str(result["rel"]["value"]), MESSAGE_CATEGORY, Qgis.Info)
                self.queryresult[result["rel"]["value"]]={"rel":result["rel"]["value"],"val":result["val"]["value"]}
        return True

    def finished(self, result):
        while self.searchResult.rowCount()>0:
            self.searchResult.removeRow(0)
        self.searchResult.setHorizontalHeaderLabels(["Attribute", "Value"])
        counter=0
        for rel in self.queryresult:
            QgsMessageLog.logMessage("Query results: " + str(rel), MESSAGE_CATEGORY, Qgis.Info)
            self.searchResult.insertRow(counter)
            item = QTableWidgetItem()
            item.setText(SPARQLUtils.labelFromURI(rel,self.prefixes))
            item.setData(256, str(rel))
            self.searchResult.setItem(counter, 0, item)
            itembutton = QTableWidgetItem()
            itembutton.setText(self.queryresult[rel]["val"])
            itembutton.setData(256, self.queryresult[rel]["val"])
            self.searchResult.setItem(counter, 1, itembutton)
            counter+=1
