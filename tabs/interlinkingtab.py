from qgis.core import QgsProject, Qgis,QgsMapLayerProxyModel
import xml.etree.ElementTree as ET
from qgis.utils import iface
from qgis.PyQt import QtCore
from qgis.PyQt.QtWidgets import QTableWidgetItem, QMessageBox, QFileDialog, QComboBox
from qgis.PyQt.QtGui import QRegularExpressionValidator
from qgis.PyQt.QtWidgets import QProgressDialog, QFileDialog
from qgis.core import QgsApplication
from qgis.core import Qgis,QgsTask, QgsMessageLog
from qgis.PyQt.QtCore import Qt
import json

from ..util.interlinkutils import InterlinkUtils
from ..util.ui.uiutils import UIUtils
from ..util.export.exporterutils import ExporterUtils
from ..tasks.processing.convertlayertask import ConvertLayerTask

## Provides implementations for functions accessible from the interlinking tab
class InterlinkingTab:
    enrichLayer = None

    dlg = None

    def __init__(self, dlg):
        self.dlg = dlg
        self.chooseLayerInterlink=dlg.chooseLayerInterlink
        self.chooseLayerInterlink.clear()
        self.addVocabConf=None
        self.interlinkTable=dlg.interlinkTable
        self.interlinkTable.cellClicked.connect(self.createInterlinkSearchDialog)
        self.searchClass=dlg.searchClass
        self.searchClass.clicked.connect(self.createInterlinkSearchDialog)
        self.interlinkNameSpace=dlg.interlinkNameSpace
        self.interlinkNameSpace.setValidator(QRegularExpressionValidator(UIUtils.urlregex, self.dlg))
        self.interlinkNameSpace.textChanged.connect(lambda: UIUtils.check_state(self.interlinkNameSpace))
        self.interlinkNameSpace.textChanged.emit(self.interlinkNameSpace.text())
        self.exportInterlink = dlg.exportInterlink
        self.exportInterlink.clicked.connect(self.exportInterlinkedLayer)
        self.loadLayerInterlink=dlg.loadLayerInterlink
        self.loadLayerInterlink.clicked.connect(self.loadLayerForInterlink)
        self.chooseLayerInterlink.setFilters(QgsMapLayerProxyModel.PointLayer|QgsMapLayerProxyModel.LineLayer|QgsMapLayerProxyModel.PolygonLayer|QgsMapLayerProxyModel.NoGeometry)
        self.dlg.exportMappingButton.clicked.connect(self.exportMapping)
        self.dlg.importMappingButton.clicked.connect(self.loadMapping)
        self.dlg.suggestMapping.clicked.connect(self.suggestSchema)

    ## Loads an enrichment mapping from a previously defined mapping file.
    #  @param self The object pointer.
    def loadMapping(self):
        dialog = QFileDialog(self.dlg)
        dialog.setFileMode(QFileDialog.AnyFile)
        if dialog.exec_():
            fileNames = dialog.selectedFiles()
            filepath = fileNames[0].split(".")
            self.readMapping(fileNames[0])

    def exportInterlinkedLayer(self):
        layer = self.chooseLayerInterlink.currentLayer()
        columntypes=json.loads(self.exportMapping(True))
        filename = QFileDialog.getSaveFileName(
            self.dlg, "Select output file ", "", ExporterUtils.getExporterString())
        QgsMessageLog.logMessage('Started task "{}"'.format(
            filename),
            "Convert Layer Dialog", Qgis.Info)
        if filename[0] == "":
            return
        progress = QProgressDialog("Loading Layer and converting it to : " + str(filename), "Abort", 0, 0, self.dlg)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setWindowTitle("Converting layer")
        progress.setCancelButton(None)
        self.qtask = ConvertLayerTask("Converting Layer to graph: " + str(filename),
                                      layer, filename, "GeoSPARQL",
                                      "WKT",self.dlg.prefixes,columntypes,
                                      self.dlg,
                                      progress)
        QgsApplication.taskManager().addTask(self.qtask)

    def suggestSchema(self):
        if self.interlinkTable.rowCount() == 0:
            self.loadLayerInterlink()
        layer = self.chooseLayerInterlink.currentLayer()
        columntypes=InterlinkUtils.suggestMappingSchema(layer)
        columnuris=InterlinkUtils.suggestColumnURIs(layer,self.dlg.prefixes)
        counter=0
        for col in columntypes:
            if "id" in col and col["id"] and "id" in col["name"] and not col["geotype"]:
                self.dlg.interlinkTable.item(counter,1).setCheckState(col["id"])
            item = QTableWidgetItem(columnuris[counter])
            item.setText(columnuris[counter])
            item.setData(1, columnuris[counter])
            self.dlg.interlinkTable.setItem(counter, 4,item)
            if col["geotype"]:
                self.dlg.interlinkTable.item(counter, 2).setCheckState(col["geotype"])
                self.dlg.interlinkTable.cellWidget(counter, 5).setCurrentIndex(5)
            self.dlg.interlinkTable.setItem(counter, 6,QTableWidgetItem(col["xsdtype"]))
            if "xsd:" in col["xsdtype"]:
                self.dlg.interlinkTable.cellWidget(counter,5).setCurrentIndex(2)
            elif "owl:Class" in col["xsdtype"]:
                self.dlg.interlinkTable.cellWidget(counter, 5).setCurrentIndex(4)
                item = QTableWidgetItem("rdfs:subClassOf")
                item.setText("rdfs:subClassOf")
                item.setData(1, "http://www.w3.org/2000/01/rdf-schema#subClassOf")
                self.dlg.interlinkTable.setItem(counter, 4,item)
            elif "ct:LabelProperty" in col["xsdtype"]:
                self.dlg.interlinkTable.cellWidget(counter, 5).setCurrentIndex(6)
                item = QTableWidgetItem("rdfs:label")
                item.setText("rdfs:label")
                item.setData(1, "http://www.w3.org/2000/01/rdf-schema#label")
                self.dlg.interlinkTable.setItem(counter, 4, item)
            elif "ct:CommentProperty" in col["xsdtype"]:
                self.dlg.interlinkTable.cellWidget(counter, 5).setCurrentIndex(7)
                item = QTableWidgetItem("rdfs:comment")
                item.setText("rdfs:comment")
                item.setData(1, "http://www.w3.org/2000/01/rdf-schema#comment")
                self.dlg.interlinkTable.setItem(counter, 4, item)
            counter+=1



    ##
    #  @brief Loads a QGIS layer for interlinking into the interlinking dialog.
    #
    #  @param self The object pointer
    def loadLayerForInterlink(self):
        if len(self.chooseLayerInterlink) == 0:
            return
        layer=self.chooseLayerInterlink.currentLayer()
        if layer is None:
            return
        self.interlinkNameSpace.setText("http://www.github.com/sparqlunicorn/data/"+str(layer.name()).lower().replace(" ","_")+"/")
        try:
            fieldnames = [field.name() for field in layer.fields()]
            while self.interlinkTable.rowCount() > 0:
                self.interlinkTable.removeRow(0)
            row = 0
            self.interlinkTable.setHorizontalHeaderLabels(
                ["Export?", "IDColumn?", "GeoColumn?", "Column", "ColumnProperty", "PropertyType", "ColumnConcept",
                 "ValueConcepts"])
            self.interlinkTable.setColumnCount(8)
            #columntypes=LayerUtils.detectLayerColumnTypes(layer)
            for field in fieldnames:
                item = QTableWidgetItem(field)
                item.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled)
                item2 = QTableWidgetItem()
                item2.setCheckState(QtCore.Qt.CheckState.Checked)
                item3 = QTableWidgetItem()
                item3.setCheckState(QtCore.Qt.CheckState.Unchecked)
                item4 = QTableWidgetItem()
                item4.setCheckState(QtCore.Qt.CheckState.Unchecked)
                self.interlinkTable.insertRow(row)
                self.interlinkTable.setItem(row, 3, item)
                self.interlinkTable.setItem(row, 0, item2)
                self.interlinkTable.setItem(row, 1, item3)
                self.interlinkTable.setItem(row, 2, item4)
                cbox = QComboBox()
                cbox.addItem(UIUtils.linkeddataicon,"Automatic")
                cbox.addItem(UIUtils.annotationpropertyicon,"AnnotationProperty")
                cbox.addItem(UIUtils.datatypepropertyicon,"DataProperty")
                cbox.addItem(UIUtils.objectpropertyicon,"ObjectProperty")
                cbox.addItem(UIUtils.subclassicon,"SubClass")
                cbox.addItem(UIUtils.georelationpropertyicon,"GeoProperty")
                cbox.addItem(UIUtils.labelannotationpropertyicon,"LabelProperty")
                cbox.addItem(UIUtils.commentannotationpropertyicon,"DescriptionProperty")
                cbox.addItem(UIUtils.classicon,"TypeProperty")
                self.interlinkTable.setCellWidget(row, 5, cbox)
                currentRowCount = self.interlinkTable.rowCount()
                row += 1
        except Exception as e:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Layer not compatible for interlinking!")
            msgBox.setText("The chosen layer is not supported for interlinking. You possibly selected a raster layer\n\n"+str(e))
            msgBox.exec()
            return

    def createInterlinkSearchDialog(self, row=-1, column=-1):
        if column > 3 and column < 7:
            self.dlg.buildSearchDialog(row, column, True, self.interlinkTable, True, False, None, self.addVocabConf)
        elif column >= 7:
            layers = QgsProject.instance().layerTreeRoot().children()
            selectedLayerIndex = self.chooseLayerInterlink.currentIndex()
            layer = layers[selectedLayerIndex].layer()
            self.dlg.buildValueMappingDialog(row, column, True, self.interlinkTable, layer)
        elif column == -1:
            self.dlg.buildSearchDialog(row, column, -1, self.dlg.interlinkOwlClassInput, False, False, None, self.addVocabConf)

    ## Reads a concept mapping from a given XML file.
    #  @param self The object pointer.
    #  @param self The file path    
    def readMapping(self, filename):
        if self.dlg.interlinkTable.rowCount() != 0:
            if "json" in filename:
                f = open(filename)
                filedata=json.load(f)
                if "namespace" in filedata:
                    self.dlg.interlinkNameSpace.setText(filedata.get("namespace"))
                if "class" in filedata:
                    self.dlg.interlinkOwlClassInput.setText(filedata.get("class"))
                if "columns" in filedata:
                    for row in range(self.dlg.interlinkTable.rowCount()):
                        columnname = self.dlg.interlinkTable.item(row, 3).text()
                        if columnname not in filedata["columns"]:
                            if "indid" in filedata and filedata["indid"]==columnname:
                                self.dlg.interlinkTable.item(row, 1).setCheckState(True)
                                item = QTableWidgetItem("rdf:type")
                                item.setText("rdf:type")
                                item.setData(1, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
                                self.dlg.interlinkTable.setItem(row, 4, item)
                                comboboxx = self.dlg.interlinkTable.cellWidget(row, 5)
                                comboboxx.setCurrentIndex(
                                    comboboxx.findText("TypeProperty", QtCore.Qt.MatchFlag.MatchFixedString))
                                item = QTableWidgetItem("owl:Class")
                                item.setText("owl:Class")
                                item.setData(1, "http://www.w3.org/2002/07/owl#Class")
                                self.dlg.interlinkTable.setItem(row, 6, item)
                            continue
                        column=filedata["columns"][columnname]
                        if "name" in column and column["name"] == columnname:
                            if "propiri" in column:
                                self.dlg.interlinkTable.setItem(row, 4, QTableWidgetItem(column["propiri"]))
                            if "prop" in column and column["prop"] is not None:
                                comboboxx = self.dlg.interlinkTable.cellWidget(row, 5)
                                proptype=column["prop"]
                                if proptype == "annotation":
                                    comboboxx.setCurrentIndex(
                                        comboboxx.findText("AnnotationProperty", QtCore.Qt.MatchFlag.MatchFixedString))
                                elif proptype == "obj":
                                    comboboxx.setCurrentIndex(
                                        comboboxx.findText("ObjectProperty", QtCore.Qt.MatchFlag.MatchFixedString))
                                elif proptype == "data":
                                    comboboxx.setCurrentIndex(
                                        comboboxx.findText("DataProperty", QtCore.Qt.MatchFlag.MatchFixedString))
                                elif proptype == "label":
                                    comboboxx.setCurrentIndex(
                                        comboboxx.findText("LabelProperty", QtCore.Qt.MatchFlag.MatchFixedString))
                                elif proptype == "geo":
                                    comboboxx.setCurrentIndex(
                                        comboboxx.findText("GeoProperty", QtCore.Qt.MatchFlag.MatchFixedString))
                                elif proptype == "type":
                                    comboboxx.setCurrentIndex(
                                        comboboxx.findText("TypeProperty", QtCore.Qt.MatchFlag.MatchFixedString))
                                elif proptype == "desc":
                                    comboboxx.setCurrentIndex(
                                        comboboxx.findText("DescriptionProperty", QtCore.Qt.MatchFlag.MatchFixedString))
                                elif proptype == "subclass":
                                    comboboxx.setCurrentIndex(
                                        comboboxx.findText("SubClass", QtCore.Qt.MatchFlag.MatchFixedString))
                                else:
                                    comboboxx.setCurrentIndex(
                                        comboboxx.findText("Automatic", QtCore.Qt.MatchFlag.MatchFixedString))
                            if "concept" in column and column["concept"] is not None:
                                item = QTableWidgetItem(column["concept"])
                                item.setText(column["concept"])
                                item.setData(1, column["concept"])
                                self.dlg.interlinkTable.setItem(row, 6, item)
                f.close()
            elif "xml" in filename:
                tree = ET.parse(filename)
                root = tree.getroot()
                filedata = root.find('file')[0]
                self.dlg.interlinkNameSpace.setText(filedata.get("namespace"))
                self.dlg.interlinkOwlClassInput.setText(filedata.get("class"))
                for neighbor in root.iter('column'):
                    name = neighbor.get("name")
                    proptype = neighbor.get("prop")
                    propiri = neighbor.get("propiri")
                    concept = neighbor.get("concept")
                    query = neighbor.get("query")
                    triplestoreurl = neighbor.get("triplestoreurl")
                    valuemappings = {}
                    for vmap in neighbor.findall("valuemapping"):
                        valuemappings[vmap.get("from")] = vmap.get("to")
                    for row in range(self.dlg.interlinkTable.rowCount()):
                        columnname = self.dlg.interlinkTable.item(row, 3).text()
                        if columnname == name:
                            if propiri is not None:
                                item = QTableWidgetItem(propiri)
                                item.setText(propiri)
                                item.setData(1, propiri)
                                self.dlg.interlinkTable.setItem(row, 4, item)
                            if proptype is not None:
                                comboboxx = self.dlg.interlinkTable.cellWidget(row, 5)
                                if proptype == "annotation":
                                    comboboxx.setCurrentIndex(
                                        comboboxx.findText("AnnotationProperty", QtCore.Qt.MatchFlag.MatchFixedString))
                                elif proptype == "obj":
                                    comboboxx.setCurrentIndex(
                                        comboboxx.findText("ObjectProperty", QtCore.Qt.MatchFlag.MatchFixedString))
                                elif proptype == "data":
                                    comboboxx.setCurrentIndex(
                                        comboboxx.findText("DataProperty", QtCore.Qt.MatchFlag.MatchFixedString))
                                elif proptype == "label":
                                    comboboxx.setCurrentIndex(
                                        comboboxx.findText("LabelProperty", QtCore.Qt.MatchFlag.MatchFixedString))
                                elif proptype == "geo":
                                    comboboxx.setCurrentIndex(
                                        comboboxx.findText("GeoProperty", QtCore.Qt.MatchFlag.MatchFixedString))
                                elif proptype == "type":
                                    comboboxx.setCurrentIndex(
                                        comboboxx.findText("TypeProperty", QtCore.Qt.MatchFlag.MatchFixedString))
                                elif proptype == "desc":
                                    comboboxx.setCurrentIndex(
                                        comboboxx.findText("DescriptionProperty", QtCore.Qt.MatchFlag.MatchFixedString))
                                elif proptype == "subclass":
                                    comboboxx.setCurrentIndex(comboboxx.findText("SubClass", QtCore.Qt.MatchFlag.MatchFixedString))
                                else:
                                    comboboxx.setCurrentIndex(comboboxx.findText("Automatic", QtCore.Qt.MatchFlag.MatchFixedString))
                            if concept is not None:
                                item = QTableWidgetItem(concept)
                                item.setText(concept)
                                item.setData(1, concept)
                                self.dlg.interlinkTable.setItem(row, 6, item)
                            if valuemappings != {} and valuemappings is not None:
                                item = QTableWidgetItem("ValueMap{}")
                                item.setText("ValueMap{}")
                                item.setData(1, valuemappings)
                                if query is not None:
                                    item.setData(2, query)
                                    item.setData(3, triplestoreurl)
                                self.dlg.interlinkTable.setItem(row, 7, item)
                            elif query is not None:
                                item = QTableWidgetItem("ValueMap{}")
                                item.setText("ValueMap{}")
                                item.setData(2, query)
                                item.setData(3, triplestoreurl)
                                if valuemappings != {} and valuemappings is not None:
                                    item.setData(1, valuemappings)
                                self.dlg.interlinkTable.setItem(row, 7, item)
        else:
            msgBox = QMessageBox()
            msgBox.setText("Please first load a dataset to enrich before loading a mapping file")
            msgBox.exec()

    ## Shows the export concept mapping dialog.
    #  @param self The object pointer. 
    def exportMapping(self,asString=False):
        if not asString:
            filename, _filter = QFileDialog.getSaveFileName(
                self.dlg, "Select   output file ", "", "JSON (.json), XML (.xml)", )
            if filename == "":
                return
            exportstring = self.exportMappingProcess("json" in filename)
            with open(filename, 'w') as output_file:
                output_file.write(exportstring)
                iface.messageBar().pushMessage("export mapping successfully!", "OK", level=Qgis.Success)
        else:
            exportstring = self.exportMappingProcess(True)
        return exportstring

    ## Converts a concept mapping to XML.
    #  @param self The object pointer. 
    def exportMappingProcess(self,jsonOrXML):
        result={"namespace":self.dlg.interlinkNameSpace.text(),"class": self.dlg.interlinkOwlClassInput.text(),"columns":{}}
        for row in range(self.dlg.interlinkTable.rowCount()):
            item = self.dlg.interlinkTable.item(row, 0)
            if item.checkState():
                column = {}
                if self.dlg.interlinkTable.item(row, 1).checkState():
                    result["indid"]=self.dlg.interlinkTable.item(row, 3).text()
                else:
                    column={"name":self.dlg.interlinkTable.item(row, 3).text(),"order":row}
                    if self.dlg.interlinkTable.item(row, 4) is not None and self.dlg.interlinkTable.item(row, 4).data(1) is not None:
                        column["propiri"]=self.dlg.interlinkTable.item(row, 4).data(1)
                    if self.dlg.interlinkTable.cellWidget(row, 5) is not None and self.dlg.interlinkTable.cellWidget(row,
                                                                                                                     5).currentText() != "Automatic":
                        if self.dlg.interlinkTable.cellWidget(row, 5).currentText() == "AnnotationProperty":
                            column["prop"]="annotation"
                        elif self.dlg.interlinkTable.cellWidget(row, 5).currentText() == "DataProperty":
                            column["prop"]="data"
                        elif self.dlg.interlinkTable.cellWidget(row, 5).currentText() == "ObjectProperty":
                            column["prop"]="obj"
                        elif self.dlg.interlinkTable.cellWidget(row, 5).currentText() == "SubClass":
                            column["prop"]="subclass"
                        elif self.dlg.interlinkTable.cellWidget(row, 5).currentText() == "GeoProperty":
                            column["prop"]="geo"
                        elif self.dlg.interlinkTable.cellWidget(row, 5).currentText() == "LabelProperty":
                            column["prop"] = "label"
                        elif self.dlg.interlinkTable.cellWidget(row, 5).currentText() == "DescriptionProperty":
                            column["prop"] = "desc"
                        elif self.dlg.interlinkTable.cellWidget(row, 5).currentText() == "TypeProperty":
                            column["prop"] = "type"
                    if self.dlg.interlinkTable.item(row, 6) is not None:
                        concept = self.dlg.interlinkTable.item(row, 6).data(0)
                        #self.exportColConfig[column] = concept
                        column["concept"]=concept
                    if self.dlg.interlinkTable.item(row, 7) is not None:
                        self.valueconcept = self.dlg.interlinkTable.item(row, 7).data(1)
                        if self.dlg.interlinkTable.item(row, 7).data(2) is not None and self.dlg.interlinkTable.item(row,
                                                                                                                     7).data(
                                3) is not None:
                            column["query"]=self.dlg.interlinkTable.item(row, 7).data(2).replace("\n", " ")
                            column["triplestoreurl"]=self.dlg.interlinkTable.item(row, 7).data(3)
                        if self.valueconcept is not None:
                            column["valuemapping"]={}
                            for key in self.valueconcept:
                                column["valuemapping"][key]=self.valueconcept[key]
                    result["columns"][column["name"]]=column
        if jsonOrXML:
            return json.dumps(result,indent=2)
        return InterlinkUtils.exportMappingXML(result)
