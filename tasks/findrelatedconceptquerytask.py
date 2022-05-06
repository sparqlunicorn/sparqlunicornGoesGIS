from ..util.ui.uiutils import UIUtils
from ..util.sparqlutils import SPARQLUtils
from qgis.core import Qgis,QgsTask, QgsMessageLog
from qgis.PyQt.QtGui import QStandardItem
from qgis.PyQt.QtWidgets import QHeaderView
from qgis.PyQt.QtCore import Qt, QSize

MESSAGE_CATEGORY = 'FindRelatedConceptQueryTask'

class FindRelatedConceptQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl,dlg,concept,triplestoreconf,searchResult):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.searchResultModel=dlg
        self.searchResult=searchResult
        self.triplestoreconf=triplestoreconf
        self.concept=concept
        while self.searchResultModel.rowCount()>0:
            self.searchResultModel.removeRow(0)
        self.searchResultModel.insertRow(0)
        curitem = QStandardItem()
        curitem.setText("Loading...")
        self.searchResultModel.setItem(0, 0, curitem)

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        rightsidequery = "SELECT DISTINCT ?rel ?val ?label ?rellabel WHERE { ?con <" + str(self.triplestoreconf["typeproperty"]) + "> <" + str(
            self.concept) + "> . ?con ?rel ?item . ?item  <" + str(
            self.triplestoreconf["typeproperty"]) + "> ?val . OPTIONAL { ?val  <" + str(
            self.triplestoreconf["labelproperty"]) + "> ?label . } OPTIONAL { ?rel  <" + str(
            self.triplestoreconf["labelproperty"]) + "> ?rellabel . }}"
        leftsidequery = "SELECT DISTINCT ?rel ?val ?label ?rellabel WHERE { ?tocon <" + str(self.triplestoreconf["typeproperty"]) + "> ?val . ?tocon ?rel ?con . ?con <" + str(self.triplestoreconf["typeproperty"]) + "> <" + str(
            self.concept) + "> . OPTIONAL { ?val <" + str(self.triplestoreconf["labelproperty"]) + "> ?label . } OPTIONAL { ?rel  <" + str(
            self.triplestoreconf["labelproperty"]) + "> ?rellabel . }}"
        QgsMessageLog.logMessage("SELECT ?rel WHERE { ?con "+str(self.triplestoreconf["typeproperty"])+" "+str(self.concept)+" . ?con ?rel ?item . OPTIONAL { ?item "+str(self.triplestoreconf["typeproperty"])+" ?val . } }", MESSAGE_CATEGORY, Qgis.Info)
        results = SPARQLUtils.executeQuery(self.triplestoreurl,leftsidequery,self.triplestoreconf)
        results2 = SPARQLUtils.executeQuery(self.triplestoreurl, rightsidequery, self.triplestoreconf)
        QgsMessageLog.logMessage("Query results: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
        self.queryresult={}
        self.queryresult2 = {}
        for result in results["results"]["bindings"]:
            if "rel" in result and "val" in result and result["rel"]["value"]!="":
                if result["rel"]["value"] not in self.queryresult:
                    self.queryresult[result["rel"]["value"]]={}
                self.queryresult[result["rel"]["value"]][result["val"]["value"]]={}
                if "rellabel" in result:
                    self.queryresult[result["rel"]["value"]][result["val"]["value"]]["rellabel"] = result["rellabel"][
                        "value"]
                else:
                    self.queryresult[result["rel"]["value"]][result["val"]["value"]]["rellabel"] = ""
                if "label" in result:
                    self.queryresult[result["rel"]["value"]][result["val"]["value"]]["label"]=result["label"]["value"]
                else:
                    self.queryresult[result["rel"]["value"]][result["val"]["value"]]["label"]=""
        for result in results2["results"]["bindings"]:
            if "rel" in result and "val" in result and result["rel"]["value"]!="":
                if result["rel"]["value"] not in self.queryresult:
                    self.queryresult2[result["rel"]["value"]]={}
                self.queryresult2[result["rel"]["value"]][result["val"]["value"]]={}
                if "rellabel" in result:
                    self.queryresult2[result["rel"]["value"]][result["val"]["value"]]["rellabel"] = result["rellabel"][
                        "value"]
                else:
                    self.queryresult2[result["rel"]["value"]][result["val"]["value"]]["rellabel"] = ""
                if "label" in result:
                    self.queryresult2[result["rel"]["value"]][result["val"]["value"]]["label"]=result["label"]["value"]
                else:
                    self.queryresult2[result["rel"]["value"]][result["val"]["value"]]["label"] = ""
        return True

    def finished(self, result):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            str(self.concept)), MESSAGE_CATEGORY, Qgis.Info)
        while self.searchResultModel.rowCount()>0:
            self.searchResultModel.removeRow(0)
        counter=0
        for rel in self.queryresult:
            for val in self.queryresult[rel]:
                self.searchResultModel.insertRow(counter)
                curitem=QStandardItem()
                if self.queryresult[rel][val]["label"]!="":
                    curitem.setText(str(self.queryresult[rel][val]["label"])+" ("+SPARQLUtils.labelFromURI(str(val))+")")
                else:
                    curitem.setText(SPARQLUtils.labelFromURI(str(val)))
                curitem.setToolTip(str(val))
                curitem.setIcon(UIUtils.classicon)
                curitem.setData(str(val),UIUtils.dataslot_conceptURI)
                self.searchResultModel.setItem(counter, 0, curitem)
                curitem=QStandardItem()
                UIUtils.detectItemNodeType(curitem, rel, self.triplestoreconf, None, None, None,
                                           SPARQLUtils.labelFromURI(rel)+"         ", rel)
                if self.queryresult[rel][val]["rellabel"]!="":
                    curitem.setText(str(self.queryresult[rel][val]["rellabel"])+" ("+SPARQLUtils.labelFromURI(rel)+")")
                self.searchResultModel.setItem(counter, 1, curitem)
                curitem=QStandardItem()
                curitem.setText(SPARQLUtils.labelFromURI(str(self.concept)))
                curitem.setIcon(UIUtils.classicon)
                curitem.setData(str(self.concept),UIUtils.dataslot_conceptURI)
                self.searchResultModel.setItem(counter, 2, curitem)
                self.searchResultModel.setItem(counter, 3, QStandardItem())
                self.searchResultModel.setItem(counter, 4, QStandardItem())
                counter+=1
        for rel in self.queryresult2:
            for val in self.queryresult2[rel]:
                self.searchResultModel.insertRow(counter)
                curitem=QStandardItem()
                UIUtils.detectItemNodeType(curitem,rel,self.triplestoreconf,None,None,None,SPARQLUtils.labelFromURI(rel)+"         ",rel)
                if self.queryresult2[rel][val]["rellabel"]!="":
                    curitem.setText(str(self.queryresult2[rel][val]["rellabel"])+" ("+SPARQLUtils.labelFromURI(rel)+")")
                self.searchResultModel.setItem(counter, 3, curitem)
                curitem=QStandardItem()
                curitem.setText(SPARQLUtils.labelFromURI(str(self.concept)))
                curitem.setIcon(UIUtils.classicon)
                curitem.setData(str(self.concept),UIUtils.dataslot_conceptURI)
                self.searchResultModel.setItem(counter, 2, curitem)
                curitem=QStandardItem()
                if self.queryresult2[rel][val]["label"]!="":
                    curitem.setText(str(self.queryresult2[rel][val]["label"])+" ("+SPARQLUtils.labelFromURI(str(val))+")")
                else:
                    curitem.setText(SPARQLUtils.labelFromURI(str(val)))
                curitem.setToolTip(str(val))
                curitem.setIcon(UIUtils.classicon)
                curitem.setData(str(val),UIUtils.dataslot_conceptURI)
                self.searchResultModel.setItem(counter, 4, curitem)
                self.searchResultModel.setItem(counter, 0, QStandardItem())
                self.searchResultModel.setItem(counter, 1, QStandardItem())
                counter+=1
        self.searchResultModel.setHeaderData(0, Qt.Horizontal, "Incoming Concept")
        self.searchResultModel.setHeaderData(1, Qt.Horizontal, "Incoming Relation")
        self.searchResultModel.setHeaderData(2, Qt.Horizontal, "Concept")
        self.searchResultModel.setHeaderData(3, Qt.Horizontal, "Outgoing Relation")
        self.searchResultModel.setHeaderData(4, Qt.Horizontal, "Outgoing Concept")
        header=self.searchResult.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
