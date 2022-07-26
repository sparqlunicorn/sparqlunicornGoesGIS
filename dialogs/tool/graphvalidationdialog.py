from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QProgressDialog, QFileDialog,QLineEdit,QMessageBox
from qgis.core import QgsApplication
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QRegExpValidator

from ...util.ui.uiutils import UIUtils
from ...tasks.processing.graphvalidationtask import GraphValidationTask
from ...tasks.processing.loadgraphtask import LoadGraphTask
import os.path

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/graphvalidationdialog.ui'))

##
#  Class representing the graph validation dialog.
class GraphValidationDialog(QtWidgets.QDialog, FORM_CLASS):
    ## The triple store configuration file
    triplestoreconf = None
    ## Prefix map
    prefixes = None
    ## LoadGraphTask for loading a graph from a file or uri
    qtask = None

    def __init__(self, triplestoreconf={}, maindlg=None, parent=None,title="Validate Graph"):
        """Constructor."""
        super(GraphValidationDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(title)
        self.setWindowIcon(UIUtils.validationicon)
        self.triplestoreconf = triplestoreconf
        self.dlg = parent
        self.maindlg = maindlg
        self.validationFileEdit=QLineEdit()
        self.validationFileEdit.setValidator(QRegExpValidator(UIUtils.urlregex, self))
        self.validationFileEdit.textChanged.connect(lambda: UIUtils.check_state(self.validationFileEdit))
        self.validationFileEdit.textChanged.emit(self.validationFileEdit.text())
        self.gridLayout.addWidget(self.validationFileEdit,1,1,1,1)
        self.validationFileEdit.hide()
        self.startValidationButton.clicked.connect(self.startValidation)
        self.dataFileLocationCBox.currentIndexChanged.connect(self.dataLocBoxChangedEvent)
        self.cancelButton.clicked.connect(self.close)

    def dataLocBoxChangedEvent(self):
        if "File" in self.dataFileLocationCBox.currentText():
            self.validationFileWidget.show()
            self.validationFileEdit.hide()
        else:
            self.validationFileWidget.hide()
            self.validationFileEdit.show()

    def loadFile(self):
        dialog = QFileDialog(self.dlg)
        dialog.setFileMode(QFileDialog.AnyFile)
        self.justloadingfromfile = True
        if dialog.exec_():
            fileNames = dialog.selectedFiles()
            filepath = fileNames[0].split(".")
            self.chosenDataFile.setText(fileNames[0])

    def startValidation(self):
        if "RDF File" in self.dataFileLocationCBox.currentText():
            fileNames=self.validationFileWidget.splitFilePaths(self.validationFileWidget.filePath())
            if len(fileNames)>0:
                progress = QProgressDialog("Validating graph: " + str(fileNames), "Abort",
                                           0, 0, self)
                progress.setWindowTitle("Graph Validation")
                progress.setWindowModality(Qt.WindowModal)
                progress.setWindowIcon(UIUtils.sparqlunicornicon)
                progress.setCancelButton(None)
                self.qtask = GraphValidationTask("Validating graph: "+str(fileNames),
                                                 fileNames, self.chosenValidatorFile.currentText(),
                                                 self.triplestoreconf, progress, self)
                QgsApplication.taskManager().addTask(self.qtask)
            else:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("No file selected!")
                msgBox.setText("No data file was selected for validation!")
                msgBox.exec()
        elif "RDF Resource" in self.rdfResourceComboBox.currentText():
            if self.validationFileEdit.text() != "":
                progress = QProgressDialog("Validating graph: " + self.validationFileEdit.text(), "Abort",
                                           0, 0, self)
                progress.setWindowTitle("Graph Validation")
                progress.setWindowModality(Qt.WindowModal)
                progress.setWindowIcon(UIUtils.sparqlunicornicon)
                progress.setCancelButton(None)
                self.qtask = GraphValidationTask("Validating graph: "+str(self.validationFileEdit.text()),
                                                 self.validationFileEdit.text(), self.chosenValidatorFile.currentText(),
                                                 self.triplestoreconf, progress, self)
                QgsApplication.taskManager().addTask(self.qtask)
            else:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("No URL defined!")
                msgBox.setText("No URL was defined for validation!")
                msgBox.exec()

    def loadURI(self):
        if self.graphURIEdit.text() != "":
            progress = QProgressDialog("Loading Graph from " + self.graphURIEdit.text(), "Abort", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setWindowIcon(UIUtils.sparqlunicornicon)
            progress.setCancelButton(None)
            self.qtask = LoadGraphTask("Loading Graph: " + self.graphURIEdit.text(), self.graphURIEdit.text(), self,
                                       self.dlg, self.maindlg, self.triplestoreconf[0]["geoconceptquery"],
                                       self.triplestoreconf, progress)
            QgsApplication.taskManager().addTask(self.qtask)
