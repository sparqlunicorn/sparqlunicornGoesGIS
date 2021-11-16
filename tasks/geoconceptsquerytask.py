from ..util.sparqlutils import SPARQLUtils
from qgis.core import Qgis
from qgis.PyQt.QtCore import QSettings, QItemSelectionModel, QSortFilterProxyModel, Qt
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
        self.dlg.geoTreeView.setModel(None)
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
            labels = SPARQLUtils.getLabelsForClasses(self.viewlist, self.dlg.triplestoreconf["classlabelquery"],self.dlg.triplestoreconf,self.triplestoreurl)
            print(labels)
            self.amountoflabels = len(labels)
            i = 0
            sorted_labels = sorted(labels.items(), key=lambda x: x[1])
            for lab in sorted_labels:
                self.resultlist.append(labels[lab[0]] + " (" + lab[0] + ")")
                i = i + 1
        self.dlg.geoTreeViewModel=QStandardItemModel()
        self.dlg.proxyModel = QSortFilterProxyModel()
        self.dlg.proxyModel.sort(0)
        self.dlg.proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.dlg.proxyModel.setSourceModel(self.dlg.geoTreeViewModel)
        self.rootNode=self.dlg.geoTreeViewModel.invisibleRootItem()
        if len(self.resultlist) > 0:
            first = True
            for concept in self.resultlist:
                item = QStandardItem()
                item.setData(concept, 256)
                item.setText(concept[concept.rfind('/') + 1:])
                item.setEditable(False)
                item.setIcon(QIcon(":/icons/resources/icons/geoclass.png"))
                item.setData("GeoClass", 257)
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
        elif len(self.viewlist) > 0:
            for concept in self.viewlist:
                item = QStandardItem()
                item.setData(concept, 256)
                item.setText(concept[concept.rfind('/') + 1:])
                item.setEditable(False)
                item.setIcon(QIcon(":/icons/resources/icons/geoclass.png"))
                item.setData("GeoClass", 257)
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
        return True

    def finished(self, result):
        if self.examplequery != None:
            self.sparql.setPlainText(self.examplequery)
            self.sparql.columnvars = {}
        self.dlg.conceptViewTabWidget.setTabText(0, "GeoConcepts (" + str(len(self.viewlist)) + ")")
        self.dlg.geoTreeView.setModel(self.dlg.proxyModel)
        if self.amountoflabels != -1:
            self.layercount.setText("[" + str(self.amountoflabels) + "]")
