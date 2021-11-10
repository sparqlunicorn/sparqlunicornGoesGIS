import os
import re
import json
import sys
from qgis.PyQt import QtWidgets
from qgis.PyQt import uic
from qgis.core import QgsProject
import xml.etree.ElementTree as ET
from qgis.utils import iface
from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QTableWidgetItem, QMessageBox, QFileDialog
from ..dialogs.whattoenrichdialog import EnrichmentDialog
from ..enrichmenttab import EnrichmentTab
from ..interlinkingtab import InterlinkingTab
from qgis.PyQt.QtCore import QRegExp, QSortFilterProxyModel, Qt, QUrl
from qgis.PyQt.QtGui import QRegExpValidator, QStandardItemModel, QDesktopServices
from ..dialogs.triplestoredialog import TripleStoreDialog
from ..dialogs.searchdialog import SearchDialog
from qgis.core import QgsProject, Qgis
from qgis.utils import iface
# from .tasks.enrichmentquerytask import EnrichmentQueryTask
from qgis.PyQt.QtWidgets import QMessageBox, QProgressDialog, QTableWidgetItem, QComboBox
from qgis.PyQt.QtCore import Qt
from qgis.core import QgsApplication
from ..dialogs.warningLayerdlg import WarningLayerDlg
from ..dialogs.triplestoredialog import TripleStoreDialog
from ..dialogs.searchdialog import SearchDialog

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/Enrichment.ui'))

MESSAGE_CATEGORY = 'Enrichment MainWindow'


class EnrichmentMainWindow(QtWidgets.QMainWindow, FORM_CLASS):
    ## The triple store configuration file

    sparqlunicorndlg = None

    def __init__(self,layers, addVocabConf, triplestoreconf, prefixes, prefixstore, comboBox, maindlg=None,  parent=None):
        """Constructor."""
        super(EnrichmentMainWindow, self).__init__(parent)
        self.sparqlunicorndlg = maindlg
        self.setupUi(self)

        self.loadUnicornLayers(layers)
        self.addVocabConf = addVocabConf
        self.prefixes = prefixes
        self.triplestoreconf = triplestoreconf
        self.searchTripleStoreDialog = TripleStoreDialog(triplestoreconf, prefixes, prefixstore,comboBox)

        self.enrichtab = EnrichmentTab(self)



        self.enrichTable.cellClicked.connect(self.createEnrichSearchDialog)
        self.addEnrichedLayerButton.clicked.connect(self.enrichtab.addEnrichedLayer)
        self.startEnrichment.clicked.connect(self.enrichtab.enrichLayerProcess)
        self.loadLayerEnrich.clicked.connect(self.loadLayerForEnrichment)
        self.addEnrichedLayerRowButton.clicked.connect(self.addEnrichRow)
        self.whattoenrich.clicked.connect(self.createWhatToEnrich)
        # self.refreshLayersEnrich.clicked.connect(self.sparqlunicorndlg.loadUnicornLayers)



    def loadUnicornLayers(self, layers):
        # Populate the comboBox with names of all the loaded unicorn layers

        for layer in layers:
            ucl = layer.name()
            # if type(layer) == QgsMapLayer.VectorLayer:
            # self.loadedLayers.addItem(layer.name())
            # self.chooseLayerInterlink.addItem(layer.name())
            self.chooseLayerEnrich.addItem(layer.name())


# functions:

    def createEnrichSearchDialog(self, row=-1, column=-1):
        if column == 1:
            self.sparqlunicorndlg.buildSearchDialog(row, column, False, self.enrichTable, False, False, None, self.addVocabConf)
        if column == 6:
            self.sparqlunicorndlg.buildSearchDialog(row, column, False, self.enrichTable, False, False, None, self.addVocabConf)
    #
    # def createEnrichSearchDialogProp(self, row=-1, column=-1):
    #     self.buildSearchDialog(row, column, False, self.findIDPropertyEdit, True, False, None, self.addVocabConf)


        ##

    #  @brief Deletes a row from the table in the enrichment dialog.
    #
    #  @param  send The sender of the request
    #
    # def deleteEnrichRow(self, send):
    #     w = send.sender().parent()
    #     row = self.enrichTable.indexAt(w.pos()).row()
    #     self.enrichTable.removeRow(row);
    #     self.enrichTable.setCurrentCell(0, 0)

    ##
    #  @brief Adds a new row to the table in the enrichment dialog.
    #
    #  @param  self The object pointer
    #
    # Check if wrongly using the button causes python error (may need to add a warning ui/py)

    def addEnrichRow(self):
        layers = QgsProject.instance().layerTreeRoot().children()
        selectedLayerIndex = self.chooseLayerEnrich.currentIndex()
        if  selectedLayerIndex == -1:
            dlg = WarningLayerDlg()
            dlg.show()
            dlg.exec_()
        else:
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
    #  @brief Creates a What To Enrich dialog with parameters given.
    #
    #  @param self The object pointer
    def createWhatToEnrich(self):
        if self.enrichTable.rowCount() == 0:
            return
        layers = QgsProject.instance().layerTreeRoot().children()
        selectedLayerIndex = self.chooseLayerEnrich.currentIndex()
        layer = layers[selectedLayerIndex].layer()
        self.searchTripleStoreDialog = EnrichmentDialog(self.triplestoreconf, self.prefixes, self.enrichTable, layer,
                                                        None, None)
        self.searchTripleStoreDialog.setMinimumSize(700, 500)
        self.searchTripleStoreDialog.setWindowTitle("Enrichment Search")
        self.searchTripleStoreDialog.exec_()


    def loadLayerForEnrichment(self):

        layers = QgsProject.instance().layerTreeRoot().children()
        selectedLayerIndex = self.chooseLayerEnrich.currentIndex()
        if  selectedLayerIndex == -1 or len(layers) == 0:
            dlg = WarningLayerDlg()
            dlg.show()
            dlg.exec_()
        else:
            # if len(layers) == 0:
            #     return
            layer = layers[selectedLayerIndex].layer()
            # self.enrichTableResult.hide()
            # while self.enrichTableResult.rowCount() > 0:
            #     self.enrichTableResult.removeRow(0);
            # self.enrichTable.show()
            self.addEnrichedLayerRowButton.setEnabled(True)
            try:
                fieldnames = [field.name() for field in layer.fields()]
                while self.enrichTable.rowCount() > 0:
                    self.enrichTable.removeRow(0);
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
        self.startEnrichment.clicked.connect(self.enrichtab.enrichLayerProcess)
