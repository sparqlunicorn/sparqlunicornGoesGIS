from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QProgressDialog, QFileDialog,QMessageBox
from qgis.core import QgsApplication, QgsCoordinateReferenceSystem
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtCore import QRegExp
from qgis.PyQt.QtGui import QRegExpValidator, QValidator

from ..util.ui.uiutils import UIUtils
from ..tasks.convertcrstask import ConvertCRSTask
from ..tasks.loadgraphtask import LoadGraphTask
import os.path

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/convertcrsdialog.ui'))

##
#  @brief The main dialog window of the SPARQLUnicorn QGIS Plugin.
class ConvertCRSDialog(QtWidgets.QDialog, FORM_CLASS):
    ## The triple store configuration file
    triplestoreconf = None
    ## Prefix map
    prefixes = None
    ## LoadGraphTask for loading a graph from a file or uri
    qtask = None

    def __init__(self, triplestoreconf={}, maindlg=None, parent=None,title="Convert CRS"):
        """Constructor."""
        super(ConvertCRSDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(title)
        self.setWindowIcon(UIUtils.rdffileicon)
        self.triplestoreconf = triplestoreconf
        self.dlg = parent
        self.maindlg = maindlg
        self.projectionSelect.setCrs(QgsCoordinateReferenceSystem('EPSG:4326'))
        urlregex = QRegExp("http[s]?://(?:[a-zA-Z#]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        urlvalidator = QRegExpValidator(urlregex, self)
        self.startConversionButton.clicked.connect(self.startConversion)
        self.cancelButton.clicked.connect(self.close)
        self.convertAllCheckBox.stateChanged.connect(self.toggleComboBoxes)
        # self.loadFromURIButton.clicked.connect(self.loadURI)

    def toggleComboBoxes(self):
        if self.convertFromComboBox.isEnabled():
            self.convertFromComboBox.setDisabled(True)
        else:
            self.convertFromComboBox.setDisabled(False)
        if self.convertToComboBox.isEnabled():
            self.convertToComboBox.setDisabled(True)
        else:
            self.convertToComboBox.setDisabled(False)

    def loadFile(self):
        dialog = QFileDialog(self.dlg)
        dialog.setFileMode(QFileDialog.AnyFile)
        self.justloadingfromfile = True
        if dialog.exec_():
            fileNames = dialog.selectedFiles()
            filepath = fileNames[0].split(".")
            self.chosenFileLabel.setText(fileNames[0])

    def startConversion(self):
        fileNames = self.convertCRSFileWidget.splitFilePaths(self.convertCRSFileWidget.filePath())
        progress = QProgressDialog("Loading Graph and converting CRS of graph: " + str(fileNames), "Abort",
                                   0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle("Modifying graph")
        progress.setCancelButton(None)
        if self.convertCRSFileWidget.filePath()!="":
            if self.convertAllCheckBox.checkState():
                self.qtask = ConvertCRSTask("Converting CRS of Graph(s): " + str(fileNames),
                                            fileNames[0], self.projectionSelect.crs(), self.convertFromComboBox, self.convertToComboBox, self,
                                            progress)
            else:
                self.qtask = ConvertCRSTask("Converting CRS of Graph(s): " + str(fileNames),
                                        fileNames[0], self.projectionSelect.crs(), None, None, self, progress)
            QgsApplication.taskManager().addTask(self.qtask)
        else:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("No file selected!")
            msgBox.setText("No file was selected for conversion!")
            msgBox.exec()

    def loadURI(self):
        if self.graphURIEdit.text() != "":
            progress = QProgressDialog("Loading Graph from " + self.graphURIEdit.text(), "Abort", 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setWindowTitle("Load Graph")
            progress.setCancelButton(None)
            self.qtask = LoadGraphTask("Loading Graph: " + self.graphURIEdit.text(), self.graphURIEdit.text(), self,
                                       self.dlg, self.maindlg, self.triplestoreconf[0]["geoconceptquery"],
                                       self.triplestoreconf, progress)
            QgsApplication.taskManager().addTask(self.qtask)
