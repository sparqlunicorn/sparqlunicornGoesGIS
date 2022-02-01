
from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QListWidgetItem, QTableWidgetItem, QMenu, QAction,QApplication
from qgis.PyQt import uic
from qgis.core import (
    QgsApplication, QgsMessageLog
)
from qgis.PyQt.QtGui import QRegExpValidator,QDesktopServices

from .dataschemadialog import DataSchemaDialog
from .menu.conceptcontextmenu import ConceptContextMenu
from ..util.sparqlutils import SPARQLUtils
from ..tasks.searchtask import SearchTask
from ..util.ui.uiutils import UIUtils
import os.path


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/searchdialog.ui'))

# Class representing a search dialog which may be used to search for concepts or properties.
class SearchDialog(QDialog, FORM_CLASS):

    currentrow = ""

    triplestoreconf = ""

    interlinkOrEnrich = False

    table = False

    ##
    #  @brief Initializes the search dialog
    #
    #  @param self The object pointer
    #  @param column The column of the GUI widget which called this dialog, if any
    #  @param row The row of the GUI widget which called this dialog, if any
    #  @param triplestoreconf The triple store configuration of the plugin
    #  @param prefixes A list of prefixes known to the plugin
    #  @param interlinkOrEnrich indicates whether this dialog was called from an enrichment or interlinking dialog
    #  @param table The GUI element ot return the result to
    #  @param propOrClass indicates whether a class or a property can be searched
    #  @param bothOptions indicates whether both a class or property may be searched
    #  @param currentprefixes Description for currentprefixes
    #  @param addVocab Description for addVocab
    #  @return Return description
    #
    #  @details More details
    #
    def __init__(self, column, row, triplestoreconf, prefixes, interlinkOrEnrich, table, propOrClass=False, bothOptions=False, currentprefixes=None, addVocab=None):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(UIUtils.searchclassicon)
        self.currentcol = column
        self.currentrow = row
        self.table = table
        self.prefixes = prefixes
        self.currentItem=None
        self.currentprefixes = currentprefixes
        self.bothOptions = bothOptions
        self.triplestoreconf = triplestoreconf
        self.interlinkOrEnrich = interlinkOrEnrich
        self.addVocab = addVocab
        if column != 4:
            self.findConcept.setChecked(True)
        if column == 4 or (not interlinkOrEnrich and column != 4) or (not interlinkOrEnrich and propOrClass):
            self.findProperty.setChecked(True)
        if not bothOptions:
            self.findProperty.setEnabled(False)
            self.findConcept.setEnabled(False)
        for triplestore in self.triplestoreconf:
            self.tripleStoreEdit.addItem(triplestore["name"])
        if addVocab != None:
            for cov in addVocab:
                self.tripleStoreEdit.addItem(addVocab[cov]["label"])
        self.searchButton.clicked.connect(self.getClassesFromLabel)
        self.searchResult.customContextMenuRequested.connect(self.onContext)
        self.searchResult.itemDoubleClicked.connect(UIUtils.openListURL)
        self.costumproperty.setValidator(QRegExpValidator(UIUtils.urlregex, self))
        self.costumproperty.textChanged.connect(lambda: UIUtils.check_state(self.costumproperty))
        self.costumproperty.textChanged.emit(self.costumproperty.text())
        self.costumpropertyButton.clicked.connect(lambda: self.applyConceptToColumn(True))
        self.applyButton.clicked.connect(self.applyConceptToColumn)

    def onContext(self,position):
        self.currentItem = self.searchResult.itemAt(position)
        menu = QMenu("Menu", self)
        actionclip = QAction("Copy IRI to clipboard")
        menu.addAction(actionclip)
        actionclip.triggered.connect(lambda: ConceptContextMenu.copyClipBoard(self.currentItem))
        action = QAction("Open in Webbrowser")
        menu.addAction(action)
        action.triggered.connect(lambda: UIUtils.openListURL(self.currentItem))
        actiondataschema = QAction("Query data schema")
        menu.addAction(actiondataschema)
        actiondataschema.triggered.connect(lambda: DataSchemaDialog(
            self.currentItem.data(256),
            SPARQLUtils.classnode,
            self.currentItem.text(),
            self.triplestoreconf[self.tripleStoreEdit.currentIndex()]["resource"],
            self.triplestoreconf[self.tripleStoreEdit.currentIndex()], self.prefixes,
            "Data Schema View for " + SPARQLUtils.labelFromURI(str(self.currentItem.data(
                256)),self.triplestoreconf[self.tripleStoreEdit.currentIndex()]["prefixesrev"] if "prefixesrev" in self.triplestoreconf[self.tripleStoreEdit.currentIndex()] else {})
        ).exec_())
        menu.exec(self.searchResult.viewport().mapToGlobal(position))

    ##
    #  @brief Returns classes for a given label from a triple store.
    #
    #  @param self The object pointer
    #  @param comboBox A comboBox indicating the triple store to be used.
    #  @return A list returning concept candidates.
    def getClassesFromLabel(self, comboBox):
        viewlist = []
        resultlist = []
        label = self.conceptSearchEdit.text()
        if label == "":
            return
        language = self.languageCBox.currentText()
        results = {}
        self.searchResult.clear()
        query = ""
        position = self.tripleStoreEdit.currentIndex()
        if self.tripleStoreEdit.currentIndex() > len(self.triplestoreconf):
            if self.findProperty.isChecked():
                self.addVocab[self.addVocab.keys()[position - len(self.triplestoreconf)]]["source"]["properties"]
                viewlist = {k: v for k, v in d.iteritems() if label in k}
            else:
                self.addVocab[self.addVocab.keys()[position - len(self.triplestoreconf)]]["source"]["classes"]
                viewlist = {k: v for k, v in d.iteritems() if label in k}
            for res in viewlist:
                item = QListWidgetItem()
                item.setData(256, val)
                item.setText(key)
                self.searchResult.addItem(item)
        else:
            self.qtask=SearchTask("Searching classes/properties for "+str(label)+" in "+str(self.triplestoreconf[self.tripleStoreEdit.currentIndex()]["resource"]["url"]),
                            self.triplestoreconf[self.tripleStoreEdit.currentIndex()]["resource"],
               query,self.triplestoreconf,self.findProperty,self.tripleStoreEdit,self.searchResult,self.prefixes,label,language,None)
            QgsApplication.taskManager().addTask(self.qtask)
        return viewlist



    # Applies the search result to a GUI element for which the search dialog was called.
    #  @param self The object pointer.
    #  @param costumURI indicates if the the search result is a manually entered URI
    def applyConceptToColumn(self, costumURI=False):
        if costumURI:
            if self.costumproperty.text() == "":
                return
            toinsert = self.costumproperty.text()
        else:
            if self.searchResult.count() == 0:
                return
            toinsert = str(self.searchResult.currentItem().data(256))
        if self.bothOptions == True:
            haschanged = False
            if self.currentprefixes != None:
                for prefix in self.currentprefixes:
                    if self.currentprefixes[prefix] in toinsert:
                        toinsert = toinsert.replace(self.currentprefixes[prefix], prefix + ":")
                        haschanged = True
            if haschanged:
                self.table.insertPlainText(toinsert)
            else:
                self.table.insertPlainText("<" + toinsert + ">")
        elif self.interlinkOrEnrich == -1:
            self.table.setText(str(toinsert))
        else:
            if costumURI:
                item = QTableWidgetItem(toinsert)
                item.setText(toinsert)
            else:
                item = QTableWidgetItem(self.searchResult.currentItem().text())
                item.setText(self.searchResult.currentItem().text())
            item.setData(256, toinsert)
            if self.interlinkOrEnrich:
                self.table.setItem(self.currentrow, self.currentcol, item)
            else:
                item2 = QTableWidgetItem()
                item2.setText(self.tripleStoreEdit.currentText())
                item2.setData(257, self.triplestoreconf[self.tripleStoreEdit.currentIndex()]["resource"])
                self.table.setItem(self.currentrow, self.currentcol, item)
                self.table.setItem(self.currentrow, (self.currentcol), item2)
        self.close()
