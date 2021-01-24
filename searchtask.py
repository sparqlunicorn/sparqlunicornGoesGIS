from time import sleep
from rdflib import *
import json
import requests
import urllib
from qgis.PyQt.QtCore import QSettings
from qgis.utils import iface
from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QListWidgetItem,QMessageBox,QProgressDialog
from rdflib.plugins.sparql import prepareQuery
from SPARQLWrapper import SPARQLWrapper, JSON, POST, GET
from qgis.core import QgsProject,QgsGeometry,QgsVectorLayer,QgsExpression,QgsFeatureRequest,QgsCoordinateReferenceSystem,QgsCoordinateTransform,QgsApplication,QgsWkbTypes,QgsField
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
    )

MESSAGE_CATEGORY = 'Search Class/Property Task'

class SearchTask(QgsTask):
    """This shows how to subclass QgsTask"""

    def __init__(self, description, triplestoreurl,query,triplestoreconf,findProperty,tripleStoreEdit,searchResult,prefixes,label,language,progress):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress=progress
        self.triplestoreurl=triplestoreurl
        self.triplestoreconf=triplestoreconf
        self.query=query
        self.label=label
        self.language=language
        self.findProperty=findProperty
        self.tripleStoreEdit=tripleStoreEdit
        self.searchResult=searchResult
        self.prefixes=prefixes
        self.results={}
        s = QSettings() #getting proxy from qgis options settings
        self.proxyEnabled = s.value("proxy/proxyEnabled")
        self.proxyType = s.value("proxy/proxyType")
        self.proxyHost = s.value("proxy/proxyHost")
        self.proxyPort = s.value("proxy/proxyPort")
        self.proxyUser = s.value("proxy/proxyUser")
        self.proxyPassword = s.value("proxy/proxyPassword")

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()),MESSAGE_CATEGORY, Qgis.Info)
        if self.proxyHost!=None and self.proxyHost!="" and self.proxyPort!=None and self.proxyPort!="":
            QgsMessageLog.logMessage('Proxy? '+str(self.proxyHost), MESSAGE_CATEGORY, Qgis.Info)
            proxy = urllib.ProxyHandler({'http': proxyHost})
            opener = urllib.build_opener(proxy)
            urllib.install_opener(opener)
        #msgBox=QMessageBox()
        #msgBox.setText(self.query+" - "+self.triplestoreconf[self.tripleStoreEdit.currentIndex()+1]["endpoint"])
        #msgBox.exec()
        if self.findProperty.isChecked():
            if "propertyfromlabelquery" in self.triplestoreconf[self.tripleStoreEdit.currentIndex() + 1]:
                self.query = self.triplestoreconf[self.tripleStoreEdit.currentIndex() + 1]["propertyfromlabelquery"].replace("%%label%%", self.label)
        else:
            if "classfromlabelquery" in self.triplestoreconf[self.tripleStoreEdit.currentIndex() + 1]:
                self.query = self.triplestoreconf[self.tripleStoreEdit.currentIndex() + 1]["classfromlabelquery"].replace("%%label%%", self.label)
        if self.query == "":
            return
        if "SELECT" in self.query:
            self.query = self.query.replace("%%label%%", self.label).replace("%%language%%", self.language)
            sparql = SPARQLWrapper(self.triplestoreconf[self.tripleStoreEdit.currentIndex() + 1]["endpoint"], agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
            sparql.setQuery(self.prefixes[self.tripleStoreEdit.currentIndex() + 1] + self.query)
            sparql.setReturnFormat(JSON)
            self.results = sparql.query().convert()
            # msgBox=QMessageBox()
            # msgBox.setText(str(results))
            # msgBox.exec()
            for res in self.results["results"]["bindings"]:
                item = QListWidgetItem()
                item.setData(1, str(res["class"]["value"]))
                if "label" in res:
                    item.setText(str(res["label"]["value"] + " (" + res["class"]["value"] + ")"))
                else:
                    item.setText(str(res["class"]["value"]))
                self.searchResult.addItem(item)
        else:
            myResponse = json.loads(requests.get(self.query).text)
            self.qids = []
            for ent in myResponse["search"]:
                qid = ent["concepturi"]
                if "http://www.wikidata.org/entity/" in qid and self.findProperty.isChecked():
                    qid = "http://www.wikidata.org/prop/direct/" + ent["id"]
                elif "http://www.wikidata.org/wiki/" in qid and self.findConcept.isChecked():
                    qid = "http://www.wikidata.org/entity/" + ent["id"]
                self.qids.append(qid)
                label = ent["label"] + " (" + ent["id"] + ") "
                if "description" in ent:
                    label += "[" + ent["description"] + "]"
                self.results[qid] = label    
        
    def finished(self, result):
        if self.query=="":
            msgBox = QMessageBox()
            msgBox.setWindowTitle("No search query specified")
            msgBox.setText("No search query specified for this triplestore")
            msgBox.exec()
            return
        if "SELECT" in self.query:
            if len(self.results["results"]) == 0 or len(self.results["results"]["bindings"]) == 0:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("Empty search result")
                msgBox.setText("The search yielded no results")
                msgBox.exec()
                return
            for res in self.results["results"]["bindings"]:
                item = QListWidgetItem()
                item.setData(1, str(res["class"]["value"]))
                if "label" in res:
                    item.setText(str(res["label"]["value"] + " (" + res["class"]["value"] + ")"))
                else:
                    item.setText(str(res["class"]["value"]))
                self.searchResult.addItem(item)
        else:
            i=0
            for result in self.results:
                item = QListWidgetItem()
                item.setData(1, self.qids[i])
                item.setText(str(self.results[result]))
                self.searchResult.addItem(item)
                i += 1
        iface.messageBar().pushMessage("Searched for concepts in", "OK", level=Qgis.Success)
