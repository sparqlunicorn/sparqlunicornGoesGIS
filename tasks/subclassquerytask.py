import json
import requests
import urllib
from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QStyle
from qgis.PyQt.QtCore import QSettings, QItemSelectionModel
from qgis.PyQt.QtGui import QStandardItem,QStandardItemModel,QColor
from SPARQLWrapper import SPARQLWrapper, JSON, GET
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog
)

MESSAGE_CATEGORY = 'SubClassQueryTask'

class SubClassQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl, query, progress,dlg,treeNode):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress=progress
        self.triplestoreurl = triplestoreurl
        self.query = query
        self.dlg=dlg
        self.treeNode=treeNode
        self.amountoflabels = -1
        self.geoTreeViewModel=self.dlg.geoTreeViewModel
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
        QgsMessageLog.logMessage('Started task "{}"'.format(self.query), MESSAGE_CATEGORY, Qgis.Info)
        sparql.setQuery(self.query)
        sparql.setMethod(GET)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        QgsMessageLog.logMessage('Started task "{}"'.format(results), MESSAGE_CATEGORY, Qgis.Info)
        for result in results["results"]["bindings"]:
            self.viewlist.append(str(result["subclass"]["value"]))
        print(self.viewlist)
        QgsMessageLog.logMessage('Started task "{}"'.format(self.viewlist), MESSAGE_CATEGORY, Qgis.Info)
        # self.layercount.setText("["+str(len(viewlist))+"]")
        if "classlabelquery" in self.dlg.triplestoreconf and self.dlg.triplestoreconf[
            "classlabelquery"] != "":
            labels = self.getLabelsForClasses(self.viewlist, self.dlg.triplestoreconf["classlabelquery"])
            print(labels)
            self.amountoflabels = len(labels)
            i = 0
            sorted_labels = sorted(labels.items(), key=lambda x: x[1])
            for lab in sorted_labels:
                self.resultlist.append(labels[lab[0]] + " (" + lab[0] + ")")
                i = i + 1
        return True

    ## Executes a SPARQL endpoint specific query to find labels for given classes. The query may be configured in the configuration file.
    #  @param self The object pointer.
    #  @param classes array of classes to find labels for
    #  @param query the class label query
    def getLabelsForClasses(self, classes, query):
        result = {}
        query = self.triplestoreconf["classlabelquery"]
        # url="https://www.wikidata.org/w/api.php?action=wbgetentities&props=labels&ids="
        if "SELECT" in query:
            vals = "VALUES ?class { "
            for qid in classes:
                vals += qid + " "
            vals += "}\n"
            query = query.replace("%%concepts%%", vals)
            sparql = SPARQLWrapper(self.triplestoreurl,
                                   agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
            sparql.setQuery(query)
            sparql.setMethod(GET)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            for res in results["results"]["bindings"]:
                result[res["class"]["value"]] = res["label"]["value"]
        else:
            url = self.triplestoreconf["classlabelquery"]
            i = 0
            qidquery = ""
            for qid in classes:
                if "Q" in qid:
                    qidquery += "Q" + qid.split("Q")[1]
                if (i % 50) == 0:
                    print(url.replace("%%concepts%%", qidquery))
                    myResponse = json.loads(requests.get(url.replace("%%concepts%%", qidquery)).text)
                    print(myResponse)
                    for ent in myResponse["entities"]:
                        print(ent)
                        if "en" in myResponse["entities"][ent]["labels"]:
                            result[ent] = myResponse["entities"][ent]["labels"]["en"]["value"]
                    qidquery = ""
                else:
                    qidquery += "|"
                i = i + 1
        return result

    def finished(self, result):
        if len(self.resultlist) > 0:
            first = True
            for concept in self.resultlist:
                item = QStandardItem()
                item.setData(concept, 256)
                item.setText(concept[concept.rfind('/') + 1:])
                item.setForeground(QColor(0,0,0))
                item.setEditable(False)
                item.setIcon(self.dlg.style().standardIcon(getattr(QStyle, "SP_ToolBarHorizontalExtensionButton")))
                self.treeNode.appendRow(item)
        elif len(self.viewlist) > 0:
            for concept in self.viewlist:
                item = QStandardItem()
                item.setData(concept, 256)
                item.setText(concept[concept.rfind('/') + 1:])
                item.setForeground(QColor(0,0,0))
                item.setEditable(False)
                item.setIcon(self.dlg.style().standardIcon(getattr(QStyle, "SP_ToolBarHorizontalExtensionButton")))
                self.treeNode.appendRow(item)
        if self.amountoflabels != -1:
            self.layercount.setText("[" + str(self.amountoflabels) + "]")