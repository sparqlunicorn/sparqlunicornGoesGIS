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
from qgis.PyQt.QtWidgets import QTableWidgetItem, QMessageBox, QFileDialog, QComboBox
from ..enrichmenttab import EnrichmentTab
from ..interlinkingtab import InterlinkingTab
from qgis.PyQt.QtCore import QRegExp, QSortFilterProxyModel, Qt, QUrl
from qgis.PyQt.QtGui import QRegExpValidator, QStandardItemModel, QDesktopServices
from ..dialogs.triplestoredialog import TripleStoreDialog
from ..dialogs.searchdialog import SearchDialog
from ..dialogs.warningLayerdlg import WarningLayerDlg
# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/Interlink.ui'))

MESSAGE_CATEGORY = 'Interlink MainWindow'

##
#  @brief The main dialog window that manages interlink for the sparqlunicorn plugins
class InterlinkMainWindow(QtWidgets.QMainWindow, FORM_CLASS):

    sparqlunicorndlg = None

    interlinktab = None

    enrichtab = None

    def __init__(self, layers, maindlg, addVocabConf, triplestoreconf, prefixes, prefixstore, comboBox, dlg=None,  parent=None):
        """Constructor."""
        super(InterlinkMainWindow, self).__init__(parent)


        self.sparqlunicorndlg = dlg
        self.setupUi(self)
        self.loadUnicornLayers(layers)
        self.maindlg = maindlg
        self.addVocabConf = addVocabConf
        self.prefixes = prefixes
        self.triplestoreconf = triplestoreconf
        self.searchTripleStoreDialog = TripleStoreDialog(triplestoreconf, prefixes, prefixstore,
                                                          comboBox)
        self.enrichtab = EnrichmentTab(self)
        self.interlinktab = InterlinkingTab(self)  #perhaps "self" needs to be replaced by "sparqlunicorndlg"
        # self.refreshLayersInterlink.clicked.connect(self.loadUnicornLayers)
        self.interlinkTable.cellClicked.connect(self.createInterlinkSearchDialog)
         # self.chooseLayerInterlink.clear()
        self.searchClass.clicked.connect(self.createInterlinkSearchDialog)
        self.searchClass.setToolTip('Will open the interlink search dialog when clicked.')
        urlregex = QRegExp("http[s]?://(?:[a-zA-Z#]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        urlvalidator = QRegExpValidator(urlregex, self)
        self.interlinkNameSpace.setValidator(urlvalidator)
        self.interlinkNameSpace.textChanged.connect(self.check_state3)
        self.interlinkNameSpace.textChanged.emit(self.interlinkNameSpace.text())
        self.exportMappingButton.clicked.connect(self.interlinktab.exportMapping)
        self.exportMappingButton.setToolTip('When clicked this will open your file directory and allow you to export the mapping you just created')
        self.importMappingButton.clicked.connect(self.interlinktab.loadMapping)
        self.importMappingButton.setToolTip('When clicked this will open your file directory and allow you to import a mapping of your choosing.')
        self.loadLayerInterlink.clicked.connect(self.loadLayerForInterlink)
        self.loadLayerInterlink.setToolTip('will load your current layer in the "Interlink Table" ')
        self.exportInterlink.clicked.connect(self.enrichtab.exportEnrichedLayer)
        self.exportInterlink.setToolTip('When clicked this will open your file directory and allow you to export the interlink that you just created.')



    def loadUnicornLayers(self, layers):
        # Populate the comboBox with names of all the loaded unicorn layers

        for layer in layers:
            ucl = layer.name()
            # if type(layer) == QgsMapLayer.VectorLayer:
            # self.loadedLayers.addItem(layer.name())
            self.chooseLayerInterlink.addItem(layer.name())
            # self.chooseLayerEnrich.addItem(layer.name())

    ##
    #  @brief Creates a search dialog with parameters for interlinking.
    #
    #  @param self The object pointer
    #  @param row The row of the table for which to map the search result
    #  @param column The column of the table for which to map the search result
    def createInterlinkSearchDialog(self, row=-1, column=-1):
        if column > 3 and column < 7:
            self.buildSearchDialog(row, column, True, self.interlinkTable, True, False, None, self.addVocabConf)
        elif column >= 7:
            layers = QgsProject.instance().layerTreeRoot().children()
            selectedLayerIndex = self.chooseLayerInterlink.currentIndex()
            layer = layers[selectedLayerIndex].layer()
            self.buildValueMappingDialog(row, column, True, self.interlinkTable, layer)
        elif column == -1:
            self.buildSearchDialog(row, column, -1, self.interlinkOwlClassInput, False, False, None, self.addVocabConf)

    ##
    #  @brief Builds a value mapping dialog window for ther interlinking dialog.
    #
    #  @param self The object pointer
    #  @param row The row of the table for which to map the value
    #  @param column The column of the table for which to map the value
    #  @param table The table in which to save the value mapping result
    #  @param layer The layer which is concerned by the enrichment oder interlinking
    def buildValueMappingDialog(self, row, column, interlinkOrEnrich, table, layer):
        self.currentcol = column
        self.currentrow = row
        valuemap = None
        if table.item(row, column) != None and table.item(row, column).text() != "":
            valuemap = table.item(row, column).data(1)
        self.interlinkdialog = ValueMappingDialog(column, row, self.triplestoreconf, interlinkOrEnrich, table,
                                                  table.item(row, 3).text(), layer, valuemap)
        self.interlinkdialog.setMinimumSize(650, 400)
        self.interlinkdialog.setWindowTitle("Get Value Mappings for column " + table.item(row, 3).text())
        self.interlinkdialog.exec_()

    def check_state3(self):
        self.searchTripleStoreDialog.check_state(self.interlinkNameSpace)


    ##
    #  @brief Loads a QGIS layer for interlinking into the interlinking dialog.
    #
    #  @param self The object pointer
    def loadLayerForInterlink(self):
        print("1")
        layers = QgsProject.instance().layerTreeRoot().children()
        selectedLayerIndex = self.chooseLayerInterlink.currentIndex()
        if  selectedLayerIndex == -1:
            print("delta")
            dlg = WarningLayerDlg()
            dlg.show()
            dlg.exec_()
        else:
            print("2")
        # if len(layers) == 0:
        #     print("3")

            # if  selectedLayerIndex == -1:
            #     print("4")
            #     dlg = WarningLayerDlg()
            #     dlg.show()
            #     dlg.exec_()
            # else:

                # return
            layer = layers[selectedLayerIndex].layer()
            # Print("5")
            while self.interlinkTable.rowCount() > 0:
                self.interlinkTable.removeRow(0);

            fieldnames = [field.name() for field in layer.fields()]



        # try:
            # print("6")
            # fieldnames = [field.name() for field in layer.fields()]
            #
            # while self.interlinkTable.rowCount() > 0:
            #     self.interlinkTable.removeRow(0);
            #     print("here")
            # row = 0
            # self.interlinkTable.setHorizontalHeaderLabels(
            #     ["Export?", "IDColumn?", "GeoColumn?", "Column", "ColumnProperty", "PropertyType", "ColumnConcept",
            #      "ValueConcepts"])
            # self.interlinkTable.setColumnCount(8)
            try:
                fieldnames = [field.name() for field in layer.fields()]

                while self.interlinkTable.rowCount() > 0:
                    self.interlinkTable.removeRow(0);
                row = 0
                    # print("here")
                for field in fieldnames:
                    print("3")
                    item = QTableWidgetItem(field)
                    # item.setFlags(QtCore.Qt.ItemIsEnabled)
                    print("here")
                    item2 = QTableWidgetItem()
                    item2.setCheckState(True)
                    item3 = QTableWidgetItem()
                    item3.setCheckState(False)
                    item4 = QTableWidgetItem()
                    item4.setCheckState(False)
                    print("4")
                    self.interlinkTable.insertRow(row)
                    self.interlinkTable.setItem(row, 3, item)
                    self.interlinkTable.setItem(row, 0, item2)
                    self.interlinkTable.setItem(row, 1, item3)
                    self.interlinkTable.setItem(row, 2, item4)
                    print("5")
                    cbox = QComboBox()
                    cbox.addItem("Automatic")
                    cbox.addItem("AnnotationProperty")
                    cbox.addItem("DataProperty")
                    cbox.addItem("ObjectProperty")
                    cbox.addItem("SubClass")
                    print("6")
                    self.interlinkTable.setCellWidget(row, 5, cbox)
                    currentRowCount = self.interlinkTable.rowCount()
                    row += 1
            except:
                print("A")
                msgBox = QMessageBox()
                msgBox.setWindowTitle("Layer not compatible for interlinking!")
                msgBox.setText("The chosen layer is not supported for interlinking. You possibly selected a raster layer")
                msgBox.exec()
                print("B")
                return

    ##
    #  @brief Builds the search dialog to search for a concept or class.
    #  @param  self The object pointer
    #  @param  row the row to insert the result
    #  @param  column the column to insert the result
    #  @param  interlinkOrEnrich indicates if the dialog is meant for interlinking or enrichment
    #  @param  table the GUI element to display the result
    def buildSearchDialog(self, row, column, interlinkOrEnrich, table, propOrClass, bothOptions=False,
                          currentprefixes=None, addVocabConf=None):
        self.currentcol = column
        self.currentrow = row
        self.interlinkdialog = SearchDialog(column, row, self.triplestoreconf, self.prefixes, interlinkOrEnrich, table,
                                            propOrClass, bothOptions, currentprefixes, addVocabConf)
        self.interlinkdialog.setMinimumSize(650, 400)
        self.interlinkdialog.setWindowTitle("Search Interlink Concept")
        self.interlinkdialog.exec_()



    ## Prepares datastructures to export enrichments of a given layer configured in the enrichment dialog.
    #  @param self The object pointer.
    def exportEnrichedLayer(self):

        if self.conceptSearchEdit.text() == "":
            # @Antoine
            msgBox = QMessageBox()
            msgBox.setWindowTitle("WARNING ")
            msgBox.setText('Concept search is empty please choose a concept by clicking the "search concept" button to proceed.')
            msgBox.exec()
            # return
        else:
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
