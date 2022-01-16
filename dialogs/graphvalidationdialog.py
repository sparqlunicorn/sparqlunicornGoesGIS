from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QProgressDialog, QFileDialog
from qgis.core import QgsApplication
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtCore import QRegExp
from qgis.PyQt.QtGui import QRegExpValidator, QValidator
from ..tasks.graphvalidationtask import GraphValidationTask
from ..tasks.loadgraphtask import LoadGraphTask
import os.path

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/graphvalidationdialog.ui'))

##
#  @brief The main dialog window of the SPARQLUnicorn QGIS Plugin.
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
        self.triplestoreconf = triplestoreconf
        self.dlg = parent
        self.maindlg = maindlg
        urlregex = QRegExp("http[s]?://(?:[a-zA-Z#]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        urlvalidator = QRegExpValidator(urlregex, self)
        self.loadDataFileButton.clicked.connect(self.loadFile)
        self.startValidationButton.clicked.connect(self.startValidation)
        self.cancelButton.clicked.connect(self.close)

    def loadFile(self):
        dialog = QFileDialog(self.dlg)
        dialog.setFileMode(QFileDialog.AnyFile)
        self.justloadingfromfile = True
        if dialog.exec_():
            fileNames = dialog.selectedFiles()
            filepath = fileNames[0].split(".")
            self.chosenDataFile.setText(fileNames[0])

    def startValidation(self):
        progress = QProgressDialog("Validating graph: " + self.chosenDataFile.text(), "Abort",
                                   0, 0, self)
        progress.setWindowTitle("Graph Validation")
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)
        #if self.convertAllCheckBox.checkState():
        #    self.qtask = GraphValidationTask("Validating graph: " + self.chosenDataFile.text(),
        #                                self.chosenDataFile.text(), self.chosenValidatorFile.text(),self.triplestoreconf,progress)
        #else:
        self.qtask = GraphValidationTask("Validating graph: " + self.chosenDataFile.text(),
                                        self.chosenDataFile.text(), self.chosenValidatorFile.currentText(),self.triplestoreconf,progress,self)
        QgsApplication.taskManager().addTask(self.qtask)

    def loadURI(self):
        if self.graphURIEdit.text() != "":
            progress = QProgressDialog("Loading Graph from " + self.graphURIEdit.text(), "Abort", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setCancelButton(None)
            self.qtask = LoadGraphTask("Loading Graph: " + self.graphURIEdit.text(), self.graphURIEdit.text(), self,
                                       self.dlg, self.maindlg, self.triplestoreconf[0]["geoconceptquery"],
                                       self.triplestoreconf, progress)
            QgsApplication.taskManager().addTask(self.qtask)
