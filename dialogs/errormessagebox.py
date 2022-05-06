
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt import uic
import os

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/errormessageboxdialog.ui'))

class ErrorMessageBox(QDialog, FORM_CLASS):

    def __init__(self, title,message, parent=None):
        super(QDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(title)
        self.errorLabel.setText(message)
        self.confirmButton.clicked.connect(self.close)

    def setText(self,text):
        self.errorLabel.setText(text)

    def setTitle(self,text):
        self.errorLabel.setWindowTitle(text)

    def setIcon(self,icon):
        self.errorLabel.setIcon(icon)

