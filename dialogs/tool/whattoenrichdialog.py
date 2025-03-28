from qgis.PyQt.QtWidgets import QDialog, QComboBox, QTableWidgetItem, QProgressDialog
from qgis.PyQt.QtWidgets import QHeaderView
from qgis.PyQt import uic
from qgis.core import QgsApplication
from qgis.PyQt.QtGui import QStandardItemModel
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtCore import QSortFilterProxyModel
from qgis.PyQt.QtGui import QStandardItem
from qgis.core import QgsMessageLog
from qgis.core import Qgis

from ...tasks.query.discovery.datasamplequerytask import DataSampleQueryTask
from ...tasks.query.discovery.dataschemaquerytask import DataSchemaQueryTask
from ...tasks.processing.layermatchingtask import LayerMatchingTask
from ...util.ui.uiutils import UIUtils
from ...util.sparqlutils import SPARQLUtils
from ...dialogs.util.searchdialog import SearchDialog
import os.path

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/whattoenrichdialog.ui'))

MESSAGE_CATEGORY = 'WhatToEnrichDialog'

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
    def __init__(self, languagemap,triplestoreconf, prefixes, enrichtable, layer, classid="", triplestoreurl=""):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.classid = classid
        self.languagemap=languagemap
        self.triplestoreurl = triplestoreurl
        self.triplestoreconf = triplestoreconf
        self.prefixes = prefixes
        self.enrichtable = enrichtable
        self.alreadyloadedSample=[]
        self.layer = layer
        """
        actionPan = QAction("Pan", self)
        actionPan.setCheckable(True)
        actionPan.triggered.connect(lambda: self.map_canvas.setMapTool(self.toolPan))
        self.toolPan = QgsMapToolPan(self.map_canvas)
        self.toolPan.setAction(actionPan)
        self.map_canvas.hide()
        uri = "url=http://a.tile.openstreetmap.org/{z}/{x}/{y}.png&zmin=0&type=xyz&zmax=19&crs=EPSG3857"
        self.mts_layer = QgsRasterLayer(uri, 'OSM', 'wms')
        if not self.mts_layer.isValid():
            print("Layer failed to load!")
        self.map_canvas.setExtent(self.mts_layer.extent())
        self.map_canvas.setLayers([self.mts_layer])
        self.map_canvas.setCurrentLayer(self.mts_layer)
        self.map_canvas.setMapTool(self.toolPan)
        """
        UIUtils.createLanguageSelectionCBox(self.languageComboBox,self.languagemap)
        self.tablemodel=QStandardItemModel()
        self.tablemodel.setHeaderData(0, Qt.Orientation.Horizontal, "Selection")
        self.tablemodel.setHeaderData(1, Qt.Orientation.Horizontal, "Attribute")
        self.tablemodel.setHeaderData(2, Qt.Orientation.Horizontal, "Sample Instances")
        self.tablemodel.insertRow(0)
        self.filter_proxy_model = QSortFilterProxyModel()
        self.filter_proxy_model.setSourceModel(self.tablemodel)
        self.filter_proxy_model.setFilterKeyColumn(1)
        self.searchResult.setModel(self.filter_proxy_model)
        self.tablemodel2=QStandardItemModel()
        self.tablemodel2.setHeaderData(0, Qt.Orientation.Horizontal, "Concept")
        self.tablemodel2.setHeaderData(1, Qt.Orientation.Horizontal, "Matching Attribute")
        self.tablemodel2.insertRow(0)
        self.selected=True
        self.toggleSelectionButton.clicked.connect(self.toggleSelect)
        self.filter_proxy_model2 = QSortFilterProxyModel()
        self.filter_proxy_model2.setSourceModel(self.tablemodel2)
        self.filter_proxy_model2.setFilterKeyColumn(1)
        self.backToMatchingSearchButton.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.stackedWidget.widget(1)))
        self.matchingConceptsResult.setModel(self.filter_proxy_model2)
        self.idCBox.setLayer(layer)
        item = QStandardItem()
        item.setText("Loading...")
        self.matchConceptsButton.clicked.connect(self.matchConceptsForIdentifier)
        self.matchingGroupBox.hide()
        self.tablemodel.setItem(0,0,item)
        self.searchResult.entered.connect(
            lambda modelindex: UIUtils.showTableURI(modelindex, self.searchResult, self.statusBarLabel))
        self.searchResult.doubleClicked.connect(
            lambda modelindex: UIUtils.openTableURL(modelindex, self.searchResult))
        self.matchingConceptsResult.doubleClicked.connect(
            lambda modelindex: UIUtils.openTableURL(modelindex, self.matchingConceptsResult))
        self.matchingConceptsResult.entered.connect(
            lambda modelindex: UIUtils.showTableURI(modelindex, self.matchingConceptsResult, self.statusBarLabel))
        for triplestore in self.triplestoreconf:
            if not "File" == triplestore["name"]:
                self.tripleStoreEdit.addItem(triplestore["name"])
        self.searchButton.clicked.connect(self.getAttributeStatistics)
        self.searchConceptButton.clicked.connect(self.createValueMappingSearchDialog)
        self.filterTableEdit.textChanged.connect(self.filter_proxy_model.setFilterRegularExpression)
        self.filterMatchingConceptsTableEdit.textChanged.connect(self.filter_proxy_model2.setFilterRegularExpression)
        self.conceptSearchEdit.textChanged.connect(self.searchResultObtained)
        self.filterTableComboBox.currentIndexChanged.connect(
            lambda: self.filter_proxy_model.setFilterKeyColumn(self.filterTableComboBox.currentIndex()))
        self.filterMatchingConceptsComboBox.currentIndexChanged.connect(
            lambda: self.filter_proxy_model2.setFilterKeyColumn(self.filterMatchingConceptsComboBox.currentIndex()))
        self.applyButton.clicked.connect(self.applyConceptToColumn)
        header =self.searchResult.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.searchResult.clicked.connect(self.loadSamples)

    def searchResultObtained(self,text):
        QgsMessageLog.logMessage("FILEPATH: " + str(text), MESSAGE_CATEGORY, Qgis.Info)
        if text[0].isdigit():
            spl=text.split("_")
            QgsMessageLog.logMessage("FILEPATH: " + str(spl), MESSAGE_CATEGORY, Qgis.Info)
            self.tripleStoreEdit.setCurrentIndex(int(spl[0]))
            self.conceptSearchEdit.setText(spl[1])
            self.matchingGroupBox.show()


    def matchConceptsForIdentifier(self):
        self.qtask3 = LayerMatchingTask("Matching candidates for chosen layer....",
                                          None,
                                          self.layer,
                                          self.idCBox.currentIndex(),
                                          self.matchCBox.currentText(),
                                          self, self.triplestoreconf[self.tripleStoreEdit.currentIndex()],
                                          self.conceptSearchEdit.text(),self.tablemodel2,self.languageComboBox.currentData(UIUtils.dataslot_language))
        QgsApplication.taskManager().addTask(self.qtask3)

    #  @brief Creates a search dialog to search for a concept.
    #  
    #  @param self The object pointer
    #  @param row A row value for the search dialog
    #  @param column A column value for the search dialog
    #  @return Return description 
    def createValueMappingSearchDialog(self, row=-1, column=-1):
        self.buildSearchDialog(row, column, -1, self.conceptSearchEdit)

    def toggleSelect(self):
        self.selected=not self.selected
        for row in range(self.tablemodel.rowCount()):
            if self.selected:
                self.tablemodel.item(row, 0).setCheckState(Qt.CheckState.Checked)
            else:
                self.tablemodel.item(row, 0).setCheckState(Qt.CheckState.Unchecked)


    def loadSamples(self,modelindex):
        row=modelindex.row()
        column=modelindex.column()
        if column==2 and row not in self.alreadyloadedSample and row!=self.searchResult.model().rowCount()-1:
            relation = str(self.searchResult.model().index(row, column-1).data(256))
            self.qtask2 = DataSampleQueryTask("Querying data sample.... (" + str(relation) + ")",
                                             self.triplestoreurl,
                                             self,
                                             self.conceptSearchEdit.text(),
                                             relation,
                                             column,row,self.triplestoreconf[self.tripleStoreEdit.currentIndex()],
                                              self.tablemodel,None,SPARQLUtils.geoclassnode)
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
        self.interlinkdialog = SearchDialog(column, row, self.triplestoreconf, self.prefixes, self.languagemap, interlinkOrEnrich, table,
                                            True)
        self.interlinkdialog.setMinimumSize(650, 500)
        self.interlinkdialog.setWindowTitle("Search Property or Class")
        self.interlinkdialog.exec()

    ## 
    #  @brief Gives statistics about most commonly occuring properties from a certain class in a given triple store.
    #  
    #  @param [in] self The object pointer
    #  @return A list of properties with their occurance given in percent
    def getAttributeStatistics(self, concept="wd:Q3914", endpoint_url="https://query.wikidata.org/sparql",
                               labellang="en", inarea="wd:Q183"):
        self.stackedWidget.setCurrentWidget(self.stackedWidget.widget(2))
        if self.conceptSearchEdit.text() == "":
            return
        progress = QProgressDialog("Executing enrichment search query....", "Abort", 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setWindowIcon(UIUtils.sparqlunicornicon)
        progress.setCancelButton(None)
        conceptstoenrich=[]
        for row in range(self.tablemodel2.rowCount(self.matchingConceptsResult.rootIndex())):
            child_index = self.tablemodel2.index(row, 0, self.matchingConceptsResult.rootIndex())
            conceptstoenrich.append(child_index.data(0))
        self.qtask = DataSchemaQueryTask("Get Property Enrichment Candidates (" + self.conceptSearchEdit.text() + ")",
                                           self.triplestoreconf[self.tripleStoreEdit.currentIndex()]["resource"],
                                           SPARQLUtils.queryPreProcessing(self.triplestoreconf[self.tripleStoreEdit.currentIndex()]["whattoenrichquery"],self.triplestoreconf,self.conceptSearchEdit.text(),False),
                                           self.conceptSearchEdit.text(),
                                           self.prefixes[self.tripleStoreEdit.currentIndex()] if self.tripleStoreEdit.currentIndex() in self.prefixes else None,
                                           self.tablemodel,
                                           self.triplestoreconf[self.tripleStoreEdit.currentIndex()],
                                           progress,
                                           self,None,conceptstoenrich)
        QgsApplication.taskManager().addTask(self.qtask)

    ## 
    #  @brief Returns a chosen concept to the calling dialog.
    #  
    #  @param [in] self The object pointer
    #  @param [in] costumURI indicates whether a URI has been entered by the user or if a URI should be selected in the result list widget
    #  @return A URI and possibly its label as a String
    def applyConceptToColumn(self, costumURI=False):
        fieldnames = [field.name() for field in self.layer.fields()]
        for row in range(self.tablemodel.rowCount()):
            if self.tablemodel.item(row, 0).checkState()==Qt.CheckState.Checked:
                relation = self.tablemodel.item(row, 1).data(UIUtils.dataslot_conceptURI)
                text=self.tablemodel.item(row, 1).text()
                item = QTableWidgetItem(
                    text[0:text.rfind('(') - 1])
                # item.setFlags(QtCore.Qt.ItemIsEnabled)
                row = self.enrichtable.rowCount()
                self.enrichtable.insertRow(row)
                self.enrichtable.setItem(row, 0, item)
                item = QTableWidgetItem()
                item.setData(UIUtils.dataslot_conceptURI, relation)
                item.setText(text)
                self.enrichtable.setItem(row, 1, item)
                item = QTableWidgetItem()
                item.setText(str(self.triplestoreconf[self.tripleStoreEdit.currentIndex()]["resource"]["url"]))
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
                cbox.setCurrentIndex(self.idCBox.currentIndex())
                itemm = QTableWidgetItem("http://www.w3.org/2000/01/rdf-schema#label")
                self.enrichtable.setItem(row, 6, itemm)
                itemm = QTableWidgetItem(self.conceptSearchEdit.text())
                self.enrichtable.setItem(row, 7, itemm)
                itemm = QTableWidgetItem(self.languageComboBox.currentText())
                itemm.setData(UIUtils.dataslot_language,self.languageComboBox.currentData(UIUtils.dataslot_language))
                self.enrichtable.setItem(row, 8, itemm)
        self.close()
