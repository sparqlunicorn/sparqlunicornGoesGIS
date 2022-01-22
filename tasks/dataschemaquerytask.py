from collections.abc import Iterable
from ..util.sparqlutils import SPARQLUtils
from qgis.core import Qgis, QgsTask, QgsMessageLog
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QStandardItem
from qgis.PyQt.QtWidgets import QMessageBox

MESSAGE_CATEGORY = 'DataSchemaQueryTask'

class DataSchemaQueryTask(QgsTask):
    """This shows how to subclass QgsTask"""

    def __init__(self, description, triplestoreurl, query, searchTerm,prefixes, searchResultModel,triplestoreconf, progress,dlg,styleprop):
        super().__init__(description, QgsTask.CanCancel)
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.query = query
        self.styleprop=styleprop
        self.dlg=dlg
        self.progress = progress
        self.prefixes= prefixes
        self.invprefixes=SPARQLUtils.invertPrefixes(triplestoreconf["prefixes"])
        self.labels = None
        self.searchResultModel=searchResultModel
        self.triplestoreconf=triplestoreconf
        if self.progress!=None:
            newtext = "\n".join(self.progress.labelText().split("\n")[0:-1])
            self.progress.setLabelText(newtext + "\nCurrent Task: Executing query (1/2)")
        self.progress = progress
        self.urilist = None
        self.sortedatt = None
        self.searchTerm = searchTerm
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
        #self.searchResult.model().clear()
        if len(results["results"]["bindings"]) == 0:
            return False
        if self.progress!=None:
            newtext = "\n".join(self.progress.labelText().split("\n")[0:-1])
            self.progress.setLabelText(newtext + "\nCurrent Task: Processing results (2/2)")
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
        while self.searchResultModel.rowCount()>0:
            self.searchResultModel.removeRow(0)
        if self.sortedatt != None:
            if len(self.sortedatt)==0:
                self.searchResult.insertRow(0)
                item = QStandardItem()
                item.setText("No results found")
                self.searchResultModel.setItem(0,0,item)
            else:
                counter=0
                for att in self.sortedatt:
                    curconcept = self.sortedatt[att]["concept"]
                    self.searchResultModel.insertRow(counter)
                    itemchecked=QStandardItem()
                    itemchecked.setFlags(Qt.ItemIsUserCheckable |
                              Qt.ItemIsEnabled)
                    itemchecked.setCheckState(Qt.Checked)
                    if curconcept in SPARQLUtils.geoproperties:
                        if SPARQLUtils.geoproperties[curconcept] == "DatatypeProperty":
                            itemchecked.setIcon(SPARQLUtils.geodatatypepropertyicon)
                            itemchecked.setToolTip("Geo Datatype Property")
                            itemchecked.setText("GeoDP")
                            self.dlg.setWindowIcon(SPARQLUtils.geoclassicon)
                        elif SPARQLUtils.geoproperties[curconcept] == "ObjectProperty":
                            itemchecked.setIcon(SPARQLUtils.geoobjectpropertyicon)
                            itemchecked.setToolTip("Geo Object Property")
                            itemchecked.setText("GeoOP")
                            self.dlg.setWindowIcon(SPARQLUtils.geoclassicon)
                    elif curconcept in SPARQLUtils.styleproperties:
                        itemchecked.setIcon(SPARQLUtils.objectpropertyicon)
                        itemchecked.setToolTip("Style Object Property")
                        itemchecked.setText("Style OP")
                        self.styleprop.append(curconcept)
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
                    self.searchResultModel.setItem(counter, 0, itemchecked)
                    item = QStandardItem()
                    if "label" in self.sortedatt[att]:
                        item.setText(str(self.sortedatt[att]["label"])+ " ("+SPARQLUtils.labelFromURI(str(self.sortedatt[att]["concept"]),self.invprefixes)+") [" + str(self.sortedatt[att]["amount"]) + "%]")
                    else:
                        item.setText(SPARQLUtils.labelFromURI(str(self.sortedatt[att]["concept"]),self.invprefixes) + " (" + str(
                            self.sortedatt[att]["amount"]) + "%)")
                    item.setData(str(self.sortedatt[att]["concept"]),256)
                    item.setToolTip("<html><b>Property URI</b> "+str(self.sortedatt[att]["concept"])+"<br>Double click to view definition in web browser")
                    self.searchResultModel.setItem(counter, 1, item)
                    itembutton = QStandardItem()
                    if "valtype" in self.sortedatt[att]:
                        itembutton.setText("Click to load samples... ["+str(self.sortedatt[att]["valtype"]).replace("http://www.w3.org/2001/XMLSchema#","xsd:").replace("http://www.w3.org/1999/02/22-rdf-syntax-ns#","rdf:").replace("http://www.opengis.net/ont/geosparql#","geo:")+"]")
                        itembutton.setData(str(self.sortedatt[att]["valtype"]),256)
                    else:
                        itembutton.setText("Click to load samples... [xsd:anyURI]")
                        itembutton.setData("http://www.w3.org/2001/XMLSchema#anyURI",256)
                    self.searchResultModel.setItem(counter, 2, itembutton)
                    counter += 1
        else:
            msgBox = QMessageBox()
            msgBox.setText("The dataschema search query did not yield any results!")
            msgBox.exec()
        self.searchResultModel.setHeaderData(0, Qt.Horizontal, "Selection")
        self.searchResultModel.setHeaderData(1, Qt.Horizontal, "Attribute")
        self.searchResultModel.setHeaderData(2, Qt.Horizontal, "Sample Instances")
        self.progress.close()
