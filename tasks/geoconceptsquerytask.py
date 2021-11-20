from ..util.sparqlutils import SPARQLUtils
from qgis.core import Qgis
from qgis.PyQt.QtCore import QSettings, QItemSelectionModel
from qgis.PyQt.QtGui import QStandardItem,QStandardItemModel,QColor,QIcon
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
)

MESSAGE_CATEGORY = 'GeoConceptsQueryTask'


class GeoConceptsQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl, query, triplestoreconf, sparql, queryvar, getlabels, layercount,
                 geoClassList, examplequery, geoClassListGui, completerClassList, dlg):
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
        self.geoClassListGui = geoClassListGui
        self.amountoflabels = -1
        self.geoClassList = geoClassList
        self.geoTreeViewModel=self.dlg.geoTreeViewModel
        self.examplequery = examplequery
        self.resultlist = []
        self.viewlist = []

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        results = SPARQLUtils.executeQuery(self.triplestoreurl,self.query,self.triplestoreconf)
        if results==False:
            return False
        for result in results["results"]["bindings"]:
            self.viewlist.append(str(result[self.queryvar]["value"]))
        print(self.viewlist)
        if self.getlabels and "classlabelquery" in self.triplestoreconf and self.triplestoreconf[
            "classlabelquery"] != "":
            labels = SPARQLUtils.getLabelsForClasses(self.viewlist, self.triplestoreconf["classlabelquery"],self.triplestoreconf,self.triplestoreurl)
            print(labels)
            self.amountoflabels = len(labels)
            i = 0
            sorted_labels = sorted(labels.items(), key=lambda x: x[1])
            for lab in sorted_labels:
                self.resultlist.append(labels[lab[0]] + " (" + lab[0] + ")")
                i = i + 1
        return True

    def finished(self, result):
        self.geoClassList.clear()
        self.geoTreeViewModel.clear()
        self.rootNode=self.geoTreeViewModel.invisibleRootItem()
        self.dlg.conceptViewTabWidget.setTabText(0, "GeoConcepts (" + str(len(self.viewlist)) + ")")
        if self.examplequery != None:
            self.sparql.setPlainText(self.examplequery)
            self.sparql.columnvars = {}
        if len(self.resultlist) > 0:
            first = True
            for concept in self.resultlist:
                # self.layerconcepts.addItem(concept)
                item = QStandardItem()
                item.setData(concept, 256)
                item.setText(concept[concept.rfind('/') + 1:])
                item.setForeground(QColor(0,0,0))
                item.setEditable(False)
                item.setIcon(SPARQLUtils.geoclassicon)
                item.setData(SPARQLUtils.geoclassnode, 257)
                #item.appendRow(QStandardItem("Child"))
                self.rootNode.appendRow(item)
                if self.triplestoreconf["name"] == "Wikidata":
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
            self.dlg.viewselectactionGeoTree()
        elif len(self.viewlist) > 0:
            for concept in self.viewlist:
                # self.layerconcepts.addItem(concept)
                item = QStandardItem()
                item.setData(concept, 256)
                item.setText(concept[concept.rfind('/') + 1:])
                item.setForeground(QColor(0,0,0))
                item.setEditable(False)
                item.setIcon(SPARQLUtils.geoclassicon)
                item.setData(SPARQLUtils.geoclassnode, 257)
                #item.appendRow(QStandardItem("Child"))
                self.rootNode.appendRow(item)
                if self.triplestoreconf["name"] == "Wikidata":
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
                # item=QListWidgetItem()
                # item.setData(1,concept)
                # item.setText(concept[concept.rfind('/')+1:])
                # self.geoClassList.addItem(item)
            self.sparql.updateNewClassList()
            self.geoClassListGui.selectionModel().setCurrentIndex(self.geoClassList.index(0, 0),
                                                                  QItemSelectionModel.SelectCurrent)
            self.dlg.viewselectactionGeoTree()
        if self.amountoflabels != -1:
            self.layercount.setText("[" + str(self.amountoflabels) + "]")
