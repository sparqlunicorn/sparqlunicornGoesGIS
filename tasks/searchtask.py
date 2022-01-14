import json
import requests
from ..util.sparqlutils import SPARQLUtils
from qgis.utils import iface
from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QListWidgetItem, QMessageBox
from qgis.core import (
    QgsTask, QgsMessageLog,
)

MESSAGE_CATEGORY = 'Search Class/Property Task'


class SearchTask(QgsTask):
    """This shows how to subclass QgsTask"""

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
        if self.findProperty.isChecked():
            if "propertyfromlabelquery" in self.triplestoreconf[self.tripleStoreEdit.currentIndex() + 1]:
                self.query = self.triplestoreconf[self.tripleStoreEdit.currentIndex() + 1][
                    "propertyfromlabelquery"].replace("%%label%%", self.label)
        else:
            if "classfromlabelquery" in self.triplestoreconf[self.tripleStoreEdit.currentIndex() + 1]:
                self.query = self.triplestoreconf[self.tripleStoreEdit.currentIndex() + 1][
                    "classfromlabelquery"].replace("%%label%%", self.label)
        if self.query == "":
            return
        if "SELECT" in self.query:
            self.query = self.query.replace("%%label%%", self.label).replace("%%language%%", self.language)
            self.results = SPARQLUtils.executeQuery(self.triplestoreurl,
                                               self.prefixes[self.tripleStoreEdit.currentIndex() + 1] + self.query,self.triplestoreconf[self.tripleStoreEdit.currentIndex() + 1])
            if self.results == False:
                return False
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
        if self.query == "":
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
            i = 0
            for result in self.results:
                item = QListWidgetItem()
                item.setData(1, self.qids[i])
                item.setText(str(self.results[result]))
                self.searchResult.addItem(item)
                i += 1
        iface.messageBar().pushMessage("Searched for concepts in", "OK", level=Qgis.Success)
