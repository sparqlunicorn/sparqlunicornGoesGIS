
from qgis.PyQt.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QListWidget, QComboBox, QMessageBox, QRadioButton, QListWidgetItem, QTableWidgetItem
from qgis.PyQt.QtCore import QRegExp
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtGui import QRegExpValidator, QValidator
from qgis.PyQt import uic
from qgis.core import QgsApplication
from ..tasks.searchtask import SearchTask
import urllib
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
        self.currentcol = column
        self.currentrow = row
        self.table = table
        self.prefixes = prefixes
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
            if not "File" == triplestore["name"]:
                self.tripleStoreEdit.addItem(triplestore["name"])
        if addVocab != None:
            for cov in addVocab:
                self.tripleStoreEdit.addItem(addVocab[cov]["label"])
        self.tripleStoreEdit.setCurrentIndex(2)
        #self.tripleStoreEdit.setEnabled(False)
        self.searchButton.clicked.connect(self.getClassesFromLabel)
        urlregex = QRegExp("http[s]?://(?:[a-zA-Z#]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        urlvalidator = QRegExpValidator(urlregex, self)
        self.costumproperty.setValidator(urlvalidator)
        self.costumproperty.textChanged.connect(self.check_state3)
        self.costumproperty.textChanged.emit(self.costumproperty.text())
        self.costumpropertyButton.clicked.connect(self.applyConceptToColumn2)
        self.applyButton.clicked.connect(self.applyConceptToColumn)
        s = QSettings()  # getting proxy from qgis options settings
        self.proxyEnabled = s.value("proxy/proxyEnabled")
        self.proxyType = s.value("proxy/proxyType")
        self.proxyHost = s.value("proxy/proxyHost")
        self.proxyPort = s.value("proxy/proxyPort")
        self.proxyUser = s.value("proxy/proxyUser")
        self.proxyPassword = s.value("proxy/proxyPassword")
        if self.proxyHost!=None and self.proxyHost!="" and self.proxyPort!=None and self.proxyPort!="":
            QgsMessageLog.logMessage('Proxy? '+str(self.proxyHost), MESSAGE_CATEGORY, Qgis.Info)
            proxy = urllib.request.ProxyHandler({'http': self.proxyHost})
            opener = urllib.request.build_opener(proxy)
            urllib.request.install_opener(opener)

    def check_state3(self):
        self.check_state(self.costumproperty)

    # Checks the state of an input field in order to highlight it with an appropriate color.
    #  @param self The object pointer.
    #  @param sender The sending object containing the validator
    def check_state(self, sender):
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QValidator.Acceptable:
            color = '#c4df9b'  # green
        elif state == QValidator.Intermediate:
            color = '#fff79a'  # yellow
        else:
            color = '#f6989d'  # red
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)

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
        language = "en"
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
                item.setData(1, val)
                item.setText(key)
                self.searchResult.addItem(item)
        else:
            if self.findProperty.isChecked():
                if "propertyfromlabelquery" in self.triplestoreconf[self.tripleStoreEdit.currentIndex() + 1]:
                    query = self.triplestoreconf[self.tripleStoreEdit.currentIndex() + 1]["propertyfromlabelquery"].replace("%%label%%", label)
            else:
                if "classfromlabelquery" in self.triplestoreconf[self.tripleStoreEdit.currentIndex() + 1]:
                    query = self.triplestoreconf[self.tripleStoreEdit.currentIndex() + 1]["classfromlabelquery"].replace("%%label%%", label)
            if query == "":
                msgBox = QMessageBox()
                msgBox.setText("No search query specified for this triplestore")
                msgBox.exec()
                return
            self.qtask=SearchTask("Searching classes/properties for "+label+" in "+self.triplestoreconf[self.tripleStoreEdit.currentIndex() + 1]["endpoint"],
                            self.triplestoreconf[self.tripleStoreEdit.currentIndex() + 1]["endpoint"],
               query,self.triplestoreconf,self.findProperty,self.tripleStoreEdit,self.searchResult,self.prefixes,label,language,None)
            QgsApplication.taskManager().addTask(self.qtask)
        return viewlist

    def applyConceptToColumn2(self):
        self.applyConceptToColumn(True)

    # Applies the search result to a GUI element for which the search dialog was called.
    #  @param self The object pointer.
    #  @param costumURI indicates if the the search result is a manually entered URI
    def applyConceptToColumn(self, costumURI=False):
        print("test")
        if costumURI:
            if self.costumproperty.text() == "":
                return
            toinsert = self.costumproperty.text()
        else:
            if self.searchResult.count() == 0:
                return
            toinsert = str(self.searchResult.currentItem().data(1))
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
            item.setData(1, toinsert)
            if self.interlinkOrEnrich:
                self.table.setItem(self.currentrow, self.currentcol, item)
            else:
                item2 = QTableWidgetItem()
                item2.setText(self.tripleStoreEdit.currentText())
                item2.setData(0, self.triplestoreconf[self.tripleStoreEdit.currentIndex() + 1]["endpoint"])
                self.table.setItem(self.currentrow, self.currentcol, item)
                self.table.setItem(self.currentrow, (self.currentcol + 1), item2)
        self.close()
