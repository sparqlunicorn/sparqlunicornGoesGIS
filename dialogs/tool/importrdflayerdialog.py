from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QProgressDialog, QFileDialog,QMessageBox
from qgis.core import QgsApplication, QgsCoordinateReferenceSystem
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtCore import QRegExp
from qgis.PyQt.QtGui import QRegExpValidator
from ...tasks.processing.extractnamespacetask import ExtractNamespaceTask

from ...util.ui.uiutils import UIUtils
from ...tasks.processing.convertcrstask import ConvertCRSTask
from ...tasks.processing.loadgraphtask import LoadGraphTask
import os.path

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/importrdflayer.ui'))

##
#  @brief The main dialog window of the SPARQLUnicorn QGIS Plugin.
class ImportRDFLayerDialog(QtWidgets.QDialog, FORM_CLASS):
    ## The triple store configuration file
    triplestoreconf = None
    ## Prefix map
    prefixes = None
    ## LoadGraphTask for loading a graph from a file or uri
    qtask = None

    def __init__(self, triplestoreconf={}, maindlg=None, parent=None, title="Import RDF Layer"):
        """Constructor."""
        super(ImportRDFLayerDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(title)
        self.setWindowIcon(UIUtils.rdffileicon)
        self.triplestoreconf = triplestoreconf
        self.dlg = parent
        self.maindlg = maindlg
        self.inputRDFFileWidget.fileChanged.connect(self.extractClasses)


    def extractClasses(self,filename):
        self.tsk=ExtractNamespaceTask("Extracting namespaces from "+str(filename),filename,None,self.layerSelectBox,self.prefixes,None)
        QgsApplication.taskManager().addTask(self.tsk)


    def
