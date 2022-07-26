from collections.abc import Iterable

from ....util.ui.uiutils import UIUtils
from ....util.sparqlutils import SPARQLUtils
from qgis.PyQt.QtCore import Qt
from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QTableWidgetItem, QMessageBox
from qgis.core import (
    QgsTask, QgsMessageLog,
)

MESSAGE_CATEGORY = 'WhatToEnrichQueryTask'


class WhatToEnrichQueryTask(QgsTask):
    """This shows how to subclass QgsTask"""

    def __init__(self, description, triplestoreurl, query, searchTerm, prefixes, searchResult,  triplestoreconf,progress):
        super().__init__(description, QgsTask.CanCancel)
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.query = query
        self.prefixes = prefixes
        self.triplestoreconf=triplestoreconf
        self.labels = None
        self.progress = progress
        self.urilist = None
        self.sortedatt = None
        self.searchTerm = searchTerm
        self.searchResult = searchResult
        self.results = None
        while self.searchResult.rowCount()>0:
            self.searchResult.removeRow(0)
        self.searchResult.setHorizontalHeaderLabels(["Selection","Attribute", "Sample Instances"])
        self.searchResult.insertRow(0)
        item = QTableWidgetItem()
        item.setText("Loading...")
        self.searchResult.setItem(0,0,item)
        self.searchResult.setMouseTracking(True)

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        QgsMessageLog.logMessage('Started task "{}"'.format(self.searchTerm), MESSAGE_CATEGORY, Qgis.Info)
        self.query=SPARQLUtils.queryPreProcessing(self.query,self.triplestoreconf)
        if self.searchTerm == "":
            return False
        if isinstance(self.prefixes, Iterable):
            results = SPARQLUtils.executeQuery(self.triplestoreurl, "".join(self.prefixes) + self.query,
                                               self.triplestoreconf)
        else:
            results = SPARQLUtils.executeQuery(self.triplestoreurl, str(self.prefixes).replace("None", "") + self.query,
                                               self.triplestoreconf)
        if results == False:
            return False
        if len(results["results"]["bindings"]) == 0:
            return False
        maxcons = int(results["results"]["bindings"][0]["countcon"]["value"])
        self.sortedatt = {}
        for result in results["results"]["bindings"]:
            if maxcons != 0 and str(maxcons) != "0":
                self.sortedatt[result["rel"]["value"][result["rel"]["value"].rfind('/') + 1:]] = {"amount": round(
                    (int(result["countrel"]["value"]) / maxcons) * 100, 2), "concept": result["rel"]["value"]}
            if "valtype" in result and result["valtype"]["value"] != "":
                self.sortedatt[result["rel"]["value"][result["rel"]["value"].rfind('/') + 1:]]["valtype"] = \
                result["valtype"]["value"]
        self.sortedatt = SPARQLUtils.getLabelsForClasses(self.sortedatt, self.triplestoreconf["propertylabelquery"],
                                                      self.triplestoreconf,
                                                      self.triplestoreurl)
        return True

    def finished(self, result):
        while self.searchResult.rowCount()>0:
            self.searchResult.removeRow(0)
        self.searchResult.setHorizontalHeaderLabels(["Selection","Attribute", "Sample Instances"])
        self.searchResult.setMouseTracking(True)
        if self.sortedatt != None:
            if len(self.sortedatt)==0:
                self.searchResult.insertRow(0)
                item = QTableWidgetItem()
                item.setText("No results found")
                self.searchResult.setItem(0,0,item)
            else:
                UIUtils.fillAttributeTable(self.sortedatt, None, self.dlg, self.searchResultModel,self.triplestoreconf, SPARQLUtils.classnode,"Check this item if you want to enrich your dataset with it",Qt.Unchecked)
        else:
            msgBox = QMessageBox()
            msgBox.setText("The enrichment search query did not yield any results!")
            msgBox.exec()
        self.progress.close()
