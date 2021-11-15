import json
import requests
from ..util.sparqlutils import SPARQLUtils
from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QTableWidgetItem, QMessageBox, QProgressDialog, QPushButton
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
)

MESSAGE_CATEGORY = 'DataSchemaQueryTask'

class DataSchemaQueryTask(QgsTask):
    """This shows how to subclass QgsTask"""

    def __init__(self, description, triplestoreurl, query, searchTerm, prefixes, searchResult,triplestoreconf, progress,graph=None):
        super().__init__(description, QgsTask.CanCancel)
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.query = query
        self.progress = progress
        self.prefixes = prefixes
        self.labels = None
        self.triplestoreconf=triplestoreconf
        self.graph=graph
        self.progress = progress
        self.urilist = None
        self.sortedatt = None
        self.searchTerm = searchTerm
        self.searchResult = searchResult
        self.results = None

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        QgsMessageLog.logMessage('Started task "{}"'.format(self.searchTerm), MESSAGE_CATEGORY, Qgis.Info)
        if self.searchTerm == "":
            return False
        concept = "<" + self.searchTerm + ">"
        if self.graph==None:
            results = SPARQLUtils.executeQuery(self.triplestoreurl,"".join(self.prefixes) + self.query,self.triplestoreconf)
        else:
            results=self.graph.query("".join(self.prefixes) + self.query)
        if results == False:
            return False
        self.searchResult.clear()
        if len(results["results"]["bindings"]) == 0:
            return False
        maxcons = int(results["results"]["bindings"][0]["countcon"]["value"])
        attlist = {}
        self.urilist = {}
        for result in results["results"]["bindings"]:
            if maxcons!=0 and str(maxcons)!="0":
                attlist[result["rel"]["value"][result["rel"]["value"].rfind('/') + 1:]] = round(
                    (int(result["countrel"]["value"]) / maxcons) * 100, 2)
                self.urilist[result["rel"]["value"][result["rel"]["value"].rfind('/') + 1:]] = result["rel"]["value"]
        self.sortedatt = sorted(attlist.items(), reverse=True, key=lambda kv: kv[1])
        self.labels = {}
        postdata = {}
        postdata["language"] = "en"
        postdata["format"] = "json"
        postdata["action"] = "wbgetentities"
        atts = [""]
        attcounter = 0
        count = 0
        for att in attlist.keys():
            if att.startswith("P") and count < 50:
                atts[attcounter] += att + "|"
                count += 1
        atts[0] = atts[0][:-1]
        i = 0
        for att in atts:
            url = "https://www.wikidata.org/w/api.php"  # ?action=wbgetentities&format=json&language=en&ids="+atts
            postdata["ids"] = att
            # msgBox=QMessageBox()
            # msgBox.setText(str(postdata))
            # msgBox.exec()
            myResponse = json.loads(requests.post(url, postdata).text)
            # msgBox=QMessageBox()
            # msgBox.setText(str(myResponse))
            # msgBox.exec()
            for ent in myResponse["entities"]:
                print(ent)
                if "en" in myResponse["entities"][ent]["labels"]:
                    self.labels[ent] = myResponse["entities"][ent]["labels"]["en"]["value"]
                i = i + 1
        return True

    def finished(self, result):
        while self.searchResult.rowCount()>0:
            self.searchResult.removeRow(0)
        self.searchResult.setHorizontalHeaderLabels(["Attribute", "Sample Instances"])
        if self.sortedatt != None:
            if len(self.sortedatt)==0:
                self.searchResult.insertRow(0)
                item = QTableWidgetItem()
                item.setText("No results found")
                self.searchResult.setItem(0,0,item)
            else:
                counter=0
                for att in self.sortedatt:
                    if att[1] < 1:
                        continue
                    if att[0] in self.labels:
                        self.searchResult.insertRow(counter)
                        item = QTableWidgetItem()
                        item.setText(self.labels[att[0]] + " (" + str(att[1]) + "%)")
                        item.setData(256, self.urilist[att[0]])
                        self.searchResult.setItem(counter, 0, item)
                        itembutton = QTableWidgetItem()
                        itembutton.setText("Click to load samples...")
                        self.searchResult.setItem(counter, 1, itembutton)
                    else:
                        self.searchResult.insertRow(counter)
                        item = QTableWidgetItem()
                        item.setText(att[0] + " (" + str(att[1]) + "%)")
                        item.setData(256, self.urilist[att[0]])
                        self.searchResult.setItem(counter, 0, item)
                        itembutton = QTableWidgetItem()
                        itembutton.setText("Click to load samples...")
                        self.searchResult.setItem(counter, 1, itembutton)
                    counter += 1
                """
                self.searchResult.insertRow(counter)
                item = QTableWidgetItem()
                item.setText("Associated styles")
                item.setData(256, self.searchTerm)
                self.searchResult.setItem(counter, 0, item)
                itembutton = QTableWidgetItem()
                itembutton.setText("Click to load styles...")
                self.searchResult.setItem(counter, 1, itembutton)
                """
        else:
            msgBox = QMessageBox()
            msgBox.setText("The enrichment search query did not yield any results!")
            msgBox.exec()
        self.progress.close()
