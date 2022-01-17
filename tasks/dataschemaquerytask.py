from collections.abc import Iterable
from ..util.sparqlutils import SPARQLUtils
from qgis.core import Qgis
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QTableWidgetItem, QMessageBox
from qgis.core import (
    QgsTask, QgsMessageLog,
)

MESSAGE_CATEGORY = 'DataSchemaQueryTask'

class DataSchemaQueryTask(QgsTask):
    """This shows how to subclass QgsTask"""

    def __init__(self, description, triplestoreurl, query, searchTerm, prefixes, searchResult,triplestoreconf, progress):
        super().__init__(description, QgsTask.CanCancel)
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.query = query
        self.progress = progress
        self.prefixes = prefixes
        self.labels = None
        self.triplestoreconf=triplestoreconf
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
        if isinstance(self.prefixes, Iterable):
            results = SPARQLUtils.executeQuery(self.triplestoreurl,"".join(self.prefixes) + self.query,self.triplestoreconf)
        else:
            results = SPARQLUtils.executeQuery(self.triplestoreurl, str(self.prefixes).replace("None","") + self.query,
                                                   self.triplestoreconf)
        if results == False:
            return False
        self.searchResult.clear()
        if len(results["results"]["bindings"]) == 0:
            return False
        maxcons = int(results["results"]["bindings"][0]["countcon"]["value"])
        self.sortedatt = {}
        for result in results["results"]["bindings"]:
            if maxcons!=0 and str(maxcons)!="0":
                self.sortedatt[result["rel"]["value"][result["rel"]["value"].rfind('/') + 1:]] = {"amount": round(
                    (int(result["countrel"]["value"]) / maxcons) * 100, 2), "concept":result["rel"]["value"]}
                if "valtype" in result and result["valtype"]["value"]!="":
                    self.sortedatt[result["rel"]["value"][result["rel"]["value"].rfind('/') + 1:]]["valtype"]=result["valtype"]["value"]
        self.labels={}
        if "propertylabelquery" in self.triplestoreconf:
            self.labels=SPARQLUtils.getLabelsForClasses(self.sortedatt.keys(), self.triplestoreconf["propertylabelquery"], self.triplestoreconf,
                                        self.triplestoreurl)
        else:
            self.labels = SPARQLUtils.getLabelsForClasses(self.sortedatt.keys(),
                                                          None,
                                                          self.triplestoreconf,
                                                          self.triplestoreurl)
        for lab in self.labels:
            if lab in self.sortedatt:
                self.sortedatt[lab]["label"]=self.labels[lab]
        return True

    def finished(self, result):
        while self.searchResult.rowCount()>0:
            self.searchResult.removeRow(0)
        self.searchResult.setHorizontalHeaderLabels(["Selection","Attribute", "Sample Instances"])
        if self.sortedatt != None:
            if len(self.sortedatt)==0:
                self.searchResult.insertRow(0)
                item = QTableWidgetItem()
                item.setText("No results found")
                self.searchResult.setItem(0,0,item)
            else:
                counter=0
                for att in self.sortedatt:
                    curconcept = self.sortedatt[att]["concept"]
                    self.searchResult.insertRow(counter)
                    itemchecked=QTableWidgetItem()
                    itemchecked.setFlags(Qt.ItemIsUserCheckable |
                              Qt.ItemIsEnabled)
                    itemchecked.setCheckState(Qt.Checked)
                    if curconcept in SPARQLUtils.geoproperties:
                        if SPARQLUtils.geoproperties[curconcept] == "DatatypeProperty":
                            itemchecked.setIcon(SPARQLUtils.geodatatypepropertyicon)
                            itemchecked.setToolTip("Geo Datatype Property")
                            itemchecked.setText("GeoDP")
                        elif SPARQLUtils.geoproperties[curconcept] == "ObjectProperty":
                            itemchecked.setIcon(SPARQLUtils.geoobjectpropertyicon)
                            itemchecked.setToolTip("Geo Object Property")
                            itemchecked.setText("GeoOP")
                    elif SPARQLUtils.namespaces["rdfs"] in curconcept \
                            or SPARQLUtils.namespaces["owl"] in curconcept \
                            or SPARQLUtils.namespaces["dc"] in curconcept:
                        itemchecked.setIcon(SPARQLUtils.annotationpropertyicon)
                        itemchecked.setToolTip("Annotation Property")
                        itemchecked.setText("AP")
                    elif "valtype" in self.sortedatt[att]:
                        itemchecked.setIcon(SPARQLUtils.datatypepropertyicon)
                        itemchecked.setToolTip("DataType Property")
                        itemchecked.setText("DP")
                    else:
                        itemchecked.setIcon(SPARQLUtils.objectpropertyicon)
                        itemchecked.setToolTip("Object Property")
                        itemchecked.setText("OP")
                    self.searchResult.setItem(counter, 0, itemchecked)
                    item = QTableWidgetItem()
                    if "label" in self.sortedatt[att]:
                        item.setText(str(self.sortedatt[att]["label"])+ " (" + str(self.sortedatt[att]["amount"]) + "%)")
                    else:
                        item.setText(SPARQLUtils.labelFromURI(str(self.sortedatt[att]["concept"])) + " (" + str(
                            self.sortedatt[att]["amount"]) + "%)")
                    item.setData(256, str(self.sortedatt[att]["concept"]))
                    item.setToolTip("<html><b>Property URI</b> "+str(self.sortedatt[att]["concept"])+"<br>Double click to view definition in web browser")
                    self.searchResult.setItem(counter, 1, item)
                    itembutton = QTableWidgetItem()
                    if "valtype" in self.sortedatt[att]:
                        itembutton.setText("Click to load samples... ["+str(self.sortedatt[att]["valtype"]).replace("http://www.w3.org/2001/XMLSchema#","xsd:").replace("http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdf:")+"]")
                        itembutton.setData(256, str(self.sortedatt[att]["valtype"]))
                    else:
                        itembutton.setText("Click to load samples... [xsd:anyURI]")
                        itembutton.setData(256, "http://www.w3.org/2001/XMLSchema#anyURI")
                    self.searchResult.setItem(counter, 2, itembutton)
                    counter += 1
        else:
            msgBox = QMessageBox()
            msgBox.setText("The dataschema search query did not yield any results!")
            msgBox.exec()
        self.progress.close()
