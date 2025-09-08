from qgis.PyQt.QtWidgets import QDialog, QMessageBox, QSizePolicy, QProgressDialog
from qgis.PyQt.QtCore import Qt
from qgis.PyQt import uic
from qgis.core import Qgis, QgsMessageLog
from qgis._gui import QgsFileWidget
from qgis.core import QgsApplication
from qgis.PyQt.QtGui import QRegularExpressionValidator

from ...tasks.query.util.triplestorerepotask import TripleStoreRepositoryTask
from ...util.ui.uiutils import UIUtils
from ...tasks.query.util.detecttriplestoretask import DetectTripleStoreTask
from ...tasks.processing.loadgraphtask import LoadGraphTask
import os.path

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/triplestorequickadddialog.ui'))

class TripleStoreQuickAddDialog(QDialog, FORM_CLASS):
    triplestoreconf = ""

    def __init__(self, triplestoreconf, prefixes, prefixstore, comboBox, maindlg=None,dlg=None,title="Configure Own RDF Resource"):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.setWindowTitle(title)
        self.triplestoreconf = triplestoreconf
        self.maindlg=maindlg
        self.dlg=dlg
        self.prefixstore = prefixstore
        self.comboBox = comboBox
        self.prefixes = prefixes
        self.recursiveResolvingCBox.hide()
        self.setWindowIcon(UIUtils.linkeddataicon)
        self.rdfResourceComboBox.removeItem(3)
        self.tripleStoreEdit.show()
        self.tripleStoreEdit.setValidator(QRegularExpressionValidator(UIUtils.urlregex, self))
        self.tripleStoreEdit.textChanged.connect(lambda: UIUtils.check_state(self.tripleStoreEdit))
        self.tripleStoreEdit.textChanged.emit(self.tripleStoreEdit.text())
        self.detectConfiguration.clicked.connect(self.detectTripleStoreConfiguration)
        self.useAuthenticationCheckBox.stateChanged.connect(self.enableAuthentication)
        self.rdfResourceComboBox.currentIndexChanged.connect(self.switchStackedWidget)
        self.loadFromRepository()

    def switchStackedWidget(self):
        curindex=self.rdfResourceComboBox.currentIndex()-1
        if curindex==-1:
            curindex=0
        self.stackedWidget.setCurrentIndex(curindex)

    def loadFromRepository(self):
        self.qtask = TripleStoreRepositoryTask("Loading Repository contents: " + self.tripleStoreEdit.text(),self.resourceSelectorCBox)
        QgsApplication.taskManager().addTask(self.qtask)


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
        triplestore=True
        uri=False
        file=False
        if self.rdfResourceComboBox.currentIndex() == 0 and (self.tripleStoreEdit.text().endswith(".ttl") or self.tripleStoreEdit.text().endswith(".owl")):
            triplestore=False
            uri=True
            self.rdfResourceComboBox.setCurrentIndex(1)
        elif self.rdfResourceComboBox.currentIndex()==1:
            triplestore=False
            uri=True
        elif self.rdfResourceComboBox.currentIndex()==2:
            triplestore = False
            uri = False
            file=True
        if triplestore:
            progress = QProgressDialog(f"Detecting configuration for triple store {self.tripleStoreEdit.text()}...\nIf autodetection takes very long (>1 minute), try to disable namespace detection...\nCurrent Task: Initial Detection",
                                       "Abort", 0, 0, self)
            progress.setWindowTitle("Triple Store Autoconfiguration")
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.show()
            self.qtask = DetectTripleStoreTask(
                f"Detecting configuration for triple store {self.tripleStoreEdit.text()}...", self.triplestoreconf,
                self.tripleStoreEdit.text(), self.tripleStoreNameEdit.text(), self.credentialUserName.text(),
                self.credentialPassword.text(),self.authenticationComboBox.currentText(), False, True, self.prefixes, self.prefixstore,
                self.comboBox, self.permanentAddCBox.isChecked(),self.detectNamespacesCBox.isChecked(), self,self.maindlg, progress)
            QgsApplication.taskManager().addTask(self.qtask)
        elif uri:
            if self.tripleStoreEdit.text() != "":
                progress = QProgressDialog(f"Loading Graph from {self.tripleStoreEdit.text()}", "Abort", 0, 0, self)
                progress.setWindowTitle("Loading Graph")
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.setCancelButton(None)
                self.qtask = LoadGraphTask("Loading Graph: " + self.tripleStoreEdit.text(), self.tripleStoreNameEdit.text(),
                                           self.tripleStoreEdit.text(), self,
                                           self.dlg, self.maindlg, self.triplestoreconf[0]["geoconceptquery"],
                                           self.triplestoreconf, progress, True)
                QgsApplication.taskManager().addTask(self.qtask)
        elif file:
            QgsMessageLog.logMessage("Add Graph File", "TripleStoreQuickAdd", Qgis.Info)
            QgsMessageLog.logMessage(str(self.chooseFileWidget.filePath()), "TripleStoreQuickAdd", Qgis.Info)
            fileNames=self.chooseFileWidget.splitFilePaths(self.chooseFileWidget.filePath())
            QgsMessageLog.logMessage(str(fileNames), "TripleStoreQuickAdd", Qgis.Info)
            if len(fileNames)>0:
                self.justloadingfromfile = True
                progress = QProgressDialog("Loading Graph: " + fileNames[0], "Abort", 0, 0, self)
                progress.setWindowTitle("Loading Graph")
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.setWindowIcon(UIUtils.sparqlunicornicon)
                progress.setCancelButton(None)
                self.qtask = LoadGraphTask("Loading Graph: " + fileNames[0], self.rdfResourceNameEdit.text(), fileNames, self,
                                           self.dlg, self.maindlg,
                                           self.triplestoreconf[0]["geoconceptquery"], self.triplestoreconf, progress,
                                           True)
                QgsApplication.taskManager().addTask(self.qtask)

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
            self.tripleStoreChooser.addItem(self.tripleStoreNameEdit.text()+" [Endpoint]")
            self.triplestoreconf.append({})
            self.triplestoreconf[index]["querytemplate"] = []
            self.triplestoreconf[index]["querytemplate"].append({})
            self.triplestoreconf[index]["querytemplate"][0]["label"] = "Example Query"
            self.triplestoreconf[index]["querytemplate"][0]["query"] = self.exampleQuery.toPlainText()
        else:
            index = self.tripleStoreChooser.currentIndex()
        self.triplestoreconf[index] = {}
        self.triplestoreconf[index]["resource"] = {"type":"endpoint","url":self.tripleStoreEdit.text()}
        self.triplestoreconf[index]["name"] = self.tripleStoreNameEdit.text()
        self.triplestoreconf[index]["mandatoryvariables"] = []
        self.triplestoreconf[index]["mandatoryvariables"].append(self.queryVarEdit.text())
        self.triplestoreconf[index]["mandatoryvariables"].append(self.queryVarItemEdit.text())
        self.triplestoreconf[index]["prefixes"] = curprefixes
        self.triplestoreconf[index]["crs"] = self.epsgEdit.text()
        self.triplestoreconf[index]["active"] = self.activeCheckBox.isChecked()
        self.addTripleStore = False

