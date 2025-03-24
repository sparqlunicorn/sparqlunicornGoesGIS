import os
from qgis.PyQt import uic
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QStyle
from qgis.PyQt.QtWidgets import QDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/preferencesdialog.ui'))

# Class representing a search dialog which may be used to search for concepts or properties.
class PreferencesDialog(QDialog, FORM_CLASS):

    def __init__(self,):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Preferences")
        self.setWindowIcon(QIcon(self.style().standardIcon(getattr(QStyle.StandardPixmap, 'SP_ComputerIcon'))))
        self.cancelButton.clicked.connect(self.close)
        self.show()

