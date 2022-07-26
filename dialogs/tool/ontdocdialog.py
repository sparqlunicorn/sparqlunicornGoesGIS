from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QProgressDialog, QFileDialog,QLineEdit,QMessageBox
from qgis.core import QgsApplication
from qgis.PyQt.QtCore import Qt
from ...tasks.processing.ontdoctask import OntDocTask

from ...util.ui.uiutils import UIUtils
import os.path

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/ontdocdialog.ui'))

##
#  Class representing the graph validation dialog.
class OntDocDialog(QtWidgets.QDialog, FORM_CLASS):
    ## The triple store configuration file
    triplestoreconf = None
    ## Prefix map
    prefixes = None
    ## LoadGraphTask for loading a graph from a file or uri
    qtask = None

    def __init__(self, triplestoreconf={}, maindlg=None, parent=None,title="Ontology Documentation"):
        """Constructor."""
        super(OntDocDialog, self).__init__(parent)
        self.setupUi(self)
        self.createDocumentationButton.clicked.connect(self.createDocumentation)


    def createDocumentation(self):
        progress = QProgressDialog("Creating ontology documentation... ", "Abort",
                                   0, 0, self)
        progress.setWindowTitle("Ontology Documentation")
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowIcon(UIUtils.sparqlunicornicon)
        progress.setCancelButton(None)

        self.qtask = OntDocTask("Creating ontology documentation... ",
                                         "", self.chosenValidatorFile.currentText(),
                                         self.triplestoreconf, progress, self)
        QgsApplication.taskManager().addTask(self.qtask)