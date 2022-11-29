from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QProgressDialog, QFileDialog,QMessageBox
from qgis.core import QgsApplication, QgsCoordinateReferenceSystem
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtCore import QRegExp
from qgis.PyQt.QtGui import QRegExpValidator

from ...util.ui.uiutils import UIUtils
from ...tasks.processing.convertcrstask import ConvertCRSTask
from ...tasks.processing.loadgraphtask import LoadGraphTask
import os.path

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/triplestorerepodialog.ui'))

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