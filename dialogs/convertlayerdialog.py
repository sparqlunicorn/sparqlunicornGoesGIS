from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import  QFileDialog
from qgis.core import QgsProject
from qgis.core import Qgis
from ..util.layerutils import LayerUtils
from ..tasks.loadgraphtask import LoadGraphTask
import os.path
from qgis.utils import iface
from rdflib import Graph

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/convertlayerdialog.ui'))


##
#  @brief The main dialog window of the SPARQLUnicorn QGIS Plugin.
class ConvertLayerDialog(QtWidgets.QDialog, FORM_CLASS):
    ## The triple store configuration file
    triplestoreconf = None
    ## Prefix map
    prefixes = None
    ## LoadGraphTask for loading a graph from a file or uri
    qtask = None

    def __init__(self, triplestoreconf={},prefixes=[], maindlg=None, parent=None):
        """Constructor."""
        super(ConvertLayerDialog, self).__init__(parent)
        self.setupUi(self)
        self.triplestoreconf = triplestoreconf
        self.dlg = parent
        self.prefixes=prefixes
        self.maindlg = maindlg
        layers = QgsProject.instance().layerTreeRoot().children()
        self.loadedLayers.clear()
        for layer in layers:
            ucl = layer.name()
            self.loadedLayers.addItem(ucl)
        self.convertToRDFButton.clicked.connect(self.startConversion)
        self.cancelButton.clicked.connect(self.close)


    def startConversion(self):
        layers = QgsProject.instance().layerTreeRoot().children()
        layer = layers[self.loadedLayers.currentIndex()].layer()
        filename, _filter = QFileDialog.getSaveFileName(
            self, "Select   output file ", "", "Linked Data (*.ttl *.n3 *.nt *.graphml)", )
        if filename == "":
            return
        if filename.endswith("graphml"):
            ttlstring = LayerUtils.layerToGraphML(layer)
        else:
            ttlstring = LayerUtils.layerToTTLString(layer, "".join(self.prefixes[self.loadedLayers.currentIndex()]),
                                                    None,None,None,None,None,None)
        with open(filename, 'w') as output_file:
            output_file.write(ttlstring)
            iface.messageBar().pushMessage("export layer successfully!", "OK", level=Qgis.Success)
        if not filename.endswith("graphml"):
            g = Graph()
            g.parse(data=ttlstring, format="ttl")
            splitted = filename.split(".")
            exportNameSpace = ""
            exportSetClass = ""
            with open(filename, 'w') as output_file:
                output_file.write(g.serialize(format=splitted[len(splitted) - 1]))
                iface.messageBar().pushMessage("export layer successfully!", "OK", level=Qgis.Success)
        self.close()
