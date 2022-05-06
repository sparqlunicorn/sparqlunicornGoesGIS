from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QStyle
from qgis.core import QgsProject, Qgis
import xml.etree.ElementTree as ET
from qgis.utils import iface
from qgis.PyQt import QtCore
from qgis.PyQt.QtWidgets import QTableWidgetItem, QMessageBox, QFileDialog, QComboBox
from qgis.PyQt.QtGui import QRegExpValidator

from ..util.ui.uiutils import UIUtils
from ..util.layerutils import LayerUtils

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
        self.searchClass.setIcon(UIUtils.searchclassicon)
        self.interlinkNameSpace=dlg.interlinkNameSpace
        self.interlinkNameSpace.setValidator(QRegExpValidator(UIUtils.urlregex, self.dlg))
        self.dlg.refreshLayersInterlink.setIcon(QIcon(self.dlg.style().standardIcon(getattr(QStyle, 'SP_BrowserReload'))))
        self.dlg.refreshLayersInterlink.clicked.connect(lambda: LayerUtils.loadLayerList([self.dlg.chooseLayerInterlink,self.dlg.chooseLayerEnrich]))
        self.interlinkNameSpace.textChanged.connect(lambda: UIUtils.check_state(self.interlinkNameSpace))
        self.interlinkNameSpace.textChanged.emit(self.interlinkNameSpace.text())
        self.loadLayerInterlink=dlg.loadLayerInterlink
        self.loadLayerInterlink.clicked.connect(self.loadLayerForInterlink)
        self.dlg.exportMappingButton.clicked.connect(self.exportMapping)
        self.dlg.importMappingButton.clicked.connect(self.loadMapping)

    ## Loads an enrichment mapping from a previously defined mapping file.
    #  @param self The object pointer.
    def loadMapping(self):
        dialog = QFileDialog(self.dlg)
        dialog.setFileMode(QFileDialog.AnyFile)
        if dialog.exec_():
            fileNames = dialog.selectedFiles()
            filepath = fileNames[0].split(".")
            self.readMapping(fileNames[0])

    ##
    #  @brief Loads a QGIS layer for interlinking into the interlinking dialog.
    #
    #  @param self The object pointer
    def loadLayerForInterlink(self):
        layers = QgsProject.instance().layerTreeRoot().children()
        selectedLayerIndex = self.chooseLayerInterlink.currentIndex()
        if len(layers) == 0:
            return
        layer = layers[selectedLayerIndex].layer()
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
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                item2 = QTableWidgetItem()
                item2.setCheckState(True)
                item3 = QTableWidgetItem()
                item3.setCheckState(False)
                item4 = QTableWidgetItem()
                item4.setCheckState(False)
                self.interlinkTable.insertRow(row)
                self.interlinkTable.setItem(row, 3, item)
                self.interlinkTable.setItem(row, 0, item2)
                self.interlinkTable.setItem(row, 1, item3)
                self.interlinkTable.setItem(row, 2, item4)
                cbox = QComboBox()
                cbox.addItem("Automatic")
                cbox.addItem("AnnotationProperty")
                cbox.addItem("DataProperty")
                cbox.addItem("ObjectProperty")
                cbox.addItem("SubClass")
                self.interlinkTable.setCellWidget(row, 5, cbox)
                currentRowCount = self.interlinkTable.rowCount()
                row += 1
        except:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Layer not compatible for interlinking!")
            msgBox.setText("The chosen layer is not supported for interlinking. You possibly selected a raster layer")
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
                        if propiri != None:
                            item = QTableWidgetItem(propiri)
                            item.setText(propiri)
                            item.setData(1, propiri)
                            self.dlg.interlinkTable.setItem(row, 4, item)
                        if proptype != None:
                            comboboxx = self.dlg.interlinkTable.cellWidget(row, 5)
                            if proptype == "annotation":
                                comboboxx.setCurrentIndex(
                                    comboboxx.findText("AnnotationProperty", QtCore.Qt.MatchFixedString))
                            elif proptype == "obj":
                                comboboxx.setCurrentIndex(
                                    comboboxx.findText("ObjectProperty", QtCore.Qt.MatchFixedString))
                            elif proptype == "data":
                                comboboxx.setCurrentIndex(
                                    comboboxx.findText("DataProperty", QtCore.Qt.MatchFixedString))
                            elif proptype == "subclass":
                                comboboxx.setCurrentIndex(comboboxx.findText("SubClass", QtCore.Qt.MatchFixedString))
                            else:
                                comboboxx.setCurrentIndex(comboboxx.findText("Automatic", QtCore.Qt.MatchFixedString))
                        if concept != None:
                            item = QTableWidgetItem(concept)
                            item.setText(concept)
                            item.setData(1, concept)
                            self.dlg.interlinkTable.setItem(row, 6, item)
                        if valuemappings != {} and valuemappings != None:
                            item = QTableWidgetItem("ValueMap{}")
                            item.setText("ValueMap{}")
                            item.setData(1, valuemappings)
                            if query != None:
                                item.setData(2, query)
                                item.setData(3, triplestoreurl)
                            self.dlg.interlinkTable.setItem(row, 7, item)
                        elif query != None:
                            item = QTableWidgetItem("ValueMap{}")
                            item.setText("ValueMap{}")
                            item.setData(2, query)
                            item.setData(3, triplestoreurl)
                            if valuemappings != {} and valuemappings != None:
                                item.setData(1, valuemappings)
                            self.dlg.interlinkTable.setItem(row, 7, item)
        else:
            msgBox = QMessageBox()
            msgBox.setText("Please first load a dataset to enrich before loading a mapping file")
            msgBox.exec()

    ## Shows the export concept mapping dialog.
    #  @param self The object pointer. 
    def exportMapping(self):
        filename, _filter = QFileDialog.getSaveFileName(
            self.dlg, "Select   output file ", "", "XML (.xml)", )
        if filename == "":
            return
        layers = QgsProject.instance().layerTreeRoot().children()
        ttlstring = self.exportMappingProcess()
        splitted = filename.split(".")
        exportNameSpace = ""
        exportSetClass = ""
        with open(filename, 'w') as output_file:
            output_file.write(ttlstring)
            iface.messageBar().pushMessage("export mapping successfully!", "OK", level=Qgis.Success)

    ## Converts a concept mapping to XML.
    #  @param self The object pointer. 
    def exportMappingProcess(self):
        xmlmappingheader = "<?xml version=\"1.0\" ?>\n<data>\n<file "
        xmlmapping = ""
        self.exportIdCol = ""
        self.exportNameSpace = self.dlg.interlinkNameSpace.text()
        self.exportSetClass = self.dlg.interlinkOwlClassInput.text()
        xmlmappingheader += "class=\"" + self.dlg.interlinkOwlClassInput.text() + "\" "
        xmlmappingheader += "namespace=\"" + self.dlg.interlinkNameSpace.text() + "\" "
        propurilist = []
        classurilist = []
        includelist = []
        for row in range(self.dlg.interlinkTable.rowCount()):
            item = self.dlg.interlinkTable.item(row, 0)
            if item.checkState():
                includelist.append(True)
                if self.dlg.interlinkTable.item(row, 1).checkState():
                    self.exportIdCol = self.dlg.interlinkTable.item(row, 3).text()
                    xmlmappingheader += " indid=\"" + self.exportIdCol + "\" "
                    propurilist.append("")
                    classurilist.append("")
                else:
                    xmlmapping += "<column name=\"" + self.dlg.interlinkTable.item(row, 3).text() + "\" "
                    column = self.dlg.interlinkTable.item(row, 3).text()
                    if self.dlg.interlinkTable.item(row, 4) != None:
                        column = self.dlg.interlinkTable.item(row, 4).data(0)
                        propurilist.append(self.dlg.interlinkTable.item(row, 4).data(1))
                        xmlmapping += "propiri=\"" + self.dlg.interlinkTable.item(row, 4).data(1) + "\" "
                    else:
                        propurilist.append("")
                    if self.dlg.interlinkTable.cellWidget(row, 5) != None and self.dlg.interlinkTable.cellWidget(row,
                                                                                                                 5).currentText() != "Automatic":
                        if self.dlg.interlinkTable.cellWidget(row, 5).currentText() == "AnnotationProperty":
                            xmlmapping += "prop=\"annotation\" "
                        elif self.dlg.interlinkTable.cellWidget(row, 5).currentText() == "DataProperty":
                            xmlmapping += "prop=\"data\" "
                        elif self.dlg.interlinkTable.cellWidget(row, 5).currentText() == "ObjectProperty":
                            xmlmapping += "prop=\"obj\" "
                        elif self.dlg.interlinkTable.cellWidget(row, 5).currentText() == "SubClass":
                            xmlmapping += "prop=\"subclass\" "
                    if self.dlg.interlinkTable.item(row, 6) != None:
                        concept = self.dlg.interlinkTable.item(row, 6).data(0)
                        self.exportColConfig[column] = concept
                        classurilist.append(concept)
                        xmlmapping += "concept=\"" + self.dlg.interlinkTable.item(row, 6).data(1) + "\" "
                    else:
                        classurilist.append("")
                    if self.dlg.interlinkTable.item(row, 7) != None:
                        self.valueconcept = self.dlg.interlinkTable.item(row, 7).data(1)
                        if self.dlg.interlinkTable.item(row, 7).data(2) != None and self.dlg.interlinkTable.item(row,
                                                                                                                 7).data(
                                3) != None:
                            xmlmapping += "query=\"" + self.dlg.interlinkTable.item(row, 7).data(2).replace("\n",
                                                                                                            " ") + "\" triplestoreurl=\"" + self.dlg.interlinkTable.item(
                                row, 7).data(3) + "\" "
                        xmlmapping += ">\n"
                        if self.valueconcept != None:
                            for key in self.valueconcept:
                                xmlmapping += "<valuemapping from=\"" + key + "\" to=\"" + self.valueconcept[
                                    key] + "\"/>\n"
                    else:
                        xmlmapping += ">\n"
                    xmlmapping += "</column>\n"
            else:
                includelist.append(False)
                propurilist.append("")
                classurilist.append("")
        xmlmapping += "</file>\n</data>"
        return xmlmappingheader + ">\n" + xmlmapping
