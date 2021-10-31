import urllib
from qgis.core import Qgis
from qgis.PyQt.QtCore import QSettings, QItemSelectionModel
from qgis.PyQt.QtGui import QStandardItem
from SPARQLWrapper import SPARQLWrapper, JSON, GET
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
)

MESSAGE_CATEGORY = 'GeoCollectionsQueryTask'


class GeoCollectionsQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl, query, triplestoreconf, sparql, queryvar, labelvar, featureOrGeoCollection, layercount,
                 geoClassList, examplequery, geoClassListGui, completerClassList, dlg):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.triplestoreconf = triplestoreconf
        self.query = query
        self.dlg = dlg
        self.layercount = layercount
        self.labelvar = labelvar
        self.classvar = queryvar
        self.featureOrGeoCollection=featureOrGeoCollection
        self.completerClassList = completerClassList
        self.completerClassList["completerClassList"] = {}
        self.queryvar = queryvar
        self.sparql = sparql
        self.geoClassListGui = geoClassListGui
        self.amountoflabels = -1
        self.geoClassList = geoClassList
        self.examplequery = examplequery
        self.resultlist = []
        self.viewlist = []
        s = QSettings()  # getting proxy from qgis options settings
        self.proxyEnabled = s.value("proxy/proxyEnabled")
        self.proxyType = s.value("proxy/proxyType")
        self.proxyHost = s.value("proxy/proxyHost")
        self.proxyPort = s.value("proxy/proxyPort")
        self.proxyUser = s.value("proxy/proxyUser")
        self.proxyPassword = s.value("proxy/proxyPassword")

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        if self.proxyHost != None and self.proxyHost != "" and self.proxyPort != None and self.proxyPort != "":
            QgsMessageLog.logMessage('Proxy? ' + str(self.proxyHost), MESSAGE_CATEGORY, Qgis.Info)
            proxy = urllib.request.ProxyHandler({'http': self.proxyHost})
            opener = urllib.request.build_opener(proxy)
            urllib.request.install_opener(opener)
        sparql = SPARQLWrapper(self.triplestoreurl,
                               agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
        print(str(self.query))
        sparql.setQuery(self.query)
        print("now sending query")
        print(self.triplestoreurl)
        sparql.setMethod(GET)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            viewlistentry={}
            if self.queryvar in result:
                self.viewlist.append(viewlistentry)
                viewlistentry["uri"]=str(result[self.queryvar]["value"])
                if self.labelvar in result:
                    viewlistentry["label"]=str(result[self.labelvar]["value"])
                if self.classvar in result:
                    viewlistentry["class"] = str(result[self.classvar]["value"])
        print(self.viewlist)
        return True

    def finished(self, result):
        self.geoClassList.clear()
        if len(self.resultlist) > 0:
            first = True
            for concept in self.resultlist:
                # self.layerconcepts.addItem(concept)
                item = QStandardItem()
                item.setData(concept["uri"], 1)
                if "class" in concept:
                    item.setText(concept["uri"][concept["uri"].rfind('/') + 1:]+" ("+concept["uri"][concept["uri"].rfind('/') + 1:]+")")
                else:
                    item.setText(concept["uri"][concept["uri"].rfind('/') + 1:])
                self.geoClassList.appendRow(item)
            self.sparql.updateNewClassList()
            self.geoClassListGui.selectionModel().setCurrentIndex(self.geoClassList.index(0, 0),
                                                                  QItemSelectionModel.SelectCurrent)
            self.dlg.viewselectaction()
        elif len(self.viewlist) > 0:
            for concept in self.viewlist:
                # self.layerconcepts.addItem(concept)
                item = QStandardItem()
                item.setData(concept, 1)
                item.setText(concept[concept.rfind('/') + 1:])
                self.geoClassList.appendRow(item)
            self.sparql.updateNewClassList()
            self.geoClassListGui.selectionModel().setCurrentIndex(self.geoClassList.index(0, 0),
                                                                  QItemSelectionModel.SelectCurrent)
            self.dlg.viewselectaction()
        if self.amountoflabels != -1:
            self.layercount.setText("[" + str(self.amountoflabels) + "]")
