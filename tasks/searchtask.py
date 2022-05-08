import json
import requests

from ..dialogs.errormessagebox import ErrorMessageBox
from ..util.ui.uiutils import UIUtils
from ..util.sparqlutils import SPARQLUtils
from qgis.utils import iface
from qgis.core import Qgis,QgsTask, QgsMessageLog
from qgis.PyQt.QtWidgets import QListWidgetItem, QMessageBox

MESSAGE_CATEGORY = 'Search Class/Property Task'

class SearchTask(QgsTask):


    def __init__(self, description, triplestoreurl, query, triplestoreconf, findProperty, tripleStoreEdit, searchResult,
                 prefixes, label, language, progress):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress = progress
        self.triplestoreurl = triplestoreurl
        self.triplestoreconf = triplestoreconf
        self.query = query
        self.label = label
        self.language = language
        self.findProperty = findProperty
        self.tripleStoreEdit = tripleStoreEdit
        self.searchResult = searchResult
        self.prefixes = prefixes
        self.results = {}

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        labelproperty="http://www.w3.org/2000/01/rdf-schema#label"
        if "labelproperty" in self.triplestoreconf and self.triplestoreconf["labelproperty"]!=None and self.triplestoreconf["labelproperty"].startswith("http"):
            labelproperty=self.triplestoreconf["labelproperty"]
        if self.findProperty.isChecked():
            if "propertyfromlabelquery" in self.triplestoreconf[self.tripleStoreEdit.currentIndex()]:
                self.query = self.triplestoreconf[self.tripleStoreEdit.currentIndex()][
                    "propertyfromlabelquery"].replace("%%label%%", self.label).replace("%%language%%", self.language)
            else:
                self.query="SELECT DISTINCT ?class ?label { ?ind ?class ?obj . ?class <"+str(labelproperty)+"> ?label . FILTER (lang(?label) = '%%language%%') FILTER(CONTAINS(?label,\"%%label%%\"))} LIMIT 100".replace("%%label%%", self.label).replace("%%language%%", self.language)
        else:
            if "classfromlabelquery" in self.triplestoreconf[self.tripleStoreEdit.currentIndex()]:
                self.query = self.triplestoreconf[self.tripleStoreEdit.currentIndex()][
                    "classfromlabelquery"].replace("%%label%%", self.label).replace("%%language%%", self.language)
            else:
                self.query="SELECT DISTINCT ?class ?label { ?ind <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?class . ?class <"+str(labelproperty)+"> ?label . FILTER (lang(?label) = '%%language%%') FILTER(CONTAINS(?label,\"%%label%%\"))} LIMIT 100".replace("%%label%%", self.label).replace("%%language%%", self.language)
        QgsMessageLog.logMessage('Started task "{}" Query:'.format(self.query), MESSAGE_CATEGORY, Qgis.Info)
        if self.query == "" or self.query==None:
            return
        if "SELECT" in self.query:
            self.query = self.query.replace("%%label%%", self.label).replace("%%language%%", self.language)
            self.results = SPARQLUtils.executeQuery(self.triplestoreurl,
                                               self.prefixes[self.tripleStoreEdit.currentIndex()] + self.query,
                                                    self.triplestoreconf[self.tripleStoreEdit.currentIndex()])
            if self.results == False:
                return False
        else:
            QgsMessageLog.logMessage('Started task "{}" Query:'.format(self.query), MESSAGE_CATEGORY, Qgis.Info)
            myResponse = json.loads(requests.get(self.query).text)
            self.qids = []
            QgsMessageLog.logMessage('Started task "{}" Query:'.format(myResponse), MESSAGE_CATEGORY, Qgis.Info)
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
        return True

    def finished(self, result):
        if self.query == "":
            msgBox = QMessageBox()
            msgBox.setWindowTitle("No search query specified")
            msgBox.setText("No search query specified for this triplestore")
            msgBox.exec()
            return
        if "SELECT" in self.query:
            if self.results==False:
                msgBox = ErrorMessageBox("Error while performing search","")
                msgBox.setText("An error occured while performing the search:\n"+str(SPARQLUtils.exception))
                msgBox.exec()
                return
            if len(self.results["results"]) == 0 or len(self.results["results"]["bindings"]) == 0:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("Empty search result")
                msgBox.setText("The search yielded no results")
                msgBox.exec()
                return
            for res in self.results["results"]["bindings"]:
                item = QListWidgetItem()
                if not self.findProperty.isChecked():
                    item.setIcon(UIUtils.classicon)
                else:
                    item.setIcon(UIUtils.objectpropertyicon)
                item.setToolTip(res["class"]["value"])
                item.setData(256, str(res["class"]["value"]))
                if "label" in res:
                    item.setText(str(res["label"]["value"] + " (" + res["class"]["value"] + ")"))
                else:
                    item.setText(str(res["class"]["value"]))
                self.searchResult.addItem(item)
        else:
            i = 0
            for result in self.results:
                item = QListWidgetItem()
                if not self.findProperty.isChecked():
                    item.setIcon(UIUtils.classicon)
                else:
                    item.setIcon(UIUtils.objectpropertyicon)
                item.setData(256, self.qids[i])
                item.setToolTip(self.qids[i])
                item.setText(str(self.results[result]))
                self.searchResult.addItem(item)
                i += 1
        iface.messageBar().pushMessage("Searched for concepts in", "OK", level=Qgis.Success)
