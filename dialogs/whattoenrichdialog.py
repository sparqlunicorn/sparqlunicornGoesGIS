from qgis.PyQt.QtWidgets import QDialog, QComboBox, QTableWidgetItem, QProgressDialog
from qgis.PyQt.QtWidgets import QHeaderView
from qgis.PyQt import uic
from qgis.core import QgsApplication
from qgis.PyQt.QtGui import QStandardItemModel
from qgis.PyQt.QtCore import Qt, QUrl
from qgis.PyQt.QtCore import QSortFilterProxyModel
from qgis.PyQt.QtGui import QDesktopServices,QStandardItem

from ..tasks.dataschemaquerytask import DataSchemaQueryTask
from ..util.ui.uiutils import UIUtils
from ..util.sparqlutils import SPARQLUtils
from ..tasks.datasamplequerytask import DataSampleQueryTask
from ..dialogs.searchdialog import SearchDialog
from ..tasks.whattoenrichquerytask import WhatToEnrichQueryTask
import os.path

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/whattoenrichdialog.ui'))


## Enrichment dialog to enrich properties to a geodataset.
class EnrichmentDialog(QDialog, FORM_CLASS):
    # Indicates the position within the given GUI element to which the result is returned.
    currentrow = ""
    # The triplestore configuration of the plugin.
    triplestoreconf = ""
    # Indicates whether this dialog was called from an enrichment or interlinking interface.
    interlinkOrEnrich = False
    # The GUI element to which the result of this dialog is returned.
    table = False
    qtask = None

    ##Initializes this dialog.
    # @param triplestoreconf The triplestore configuration file
    # @param prefixes RDF prefixes to be used in this dialog
    # @param enrichtable the GUI object to save the results in
    # @param layer the layer to enrich
    # @param classid the classid to use for enrichment
    # @param triplestoreurl the url of the triplestore to use for enrichment
    def __init__(self, triplestoreconf, prefixes, enrichtable, layer, classid="", triplestoreurl=""):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.classid = classid
        self.triplestoreurl = triplestoreurl
        self.triplestoreconf = triplestoreconf
        self.prefixes = prefixes
        self.enrichtable = enrichtable
        self.alreadyloadedSample=[]
        self.layer = layer
        self.tablemodel=QStandardItemModel()
        self.tablemodel.setHeaderData(0, Qt.Horizontal, "Selection")
        self.tablemodel.setHeaderData(1, Qt.Horizontal, "Attribute")
        self.tablemodel.setHeaderData(2, Qt.Horizontal, "Sample Instances")
        self.tablemodel.insertRow(0)
        self.filter_proxy_model = QSortFilterProxyModel()
        self.filter_proxy_model.setSourceModel(self.tablemodel)
        self.filter_proxy_model.setFilterKeyColumn(1)
        self.searchResult.setModel(self.filter_proxy_model)
        fieldnames = [field.name() for field in layer.fields()]
        for field in fieldnames:
            self.idCBox.addItem(field)
        item = QStandardItem()
        item.setText("Loading...")
        self.tablemodel.setItem(0,0,item)
        self.searchResult.entered.connect(
            lambda modelindex: UIUtils.showTableURI(modelindex, self.searchResult, self.statusBarLabel))
        self.searchResult.doubleClicked.connect(
            lambda modelindex: UIUtils.openTableURL(modelindex, self.searchResult))
        for triplestore in self.triplestoreconf:
            if not "File" == triplestore["name"]:
                self.tripleStoreEdit.addItem(triplestore["name"])
        self.searchButton.clicked.connect(self.getAttributeStatistics)
        self.searchConceptButton.clicked.connect(self.createValueMappingSearchDialog)
        #self.costumpropertyLabel.hide()
        #self.inAreaEditText.hide()
        #self.searchButton2.clicked.connect(self.getAttributeStatistics)
        #self.searchButton2.hide()
        self.applyButton.clicked.connect(self.applyConceptToColumn)
        header =self.searchResult.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.searchResult.clicked.connect(self.loadSamples)


    #  @brief Creates a search dialog to search for a concept.
    #  
    #  @param self The object pointer
    #  @param row A row value for the search dialog
    #  @param column A column value for the search dialog
    #  @return Return description 
    def createValueMappingSearchDialog(self, row=-1, column=-1):
        self.buildSearchDialog(row, column, -1, self.conceptSearchEdit)

    def loadSamples(self,modelindex):
        row=modelindex.row()
        column=modelindex.column()
        if column==2 and row not in self.alreadyloadedSample and row!=self.dataSchemaTableView.model().rowCount()-1:
            relation = str(self.dataSchemaTableView.model().index(row, column-1).data(256))
            self.qtask2 = DataSampleQueryTask("Querying dataset schema.... (" + self.label + ")",
                                             self.triplestoreurl,
                                             self,
                                             self.concept,
                                             relation,
                                             column,row,self.triplestoreconf[self.curindex],self.tablemodel,self.map_canvas)
            QgsApplication.taskManager().addTask(self.qtask2)
            self.alreadyloadedSample.append(row)

    ## 
    #  @brief Builds the search dialog for the concept search
    #  
    #  @param self The object pointer
    #  @param row The row for enrichment
    #  @param column The column for enrichment
    #  @param interlinkOrEnrich Indicates if enrichment or interlinking is calling this dialog
    #  @param table The UI element used for displaying results
    def buildSearchDialog(self, row, column, interlinkOrEnrich, table):
        self.currentcol = column
        self.currentrow = row
        self.interlinkdialog = SearchDialog(column, row, self.triplestoreconf, self.prefixes, interlinkOrEnrich, table,
                                            True)
        self.interlinkdialog.setMinimumSize(650, 500)
        self.interlinkdialog.setWindowTitle("Search Property or Class")
        self.interlinkdialog.exec_()

    ## 
    #  @brief Gives statistics about most commonly occuring properties from a certain class in a given triple store.
    #  
    #  @param [in] self The object pointer
    #  @return A list of properties with their occurance given in percent
    def getAttributeStatistics(self, concept="wd:Q3914", endpoint_url="https://query.wikidata.org/sparql",
                               labellang="en", inarea="wd:Q183"):
        if self.conceptSearchEdit.text() == "":
            return
        concept = "<" + self.conceptSearchEdit.text() + ">"
        progress = QProgressDialog("Executing enrichment search query....", "Abort", 0, 0, self)
        progress.setWindowTitle("Enrichment Search Query")
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowIcon(SPARQLUtils.sparqlunicornicon)
        progress.setCancelButton(None)
        self.qtask =DataSchemaQueryTask("Get Property Enrichment Candidates (" + self.conceptSearchEdit.text() + ")",
                            self.triplestoreconf[self.tripleStoreEdit.currentIndex()]["endpoint"],
                            self.triplestoreconf[self.tripleStoreEdit.currentIndex()][
                                "whattoenrichquery"].replace("%%concept%%", concept),
                            self.conceptSearchEdit.text(),
                            self.prefixes[self.tripleStoreEdit.currentIndex()] if self.tripleStoreEdit.currentIndex() in self.prefixes else None,
                            self.tablemodel, self.triplestoreconf[self.tripleStoreEdit.currentIndex()], progress, self)
        #self.qtask = DataSchemaQueryTask("Get Property Enrichment Candidates (" + self.conceptSearchEdit.text() + ")",
        #                                   endpoint_url,
        #                                   self.triplestoreconf[self.tripleStoreEdit.currentIndex()][
        #                                       "whattoenrichquery"].replace("%%concept%%", concept).replace("%%area%%",
        #                                                                                                    "?area"),
        #                                   self.conceptSearchEdit.text(),
        #                                   self.prefixes[self.tripleStoreEdit.currentIndex()],
        #                                   self.searchResult,self.triplestoreconf[self.tripleStoreEdit.currentIndex()], progress)
        QgsApplication.taskManager().addTask(self.qtask)

    ## 
    #  @brief Returns a chosen concept to the calling dialog.
    #  
    #  @param [in] self The object pointer
    #  @param [in] costumURI indicates whether a URI has been entered by the user or if a URI should be selected in the result list widget
    #  @return A URI and possibly its label as a String
    def applyConceptToColumn(self, costumURI=False):
        fieldnames = [field.name() for field in self.layer.fields()]
        item = QTableWidgetItem(
            self.searchResult.currentItem().text()[0:self.searchResult.currentItem().text().rfind('(') - 1])
        # item.setFlags(QtCore.Qt.ItemIsEnabled)
        row = self.enrichtable.rowCount()
        self.enrichtable.insertRow(row)
        self.enrichtable.setItem(row, 0, item)
        item = QTableWidgetItem()
        item.setData(1, self.searchResult.currentItem().data(1))
        item.setText(self.searchResult.currentItem().text())
        self.enrichtable.setItem(row, 1, item)
        item = QTableWidgetItem()
        item.setText(self.triplestoreconf[self.tripleStoreEdit.currentIndex() + 1]["endpoint"])
        self.enrichtable.setItem(row, 2, item)
        cbox = QComboBox()
        cbox.addItem("Get Remote")
        cbox.addItem("No Enrichment")
        cbox.addItem("Exclude")
        self.enrichtable.setCellWidget(row, 3, cbox)
        cbox = QComboBox()
        cbox.addItem("Enrich Value")
        cbox.addItem("Enrich URI")
        cbox.addItem("Enrich Both")
        self.enrichtable.setCellWidget(row, 4, cbox)
        cbox = QComboBox()
        for fieldd in fieldnames:
            cbox.addItem(fieldd)
        self.enrichtable.setCellWidget(row, 5, cbox)
        itemm = QTableWidgetItem("http://www.w3.org/2000/01/rdf-schema#label")
        self.enrichtable.setItem(row, 6, itemm)
        itemm = QTableWidgetItem(self.conceptSearchEdit.text())
        self.enrichtable.setItem(row, 7, itemm)
        itemm = QTableWidgetItem("")
        self.enrichtable.setItem(row, 8, itemm)
        self.close()