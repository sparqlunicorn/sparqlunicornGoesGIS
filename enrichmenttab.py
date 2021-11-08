from qgis.core import QgsProject, Qgis
from qgis.utils import iface
from .tasks.enrichmentquerytask import EnrichmentQueryTask
from qgis.PyQt.QtWidgets import QMessageBox, QProgressDialog, QTableWidgetItem
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsApplication
from .dialogs.warningLayerdlg import WarningLayerDlg

class EnrichmentTab:
    enrichLayer = None

    enrichedExport = False

    dlg = None

    qtask = None

    originalRowCount = 0

    enrichLayerCounter = 0

    def __init__(self, dlg):
        self.dlg = dlg

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
                progress.setCancelButton(None)
                self.qtask = EnrichmentQueryTask("Enriching column: " + self.dlg.enrichTable.item(row, 0).text(),
                                                 triplestoreurl, self.enrichLayer, strategy,
                                                 self.dlg.enrichTable.item(row, 8).text(), row,
                                                 len(self.enrichLayer.fields()),
                                                 self.dlg.enrichTable.item(row, 0).text(), self.dlg.enrichTable,
                                                 self.dlg.enrichTableResult, idfield, idprop,
                                                 self.dlg.enrichTable.item(row, 1), content, progress)
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
        existslayer = True
        if self.enrichLayer == None:
            layers = QgsProject.instance().layerTreeRoot().children()
            selectedLayerIndex = self.dlg.chooseLayerEnrich.currentIndex()
            if  selectedLayerIndex == -1:
                existslayer = False
                dlg = WarningLayerDlg()
                dlg.show()
                dlg.exec_()
            else:
                self.enrichLayer = layers[selectedLayerIndex].layer().clone()
        if existslayer is True:

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
                        self.exportColConfig[column] = concept
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
