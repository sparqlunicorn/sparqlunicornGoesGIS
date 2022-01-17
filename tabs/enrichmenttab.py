from qgis.core import QgsProject, Qgis
from qgis.utils import iface
from qgis.PyQt import QtCore

from ..util.sparqlutils import SPARQLUtils
from ..util.layerutils import LayerUtils
from ..tasks.enrichmentquerytask import EnrichmentQueryTask
from qgis.PyQt.QtWidgets import QMessageBox, QProgressDialog, QTableWidgetItem
from qgis.PyQt.QtWidgets import QComboBox, QTableWidgetItem, QHBoxLayout, QPushButton, QWidget, \
    QAbstractItemView, QMessageBox, QApplication, QMenu, QAction, QFileDialog, QStyle
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsApplication
from ..dialogs.whattoenrichdialog import EnrichmentDialog


class EnrichmentTab:
    enrichLayer = None

    enrichedExport = False

    dlg = None

    qtask = None

    originalRowCount = 0

    enrichLayerCounter = 0

    def __init__(self, dlg):
        self.dlg = dlg
        self.chooseLayerEnrich = dlg.chooseLayerEnrich
        self.enrichTableResult = dlg.enrichTableResult
        self.enrichTable = dlg.enrichTable
        self.addEnrichedLayerRowButton = dlg.addEnrichedLayerRowButton
        self.addEnrichedLayerRowButton.clicked.connect(self.addEnrichRow)
        self.addEnrichedLayerButton = dlg.addEnrichedLayerButton
        self.addEnrichedLayerButton.clicked.connect(self.addEnrichedLayer)
        self.startEnrichment = dlg.startEnrichment
        self.startEnrichment.clicked.connect(self.enrichLayerProcess)
        self.exportInterlink = dlg.exportInterlink
        self.exportInterlink.clicked.connect(self.exportEnrichedLayer)
        self.loadLayerEnrich = dlg.loadLayerEnrich
        self.loadLayerEnrich.clicked.connect(self.loadLayerForEnrichment)
        self.whattoenrich = dlg.whattoenrich
        self.whattoenrich.clicked.connect(self.createWhatToEnrich)
        self.dlg.refreshLayersEnrich.clicked.connect(lambda: LayerUtils.loadLayerList([self.dlg.chooseLayerInterlink,self.dlg.chooseLayerEnrich]))

    ##
    #  @brief Creates a What To Enrich dialog with parameters given.
    #
    #  @param self The object pointer
    def createWhatToEnrich(self):
        if self.enrichTable.rowCount() == 0:
            return
        layers = QgsProject.instance().layerTreeRoot().children()
        selectedLayerIndex = self.chooseLayerEnrich.currentIndex()
        layer = layers[selectedLayerIndex].layer()
        self.searchTripleStoreDialog = EnrichmentDialog(self.dlg.triplestoreconf, self.dlg.prefixes, self.enrichTable,
                                                        layer,
                                                        None, None)
        self.searchTripleStoreDialog.setMinimumSize(700, 500)
        self.searchTripleStoreDialog.setWindowTitle("Enrichment Search")
        self.searchTripleStoreDialog.exec_()

    def createEnrichSearchDialog(self, row=-1, column=-1):
        if column == 1:
            self.dlg.buildSearchDialog(row, column, False, self.enrichTable, False, False, None, self.dlg.addVocabConf)
        if column == 6:
            self.dlg.buildSearchDialog(row, column, False, self.enrichTable, False, False, None, self.dlg.addVocabConf)

    def createEnrichSearchDialogProp(self, row=-1, column=-1):
        self.dlg.buildSearchDialog(row, column, False, self.dlg.findIDPropertyEdit, True, False, None,
                                   self.dlg.addVocabConf)

    ##
    #  @brief Adds a new row to the table in the enrichment dialog.
    #
    #  @param  self The object pointer
    #
    def addEnrichRow(self):
        layers = QgsProject.instance().layerTreeRoot().children()
        selectedLayerIndex = self.chooseLayerEnrich.currentIndex()
        layer = layers[selectedLayerIndex].layer()
        self.enrichTableResult.hide()
        fieldnames = [field.name() for field in layer.fields()]
        item = QTableWidgetItem("new_column")
        # item.setFlags(QtCore.Qt.ItemIsEnabled)
        row = self.enrichTable.rowCount()
        self.enrichTable.insertRow(row)
        self.enrichTable.setItem(row, 0, item)
        cbox = QComboBox()
        cbox.addItem("Get Remote")
        cbox.addItem("No Enrichment")
        cbox.addItem("Exclude")
        self.enrichTable.setCellWidget(row, 3, cbox)
        cbox = QComboBox()
        cbox.addItem("Enrich Value")
        cbox.addItem("Enrich URI")
        cbox.addItem("Enrich Both")
        self.enrichTable.setCellWidget(row, 4, cbox)
        cbox = QComboBox()
        for fieldd in fieldnames:
            cbox.addItem(fieldd)
        self.enrichTable.setCellWidget(row, 5, cbox)
        itemm = QTableWidgetItem("http://www.w3.org/2000/01/rdf-schema#label")
        self.enrichTable.setItem(row, 6, itemm)
        itemm = QTableWidgetItem("")
        self.enrichTable.setItem(row, 7, itemm)
        itemm = QTableWidgetItem("")
        self.enrichTable.setItem(row, 8, itemm)

    ##
    #  @brief Loads a QGIS layer for enrichment into the enrichment dialog.
    #
    #  @param self The object pointer
    def loadLayerForEnrichment(self):
        layers = QgsProject.instance().layerTreeRoot().children()
        selectedLayerIndex = self.chooseLayerEnrich.currentIndex()
        if len(layers) == 0:
            return
        layer = layers[selectedLayerIndex].layer()
        self.enrichTableResult.hide()
        while self.enrichTableResult.rowCount() > 0:
            self.enrichTableResult.removeRow(0)
        self.enrichTable.show()
        self.addEnrichedLayerRowButton.setEnabled(True)
        try:
            fieldnames = [field.name() for field in layer.fields()]
            while self.enrichTable.rowCount() > 0:
                self.enrichTable.removeRow(0)
            row = 0
            self.enrichTable.setColumnCount(9)
            self.enrichTable.setHorizontalHeaderLabels(
                ["Column", "EnrichmentConcept", "TripleStore", "Strategy", "content", "ID Column", "ID Property",
                 "ID Domain", "Language"])
            for field in fieldnames:
                item = QTableWidgetItem(field)
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                currentRowCount = self.enrichTable.rowCount()
                self.enrichTable.insertRow(row)
                self.enrichTable.setItem(row, 0, item)
                cbox = QComboBox()
                cbox.addItem("No Enrichment")
                cbox.addItem("Keep Local")
                cbox.addItem("Keep Remote")
                cbox.addItem("Replace Local")
                cbox.addItem("Merge")
                cbox.addItem("Ask User")
                cbox.addItem("Exclude")
                self.enrichTable.setCellWidget(row, 3, cbox)
                cbox = QComboBox()
                cbox.addItem("Enrich Value")
                cbox.addItem("Enrich URI")
                cbox.addItem("Enrich Both")
                self.enrichTable.setCellWidget(row, 4, cbox)
                cbox = QComboBox()
                for fieldd in fieldnames:
                    cbox.addItem(fieldd)
                self.enrichTable.setCellWidget(row, 5, cbox)
                itemm = QTableWidgetItem("http://www.w3.org/2000/01/rdf-schema#label")
                self.enrichTable.setItem(row, 6, itemm)
                itemm = QTableWidgetItem("")
                self.enrichTable.setItem(row, 7, itemm)
                itemm = QTableWidgetItem("")
                self.enrichTable.setItem(row, 8, itemm)
                celllayout = QHBoxLayout()
                upbutton = QPushButton("Up")
                removebutton = QPushButton("Remove", self)
                removebutton.clicked.connect(self.deleteEnrichRow)
                downbutton = QPushButton("Down")
                celllayout.addWidget(upbutton)
                celllayout.addWidget(downbutton)
                celllayout.addWidget(removebutton)
                w = QWidget()
                w.setLayout(celllayout)
                optitem = QTableWidgetItem()
                # self.enrichTable.setCellWidget(row,4,w)
                # self.enrichTable.setItem(row,3,cbox)
                row += 1
            self.originalRowCount = row
        except:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Layer not compatible for enrichment!")
            msgBox.setText("The chosen layer is not supported for enrichment. You possibly selected a raster layer")
            msgBox.exec()
            return

    #  @brief Deletes a row from the table in the enrichment dialog.
    #
    #  @param  send The sender of the request
    #
    def deleteEnrichRow(self, send):
        w = send.sender().parent()
        row = self.enrichTable.indexAt(w.pos()).row()
        self.enrichTable.removeRow(row)
        self.enrichTable.setCurrentCell(0, 0)

    ## Starts the process of layer enrichment according to the options selected in the enrichment dialog.
    #  @param self The object pointer.
    def enrichLayerProcess(self):
        layers = QgsProject.instance().layerTreeRoot().children()
        selectedLayerIndex = self.dlg.chooseLayerEnrich.currentIndex()
        self.enrichLayer = layers[selectedLayerIndex].layer().clone()
        attlist = {}
        itemlist = []
        propertylist = []
        excludelist = []
        resultmap = {}
        self.dlg.enrichTableResult.clear()
        self.dlg.enrichTableResult.setRowCount(0)
        self.dlg.enrichTableResult.setColumnCount(self.dlg.enrichTable.rowCount())
        fieldnames = []
        for row in range(self.dlg.enrichTable.rowCount()):
            fieldnames.append(self.dlg.enrichTable.item(row, 0).text())
        self.dlg.enrichTableResult.setHorizontalHeaderLabels(fieldnames)
        self.enrichLayer.startEditing()
        for row in range(self.dlg.enrichTable.rowCount()):
            idfield = self.dlg.enrichTable.cellWidget(row, 5).currentText()
            idprop = self.dlg.enrichTable.item(row, 6).text()
            if idprop == None or idprop == "":
                msgBox = QMessageBox()
                msgBox.setText(
                    "ID Property has not been specified for column " + str(self.dlg.enrichTable.item(row, 0).text()))
                msgBox.exec()
                return
            item = self.dlg.enrichTable.item(row, 0).text()
            propertyy = self.dlg.enrichTable.item(row, 1)
            triplestoreurl = ""
            if self.dlg.enrichTable.item(row, 2) != None:
                triplestoreurl = self.dlg.enrichTable.item(row, 2).text()
                print(self.dlg.enrichTable.item(row, 2).text())
            strategy = self.dlg.enrichTable.cellWidget(row, 3).currentText()
            content = ""
            if self.dlg.enrichTable.cellWidget(row, 4) != None:
                content = self.dlg.enrichTable.cellWidget(row, 4).currentText()
            if item != idfield:
                propertylist.append(self.dlg.enrichTable.item(row, 1))
            if strategy == "Exclude":
                excludelist.append(row)
            if strategy != "No Enrichment" and propertyy != None:
                progress = QProgressDialog("Enriching column " + self.dlg.enrichTable.item(row, 0).text(), "Abort", 0,
                                           0, self.dlg)
                progress.setWindowModality(Qt.WindowModal)
                progress.setWindowIcon(SPARQLUtils.sparqlunicornicon)
                progress.setCancelButton(None)
                self.qtask = EnrichmentQueryTask("Enriching column: " + self.dlg.enrichTable.item(row, 0).text(),
                                                 triplestoreurl, self.enrichLayer, strategy,
                                                 self.dlg.enrichTable.item(row, 8).text(), row,
                                                 len(self.enrichLayer.fields()),
                                                 self.dlg.enrichTable.item(row, 0).text(), self.dlg.enrichTable,
                                                 self.dlg.enrichTableResult, idfield, idprop,
                                                 self.dlg.enrichTable.item(row, 1), content, progress,
                                                 self.dlg.triplestoreconf)
                QgsApplication.taskManager().addTask(self.qtask)
            else:
                rowww = 0
                for f in self.enrichLayer.getFeatures():
                    if rowww >= self.dlg.enrichTableResult.rowCount():
                        self.dlg.enrichTableResult.insertRow(rowww)
                    # if item in f:
                    newitem = QTableWidgetItem(str(f[item]))
                    self.dlg.enrichTableResult.setItem(rowww, row, newitem)
                    # if ";" in str(newitem):
                    #    newitem.setBackground(QColor.red)
                    print(str(newitem))
                    rowww += 1
            self.enrichLayer.commitChanges()
            row += 1
        iface.vectorLayerTools().stopEditing(self.enrichLayer)
        self.enrichLayer.dataProvider().deleteAttributes(excludelist)
        self.enrichLayer.updateFields()
        self.dlg.enrichTable.hide()
        self.dlg.enrichTableResult.show()
        self.dlg.startEnrichment.setText("Enrichment Configuration")
        self.dlg.startEnrichment.clicked.disconnect()
        self.dlg.startEnrichment.clicked.connect(self.dlg.showConfigTable)
        self.dlg.addEnrichedLayerRowButton.setEnabled(False)
        return self.enrichLayer

    ## Adds a QGIS layer which has been previously enriched to QGIS.
    #  @param self The object pointer.
    def addEnrichedLayer(self):
        if self.enrichLayer == None:
            layers = QgsProject.instance().layerTreeRoot().children()
            selectedLayerIndex = self.dlg.chooseLayerEnrich.currentIndex()
            self.enrichLayer = layers[selectedLayerIndex].layer().clone()
        self.enrichLayerCounter += 1
        self.enrichLayer.setName(self.enrichLayer.name() + "_enrich" + str(self.enrichLayerCounter))
        self.enrichLayer.startEditing()
        row = 0
        fieldnames = [field.name() for field in self.enrichLayer.fields()]
        for f in self.enrichLayer.getFeatures():
            fieldcounter = 0
            for field in fieldnames:
                if self.dlg.enrichTableResult.item(row, fieldcounter) != None:
                    f[field] = self.dlg.enrichTableResult.item(row, fieldcounter).text()
                else:
                    f[field] = ""
                fieldcounter += 1
            self.enrichLayer.updateFeature(f)
            row += 1
        self.enrichLayer.commitChanges()
        iface.vectorLayerTools().stopEditing(self.enrichLayer)
        QgsProject.instance().addMapLayer(self.enrichLayer, True)
        canvas = iface.mapCanvas()
        canvas.setExtent(self.enrichLayer.extent())
        iface.messageBar().pushMessage("Add layer", "OK", level=Qgis.Success)
        self.dlg.close()

    ##
    #  @brief Shows the configuration table after creating an enrichment result.
    #
    #  @param  self The object pointer
    #
    def showConfigTable(self):
        self.enrichTableResult.hide()
        self.enrichTable.show()
        self.startEnrichment.setText("Start Enrichment")
        self.startEnrichment.clicked.disconnect()
        self.startEnrichment.clicked.connect(self.enrichLayerProcess)

    ## Prepares datastructures to export enrichments of a given layer configured in the enrichment dialog.
    #  @param self The object pointer.
    def exportEnrichedLayer(self):
        self.exportIdCol = ""
        self.exportNameSpace = self.dlg.interlinkNameSpace.text()
        self.exportSetClass = self.dlg.interlinkOwlClassInput.text()
        propurilist = []
        classurilist = []
        includelist = []
        proptypelist = []
        valuemappings = {}
        valuequeries = []
        for row in range(self.dlg.interlinkTable.rowCount()):
            item = self.dlg.interlinkTable.item(row, 0)
            if item.checkState():
                includelist.append(True)
                if self.dlg.interlinkTable.item(row, 1).checkState():
                    self.exportIdCol = self.dlg.interlinkTable.item(row, 3).text()
                    propurilist.append("")
                    classurilist.append("")
                    proptypelist.append("")
                else:
                    column = self.dlg.interlinkTable.item(row, 3).text()
                    if self.dlg.interlinkTable.item(row, 4) != None:
                        column = self.dlg.interlinkTable.item(row, 3).data(0)
                        propurilist.append(self.dlg.interlinkTable.item(row, 4).data(1))
                    else:
                        propurilist.append("")
                    if self.dlg.interlinkTable.item(row, 5) != None:
                        proptypelist.append(self.dlg.interlinkTable.item(row, 5).text())
                    else:
                        proptypelist.append("")
                    if self.dlg.interlinkTable.item(row, 6) != None:
                        concept = self.dlg.interlinkTable.item(row, 6).data(0)
                        self.dlg.exportColConfig[column] = concept
                        classurilist.append(concept)
                    else:
                        classurilist.append("")
                    if self.dlg.interlinkTable.item(row, 7) != None:
                        self.valueconcept = self.dlg.interlinkTable.item(row, 7).data(0)
                        valuemappings[item.text()] = self.dlg.interlinkTable.item(row, 7).data(1)
                        valuequeries.append({self.dlg.interlinkTable.item(row, 7).data(2),
                                             self.dlg.interlinkTable.item(row, 7).data(3)})
            else:
                includelist.append(False)
                propurilist.append("")
                classurilist.append("")
                proptypelist.append("")
        self.enrichedExport = True
        self.dlg.maindlg.exportLayer(propurilist, classurilist, includelist, proptypelist, valuemappings, valuequeries,
                                     self.dlg.exportTripleStore.isChecked())
