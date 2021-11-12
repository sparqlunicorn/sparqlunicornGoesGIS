from qgis.PyQt.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QListWidget, QComboBox, QMessageBox, \
    QRadioButton, QListWidgetItem, QTableWidgetItem, QProgressDialog
from qgis.PyQt.QtCore import QRegExp, Qt
from qgis.PyQt import uic
from qgis.core import QgsProject, QgsApplication, QgsMessageLog
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
    def __init__(self, triplestoreconf, prefixes, enrichtable, layer, classid="", triplestoreurl="", addVocab=None):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.classid = classid
        self.triplestoreurl = triplestoreurl
        self.triplestoreconf = triplestoreconf
        self.prefixes = prefixes
        self.enrichtable = enrichtable
        self.layer = layer
        for triplestore in self.triplestoreconf:
            if not "File" == triplestore["name"]:
                self.tripleStoreEdit.addItem(triplestore["name"])
                # me
                # tripleStoreEdit = QComboBox(self)
                # tripleStoreEdit.addItem("Wikidata")
                # tripleStoreEdit.addItem("DBPedia")
        if addVocab != None:
            for cov in addVocab:
                self.tripleStoreEdit.addItem(addVocab[cov]["label"])
                self.tripleStoreEdit.setCurrentIndex(2)
                self.tripleStoreEdit.setEnabled(True)
                # me
        self.searchButton.clicked.connect(self.getAttributeStatistics)
        self.searchConceptButton.clicked.connect(self.createValueMappingSearchDialog)
        self.costumpropertyLabel.hide()
        self.inAreaEditText.hide()
        self.searchButton2.clicked.connect(self.getAttributeStatistics)
        self.searchButton2.hide()
        self.applyButton.clicked.connect(self.applyConceptToColumn)
        # me

        # tripleStoreEdit.activated[str].connect(self.onActivated)
        # me

        ##

    #  @brief Creates a search dialog to search for a concept.
    #
    #  @param self The object pointer
    #  @param row A row value for the search dialog
    #  @param column A column value for the search dialog
    #  @return Return description
    def createValueMappingSearchDialog(self, row=-1, column=-1):
        self.buildSearchDialog(row, column, -1, self.conceptSearchEdit)

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
# msg box instead of return to tell the user that concept search is empty and that they need to choose a concept.
        if self.conceptSearchEdit.text() == "":
            # @Antoine
            msgBox = QMessageBox()
            msgBox.setWindowTitle("WARNING ")
            msgBox.setText('Concept search is empty please choose a concept by clicking the "search concept" button to proceed.')
            msgBox.exec()
            # return
        else:
        # @Antoine

# Defines the variable "concept" , which is a string composed of the three concatenated strings"<" + self.conceptSearchEdit.text() + ">"
            concept = "<" + self.conceptSearchEdit.text() + ">"
# Defines the variable "progress"  which is an instances of the "QProgressDialog" class and is initiated through its Constructor
            progress = QProgressDialog("Executing enrichment search query....", "Abort", 0, 0, self)
            # here progress calls its "setWindowModality" function and provides (Qt.WindowModal) as a parameter of this function.
            progress.setWindowModality(Qt.WindowModal)
            # calls  its "setCancelButton function and provides "None" as its parameter value
            progress.setCancelButton(None)
            # "What to enrich" defines its attribute "qtask"  as an instance of "WhatToEnrichQueryTask" class
            self.qtask = WhatToEnrichQueryTask("Get Property Enrichment Candidates (" + self.conceptSearchEdit.text() + ")",
                                               endpoint_url,
                                               self.triplestoreconf[self.tripleStoreEdit.currentIndex() + 1][
                                                   "whattoenrichquery"].replace("%%concept%%", concept).replace("%%area%%","?area"),
                                                   # "What to enrich" calls its attribute conceptSearchEdit and retrieves the text inside through the function "text()"
                                                   self.conceptSearchEdit.text(),
                                                   # What to Enrich gets tripleStoreEdit's currentIndex() to find the appropriate item of a list of prefixes in accordance with the current triple store defined in "tripleStoreEdit"
                                                   self.prefixes[self.tripleStoreEdit.currentIndex()],
                                                   # The two last parameters of the WhatToEnrichQueryTask Constructor are(1) the searchResult attribute of what to enrich and (2) the progress variable
                                                   self.searchResult, progress)
         #QGIS Application first calls its "taskManager" function and then it calls the function addTask of the QgsApplication.taskManager() result
            QgsApplication.taskManager().addTask(self.qtask)

    ##
    #  @brief Returns a chosen concept to the calling dialog.
    #
    #  @param [in] self The object pointer
    #  @param [in] costumURI indicates whether a URI has been entered by the user or if a URI should be selected in the result list widget
    #  @return A URI and possibly its label as a String
    def applyConceptToColumn(self, costumURI=False):
        fieldnames = [field.name() for field in self.layer.fields()]
        if self.searchResult.count() == 0 :
            msgBox = QMessageBox()
            msgBox.setWindowTitle("WARNING for apply button")
            msgBox.setText('You need to first "select a concept", then "select properties for enrichment" and only then click on the apply button.'+
            'If you have done these two steps that means there are no results so you cannot apply enrichement.Try again with other concepts!')
            msgBox.exec()
        else:
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
