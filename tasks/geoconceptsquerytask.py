from ..util.ui.uiutils import UIUtils
from ..util.sparqlutils import SPARQLUtils
from qgis.PyQt.QtCore import QItemSelectionModel
from qgis.PyQt.QtGui import QStandardItem,QColor
from qgis.PyQt.QtWidgets import QHeaderView
from qgis.core import Qgis,QgsTask, QgsMessageLog

MESSAGE_CATEGORY = 'GeoConceptsQueryTask'

class GeoConceptsQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl, query, triplestoreconf, sparql, queryvar, getlabels, layercount,
                 geoClassList, examplequery, geoClassListGui, completerClassList, dlg,preferredlang="en"):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.triplestoreconf = triplestoreconf
        self.query = query
        self.dlg = dlg
        self.layercount = layercount
        self.getlabels = getlabels
        self.completerClassList = completerClassList
        self.completerClassList["completerClassList"] = {}
        self.queryvar = queryvar
        self.sparql = sparql
        self.preferredlang=preferredlang
        self.geoClassListGui = geoClassListGui
        self.amountoflabels = -1
        self.geoClassList = geoClassList
        self.geoTreeViewModel=self.dlg.geoTreeViewModel
        self.examplequery = examplequery
        self.resultlist = {}

    def run(self):
        #QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        results = SPARQLUtils.executeQuery(self.triplestoreurl,self.query,self.triplestoreconf)
        if results==False:
            return False
        for result in results["results"]["bindings"]:
            self.resultlist[str(result[self.queryvar]["value"])]={"concept":str(result[self.queryvar]["value"])}
        if self.getlabels and "labelproperty" in self.triplestoreconf and self.triplestoreconf[
            "labelproperty"] != "":
            if "classlabelquery" in self.triplestoreconf:
                self.resultlist = SPARQLUtils.getLabelsForClasses(self.resultlist, self.triplestoreconf["classlabelquery"],self.triplestoreconf,self.triplestoreurl,self.preferredlang)
            else:
                self.resultlist = SPARQLUtils.getLabelsForClasses(self.resultlist, None,
                                                         self.triplestoreconf, self.triplestoreurl,self.preferredlang)
            QgsMessageLog.logMessage('Started task "{}"'.format(str(self.resultlist)), MESSAGE_CATEGORY, Qgis.Info)
        return True

    def finished(self, result):
        self.geoClassList.clear()
        self.geoTreeViewModel.clear()
        self.geoClassListGui.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.geoClassListGui.header().setStretchLastSection(False)
        self.geoClassListGui.header().setMinimumSectionSize(self.dlg.classTreeView.width())
        self.rootNode=self.geoTreeViewModel.invisibleRootItem()
        self.dlg.conceptViewTabWidget.setTabText(0, "GeoConcepts (" + str(len(self.resultlist)) + ")")
        if self.examplequery != None:
            self.sparql.setPlainText(self.examplequery)
            self.sparql.columnvars = {}
        for concept in self.resultlist:
            item = QStandardItem()
            item.setData(self.resultlist[concept]["concept"], 256)
            if "label" in self.resultlist[concept] and self.resultlist[concept]["label"]!="":
                item.setText(self.resultlist[concept]["label"]+" ("+SPARQLUtils.labelFromURI(self.resultlist[concept]["concept"],self.triplestoreconf["prefixesrev"]) + ")")
            else:
                item.setText(SPARQLUtils.labelFromURI(self.resultlist[concept]["concept"],self.triplestoreconf["prefixesrev"]))
            item.setForeground(QColor(0,0,0))
            item.setEditable(False)
            item.setIcon(UIUtils.geoclassicon)
            item.setData(SPARQLUtils.geoclassnode, 257)
            item.setToolTip("GeoClass "+str(item.text())+": <br>"+SPARQLUtils.treeNodeToolTip)
            self.rootNode.appendRow(item)
            if self.triplestoreconf["name"] == "Wikidata" and "label" in self.resultlist[concept]:
                self.completerClassList["completerClassList"][self.resultlist[concept]["concept"][self.resultlist[concept]["concept"].rfind('/') + 1:]] = "wd:" + \
                                                                                                  item.text().split(
                                                                                                      "(")[
                                                                                                      1].replace(
                                                                                                      " ",
                                                                                                      "_").replace(
                                                                                                      ")", "")
            else:
                self.completerClassList["completerClassList"][
                    item.text()] = "<" + str(self.resultlist[concept]["concept"]) + ">"
        self.sparql.updateNewClassList()
        self.geoClassListGui.selectionModel().setCurrentIndex(self.geoClassList.index(0, 0),
                                                              QItemSelectionModel.SelectCurrent)
        self.dlg.currentProxyModel = self.dlg.geoTreeViewProxyModel
        self.dlg.currentContext = self.dlg.geoTreeView
        self.dlg.currentContextModel = self.dlg.geoTreeViewModel
        self.dlg.conceptSelectAction()