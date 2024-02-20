from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import QgsProject,QgsMapLayerProxyModel, Qgis
from qgis.PyQt.QtWidgets import QProgressDialog, QFileDialog,QMessageBox
from qgis.core import QgsApplication
from qgis.core import Qgis,QgsTask, QgsMessageLog
from qgis.PyQt.QtCore import Qt

from ...util.export.data.exporter.exporterutils import ExporterUtils
from ...util.ui.uiutils import UIUtils
from ...tasks.processing.convertlayertask import ConvertLayerTask
import os.path

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/convertlayerdialog.ui'))

##
#  @brief The main dialog window of the SPARQLUnicorn QGIS Plugin.
class ConvertLayerDialog(QtWidgets.QDialog, FORM_CLASS):
    ## The triple store configuration file
    triplestoreconf = None
    ## Prefix map
    prefixes = None
    ## LoadGraphTask for loading a graph from a file or uri
    qtask = None

    def __init__(self, triplestoreconf={},prefixes=[],maindlg=None, parent=None,title="Convert Layer to Graph"):
        """Constructor."""
        super(ConvertLayerDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(UIUtils.featurecollectionToRDFicon)
        self.triplestoreconf = triplestoreconf
        self.setWindowTitle(title)
        self.dlg = parent
        self.prefixes=prefixes
        self.maindlg = maindlg
        self.loadedLayers.setFilters(
            QgsMapLayerProxyModel.PointLayer | QgsMapLayerProxyModel.LineLayer | QgsMapLayerProxyModel.PolygonLayer | QgsMapLayerProxyModel.NoGeometry)
        self.convertToRDFButton.clicked.connect(self.startConversion)
        self.vocabularyCBox.currentIndexChanged.connect(self.vocabularyCBoxIndexChanged)

    def vocabularyCBoxIndexChanged(self):
        if "GeoSPARQL" not in self.vocabularyCBox.currentText():
            self.literalTypeCBox.setEnabled(False)
        else:
            self.literalTypeCBox.setEnabled(True)


    def startConversion(self):
        layer = self.loadedLayers.currentLayer()
        filename = QFileDialog.getSaveFileName(
            self, "Select output file ", "", ExporterUtils.getExporterString())
        QgsMessageLog.logMessage('Started task "{}"'.format(
            filename),
            "Convert Layer Dialog", Qgis.Info)
        if filename == "":
            return
        progress = QProgressDialog("Loading Layer and converting it to : " + str(filename), "Abort", 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle("Converting layer")
        progress.setCancelButton(None)
        self.qtask = ConvertLayerTask("Converting Layer to graph: " + str(filename),
                                      layer, filename, self.vocabularyCBox.currentText(),
                                      "WKT",self.prefixes,
                                      self,
                                      progress)
        QgsApplication.taskManager().addTask(self.qtask)


