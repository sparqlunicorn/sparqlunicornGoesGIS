from qgis.PyQt.QtWidgets import QDialog
import os
from qgis.PyQt import uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/aboutdialog.ui'))

class AboutDialog(QDialog, FORM_CLASS):

    def __init__(self,):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.okButton.clicked.connect(self.close)
        self.show()