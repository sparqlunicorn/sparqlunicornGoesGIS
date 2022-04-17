from ..util.layerutils import LayerUtils
from ..util.ui.uiutils import UIUtils
from ..util.sparqlutils import SPARQLUtils
from qgis.core import Qgis, QgsFeature, QgsVectorLayer, QgsCoordinateReferenceSystem
from qgis.core import Qgis,QgsTask, QgsMessageLog
from qgis.PyQt.QtGui import QStandardItem
import json

from qgis.PyQt.QtCore import Qt, QSize

MESSAGE_CATEGORY = 'FindRelatedConceptQueryTask'

class FindRelatedConceptQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl,dlg,concept,triplestoreconf):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.searchResultModel=dlg
        self.triplestoreconf=triplestoreconf
        self.concept=concept

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        rightsidequery = "SELECT ?rel ?val WHERE { ?con <" + str(self.triplestoreconf["typeproperty"]) + "> <" + str(
            self.concept) + "> . ?con ?rel ?item . OPTIONAL { ?item  <" + str(
            self.triplestoreconf["typeproperty"]) + "> ?val . } }"
        leftsidequery = "SELECT ?rel ?val WHERE { ?tocon <" + str(self.triplestoreconf["typeproperty"]) + "> ?val . ?tocon ?rel ?con . ?con <" + str(self.triplestoreconf["typeproperty"]) + "> <" + str(
            self.concept) + "> . }"
        QgsMessageLog.logMessage("SELECT ?rel WHERE { ?con "+str(self.triplestoreconf["typeproperty"])+" "+str(self.concept)+" . ?con ?rel ?item . OPTIONAL { ?item "+str(self.triplestoreconf["typeproperty"])+" ?val . } }", MESSAGE_CATEGORY, Qgis.Info)
        results = SPARQLUtils.executeQuery(self.triplestoreurl,leftsidequery,self.triplestoreconf)
        results2 = SPARQLUtils.executeQuery(self.triplestoreurl, rightsidequery, self.triplestoreconf)
        QgsMessageLog.logMessage("Query results: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
        self.queryresult={}
        self.queryresult2 = {}
        for result in results["results"]["bindings"]:
            if "rel" in result and "val" in result and result["rel"]["value"]!="":
                if result["rel"]["value"] not in self.queryresult:
                    self.queryresult[result["rel"]["value"]]=set()
                    #self.queryresult[result["rel"]["value"]]["values"]=set()
                self.queryresult[result["rel"]["value"]].add(result["val"]["value"])
        for result in results2["results"]["bindings"]:
            if "rel" in result and "val" in result and result["rel"]["value"]!="":
                if result["rel"]["value"] not in self.queryresult:
                    self.queryresult2[result["rel"]["value"]]=set()
                    #self.queryresult[result["rel"]["value"]]["values"]=set()
                self.queryresult2[result["rel"]["value"]].add(result["val"]["value"])
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
                curitem.setText(SPARQLUtils.labelFromURI(str(val)))
                curitem.setToolTip(str(val))
                curitem.setIcon(UIUtils.classicon)
                self.searchResultModel.setItem(counter, 0, curitem)
                curitem=QStandardItem()
                curitem.setText(SPARQLUtils.labelFromURI(rel))
                curitem.setToolTip(rel)
                self.searchResultModel.setItem(counter, 1, curitem)
                self.searchResultModel.setItem(counter, 2, QStandardItem())
                self.searchResultModel.setItem(counter, 3, QStandardItem())
                counter+=1
        for rel in self.queryresult2:
            for val in self.queryresult2[rel]:
                self.searchResultModel.insertRow(counter)
                curitem=QStandardItem()
                curitem.setText(SPARQLUtils.labelFromURI(rel))
                curitem.setToolTip(rel)
                self.searchResultModel.setItem(counter, 2, curitem)
                curitem=QStandardItem()
                curitem.setText(SPARQLUtils.labelFromURI(str(val)))
                curitem.setToolTip(str(val))
                curitem.setIcon(UIUtils.classicon)
                self.searchResultModel.setItem(counter, 3, curitem)
                self.searchResultModel.setItem(counter, 0, QStandardItem())
                self.searchResultModel.setItem(counter, 1, QStandardItem())
                counter+=1
        self.searchResultModel.setHeaderData(0, Qt.Horizontal, "Incoming Concept")
        self.searchResultModel.setHeaderData(1, Qt.Horizontal, "Incoming Relation")
        self.searchResultModel.setHeaderData(2, Qt.Horizontal, "Outgoing Relation")
        self.searchResultModel.setHeaderData(3, Qt.Horizontal, "Outgoing Concept")
