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
        self.resultlist = []
        self.viewlist = []

    def run(self):
        #QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        results = SPARQLUtils.executeQuery(self.triplestoreurl,self.query,self.triplestoreconf)
        if results==False:
            return False
        for result in results["results"]["bindings"]:
            self.viewlist.append(str(result[self.queryvar]["value"]))
        print(self.viewlist)
        if self.getlabels and "labelproperty" in self.triplestoreconf and self.triplestoreconf[
            "labelproperty"] != "":
            if "classlabelquery" in self.triplestoreconf:
                labels = SPARQLUtils.getLabelsForClasses(self.viewlist, self.triplestoreconf["classlabelquery"],self.triplestoreconf,self.triplestoreurl,self.preferredlang)
            else:
                labels = SPARQLUtils.getLabelsForClasses(self.viewlist, None,
                                                         self.triplestoreconf, self.triplestoreurl,self.preferredlang)
            #QgsMessageLog.logMessage('Started task "{}"'.format(str(labels)), MESSAGE_CATEGORY, Qgis.Info)
            self.amountoflabels = len(labels)
            i = 0
            self.resultlist=[]
            for lab in labels:
                self.resultlist.append({"label":labels[lab] + " ("+SPARQLUtils.labelFromURI(lab,self.triplestoreconf["prefixesrev"]) + ")","concept":self.viewlist[i]})
                i = i + 1
            #QgsMessageLog.logMessage('Started task "{}"'.format(str(self.resultlist)), MESSAGE_CATEGORY, Qgis.Info)
        return True

    def finished(self, result):
        self.geoClassList.clear()
        self.geoTreeViewModel.clear()
        self.geoClassListGui.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.geoClassListGui.header().setStretchLastSection(False)
        self.geoClassListGui.header().setMinimumSectionSize(self.dlg.classTreeView.width())
        self.rootNode=self.geoTreeViewModel.invisibleRootItem()
        self.dlg.conceptViewTabWidget.setTabText(0, "GeoConcepts (" + str(len(self.viewlist)) + ")")
        if self.examplequery != None:
            self.sparql.setPlainText(self.examplequery)
            self.sparql.columnvars = {}
        if len(self.resultlist) > 0:
            for concept in self.resultlist:
                item = QStandardItem()
                item.setData(concept["concept"], 256)
                item.setText(SPARQLUtils.labelFromURI(concept["label"],self.triplestoreconf["prefixesrev"]))
                item.setForeground(QColor(0,0,0))
                item.setEditable(False)
                item.setIcon(UIUtils.geoclassicon)
                item.setData(SPARQLUtils.geoclassnode, 257)
                item.setToolTip("GeoClass "+str(item.text())+": <br>"+SPARQLUtils.treeNodeToolTip)
                self.rootNode.appendRow(item)
                if self.triplestoreconf["name"] == "Wikidata":
                    self.completerClassList["completerClassList"][concept["concept"][concept["concept"].rfind('/') + 1:]] = "wd:" + \
                                                                                                      concept["label"].split(
                                                                                                          "(")[
                                                                                                          1].replace(
                                                                                                          " ",
                                                                                                          "_").replace(
                                                                                                          ")", "")
                else:
                    self.completerClassList["completerClassList"][
                        item.text()] = "<" + str(concept["concept"]) + ">"
        elif len(self.viewlist) > 0:
            for concept in self.viewlist:
                item = QStandardItem()
                item.setData(concept, 256)
                item.setText(SPARQLUtils.labelFromURI(concept,self.triplestoreconf["prefixesrev"]))
                item.setForeground(QColor(0,0,0))
                item.setEditable(False)
                item.setIcon(UIUtils.geoclassicon)
                item.setData(SPARQLUtils.geoclassnode, 257)
                item.setToolTip("GeoClass "+str(item.text())+": <br>"+SPARQLUtils.treeNodeToolTip)
                self.rootNode.appendRow(item)
                if self.triplestoreconf["name"] == "Wikidata" and "(" in concept:
                    self.completerClassList["completerClassList"][concept[concept.rfind('/') + 1:]] = "wd:" + \
                                                                                                      concept.split(
                                                                                                          "(")[
                                                                                                          1].replace(
                                                                                                          " ",
                                                                                                          "_").replace(
                                                                                                          ")", "")
                else:
                    self.completerClassList["completerClassList"][
                        concept[concept.rfind('/') + 1:]] = "<" + concept + ">"
        self.sparql.updateNewClassList()
        self.geoClassListGui.selectionModel().setCurrentIndex(self.geoClassList.index(0, 0),
                                                              QItemSelectionModel.SelectCurrent)
        self.dlg.currentProxyModel = self.dlg.geoTreeViewProxyModel
        self.dlg.currentContext = self.dlg.geoTreeView
        self.dlg.currentContextModel = self.dlg.geoTreeViewModel
        self.dlg.conceptSelectAction()