from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtWidgets import QStyle
from qgis.PyQt.QtGui import QIcon
import os
from qgis.PyQt import uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/layerquerydialog.ui'))

class LayerQueryDialog(QDialog, FORM_CLASS):

    def __init__(self,):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxInformation'))))
        self.chooseField.setLayer(self.chooseLayer.currentLayer())
        self.show()