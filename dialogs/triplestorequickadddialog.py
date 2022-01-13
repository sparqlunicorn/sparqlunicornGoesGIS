from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QListWidgetItem, QSizePolicy
from qgis.PyQt.QtCore import QRegExp, Qt
from qgis.PyQt import uic
from qgis._gui import QgsFileWidget
from qgis.core import QgsApplication
from qgis.PyQt.QtWidgets import QProgressDialog, QFileDialog
from qgis.PyQt.QtGui import QRegExpValidator, QValidator
from ..tasks.detecttriplestoretask import DetectTripleStoreTask
from ..tasks.loadgraphtask import LoadGraphTask
import os.path

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/triplestorequickadddialog.ui'))


class TripleStoreQuickAddDialog(QDialog, FORM_CLASS):
    triplestoreconf = ""

    def __init__(self, triplestoreconf, prefixes, prefixstore, comboBox, maindlg=None,dlg=None):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.triplestoreconf = triplestoreconf
        self.maindlg=maindlg
        self.dlg=dlg
        self.prefixstore = prefixstore
        self.comboBox = comboBox
        self.prefixes = prefixes
        urlregex = QRegExp("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        urlvalidator = QRegExpValidator(urlregex, self)
        self.recursiveResolvingCBox.hide()
        self.chooseFileWidget=QgsFileWidget()
        self.gridLayout.addWidget(self.chooseFileWidget,4,1,Qt.AlignLeft)
        self.chooseFileWidget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.chooseFileWidget.hide()
        self.tripleStoreEdit.show()
        self.tripleStoreEdit.setValidator(urlvalidator)
        self.tripleStoreEdit.textChanged.connect(self.check_state1)
        self.tripleStoreEdit.textChanged.emit(self.tripleStoreEdit.text())
        self.tripleStoreCloseButton.clicked.connect(self.closeTripleStoreDialog)
        self.detectConfiguration.clicked.connect(self.detectTripleStoreConfiguration)
        self.useAuthenticationCheckBox.stateChanged.connect(self.enableAuthentication)
        self.rdfResourceComboBox.currentIndexChanged.connect(self.resboxChangedEvent)

    def resboxChangedEvent(self):
        if "File" in self.rdfResourceComboBox.currentText():
            self.chooseFileWidget.show()
            self.tripleStoreEdit.hide()
        else:
            self.chooseFileWidget.hide()
            self.tripleStoreEdit.show()

    def closeTripleStoreDialog(self):
        self.close()

    def enableAuthentication(self):
        if self.useAuthenticationCheckBox.checkState():
            self.authenticationComboBox.setEnabled(True)
            self.credentialUserName.setEnabled(True)
            self.credentialPassword.setEnabled(True)
        else:
            self.authenticationComboBox.setEnabled(False)
            self.credentialUserName.setEnabled(False)
            self.credentialPassword.setEnabled(False)

    def detectTripleStoreConfiguration(self):
        if "SPARQL Endpoint" in self.rdfResourceComboBox.currentText():
            progress = QProgressDialog("Detecting configuration for triple store " + self.tripleStoreEdit.text() + "...\nIf autodetection takes very long (>1 minute), try to disable namespace detection...\nCurrent Task: Initial Detection",
                                       "Abort", 0, 0, self)
            progress.setWindowTitle("Triple Store Autoconfiguration")
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            self.qtask = DetectTripleStoreTask(
                "Detecting configuration for triple store " + self.tripleStoreEdit.text() + "...", self.triplestoreconf,
                self.tripleStoreEdit.text(), self.tripleStoreNameEdit.text(), self.credentialUserName.text(),
                self.credentialPassword.text(),self.authenticationComboBox.currentText(), False, True, self.prefixes, self.prefixstore,
                None, self.comboBox, self.permanentAddCBox.isChecked(),self.detectNamespacesCBox.isChecked(), self, progress)
            QgsApplication.taskManager().addTask(self.qtask)
        elif "RDF Resource" in self.rdfResourceComboBox.currentText():
            if self.tripleStoreEdit.text() != "":
                progress = QProgressDialog("Loading Graph from " + self.tripleStoreEdit.text(), "Abort", 0, 0, self)
                progress.setWindowTitle("Loading Graph")
                progress.setWindowModality(Qt.WindowModal)
                progress.setCancelButton(None)
                self.qtask = LoadGraphTask("Loading Graph: " + self.tripleStoreEdit.text(), self.tripleStoreNameEdit.text(),
                                           self.tripleStoreEdit.text(), self,
                                           self.dlg, self.maindlg, self.triplestoreconf[0]["geoconceptquery"],
                                           self.triplestoreconf, progress, True)
                QgsApplication.taskManager().addTask(self.qtask)
        elif "RDF File" in self.rdfResourceComboBox.currentText():
            fileNames=self.chooseFileWidget.splitFilePaths(self.chooseFileWidget.filePath())
            if len(fileNames)>0:
                self.justloadingfromfile = True
                progress = QProgressDialog("Loading Graph: " + fileNames[0], "Abort", 0, 0, self)
                progress.setWindowTitle("Loading Graph")
                progress.setWindowModality(Qt.WindowModal)
                progress.setCancelButton(None)
                self.qtask = LoadGraphTask("Loading Graph: " + fileNames[0], self.tripleStoreNameEdit.text(), fileNames, self,
                                           self.dlg, self.maindlg,
                                           self.triplestoreconf[0]["geoconceptquery"], self.triplestoreconf, progress,
                                           True)
                QgsApplication.taskManager().addTask(self.qtask)

    ## 
    #  @brief Adds a new SPARQL endpoint to the triple store registry
    #  
    #  @param [in] self The object pointer
    def addNewSPARQLEndpoint(self):
        self.addTripleStore = True
        self.applyCustomSPARQLEndPoint()

    ## 
    #  @brief Adds a prefix to the list of prefixes in the search dialog window.
    #  
    #  @param [in] self The object pointer
    def addPrefixToList(self):
        item = QListWidgetItem()
        item.setData(0,
                     "PREFIX " + self.tripleStorePrefixNameEdit.text() + ":<" + self.tripleStorePrefixEdit.text() + ">")
        item.setText("PREFIX " + self.tripleStorePrefixNameEdit.text() + ":<" + self.tripleStorePrefixEdit.text() + ">")
        self.prefixList.addItem(item)

    ## 
    #  @brief Removes a prefix from the list of prefixes in the search dialog window.
    #  
    #  @param [in] self The object pointer
    def removePrefixFromList(self):
        item = QListWidgetItem()
        for item in self.prefixList.selectedItems():
            self.prefixList.removeItemWidget(item)

    def applyCustomSPARQLEndPoint(self):
        if not self.testTripleStoreConnection(True):
            return
        if self.tripleStoreNameEdit.text() == "":
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Triple Store Name is missing!")
            msgBox.setText("Please enter a triple store name")
            msgBox.exec()
            return
        # self.endpoints.append(self.tripleStoreEdit.text())
        self.comboBox.addItem(str(self.tripleStoreNameEdit.text())+" [Endpoint]")
        curprefixes = []
        for i in range(self.prefixList.count()):
            curprefixes.append(self.prefixList.item(i).text())
        if self.addTripleStore:
            index = len(self.triplestoreconf)
            self.tripleStoreChooser.addItem(self.tripleStoreNameEdit.text())
            self.triplestoreconf.append({})
            self.triplestoreconf[index]["querytemplate"] = []
            self.triplestoreconf[index]["querytemplate"].append({})
            self.triplestoreconf[index]["querytemplate"][0]["label"] = "Example Query"
            self.triplestoreconf[index]["querytemplate"][0]["query"] = self.exampleQuery.toPlainText()
        else:
            index = self.tripleStoreChooser.currentIndex()
        self.triplestoreconf[index] = {}
        self.triplestoreconf[index]["endpoint"] = self.tripleStoreEdit.text()
        self.triplestoreconf[index]["name"] = self.tripleStoreNameEdit.text()
        self.triplestoreconf[index]["mandatoryvariables"] = []
        self.triplestoreconf[index]["mandatoryvariables"].append(self.queryVarEdit.text())
        self.triplestoreconf[index]["mandatoryvariables"].append(self.queryVarItemEdit.text())
        self.triplestoreconf[index]["prefixes"] = curprefixes
        self.triplestoreconf[index]["crs"] = self.epsgEdit.text()
        self.triplestoreconf[index]["active"] = self.activeCheckBox.isChecked()
        self.addTripleStore = False

    def check_state1(self):
        self.check_state(self.tripleStoreEdit)

    def check_state2(self):
        self.check_state(self.tripleStorePrefixEdit)

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
