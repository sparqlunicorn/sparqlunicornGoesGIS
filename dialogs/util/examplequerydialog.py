import os
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/examplequerydialog.ui'))

# Class representing a search dialog which may be used to search for concepts or properties.
class ExampleQueryDialog(QDialog, FORM_CLASS):

    def __init__(self,queryList,queryName=None):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Add Example Query")
        self.queryList=queryList
        self.addOrEdit=True
        if queryName is not None:
            self.addOrEdit=False
            self.setWindowTitle("Edit Example Query Title")
            self.queryNameEdit.setText(queryName)
        self.cancelButton.clicked.connect(self.close)
        self.okButton.clicked.connect(self.saveQuery)

    def saveQuery(self):
        if self.addOrEdit:
            self.queryList.addItem(self.queryNameEdit.text())
            self.queryList.setCurrentIndex(self.queryList.count()-1)
        else:
            self.queryList.setItemText(self.queryList.currentIndex(),self.queryNameEdit.text())
        self.close()
