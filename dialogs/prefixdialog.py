import os
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtGui import QRegExpValidator
from qgis.PyQt.QtWidgets import QListWidgetItem

from ..util.ui.uiutils import UIUtils

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/prefixdialog.ui'))

# Class representing a search dialog which may be used to search for concepts or properties.
class PrefixDialog(QDialog, FORM_CLASS):

    def __init__(self,prefixList,prefix=None,uri=None):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.prefixList=prefixList
        self.prefixEdit.setValidator(QRegExpValidator(UIUtils.prefixregex, self))
        self.prefixEdit.textChanged.connect(lambda: UIUtils.check_state(self.prefixEdit))
        self.uriEdit.setValidator(QRegExpValidator(UIUtils.urlregex, self))
        self.uriEdit.textChanged.connect(lambda: UIUtils.check_state(self.uriEdit))
        self.addOrEdit=True
        if prefix!=None:
            self.addOrEdit=False
            self.prefixEdit.setText(prefix)
        if uri!=None:
            self.addOrEdit=False
            self.uriEdit.setText(uri)
        self.cancelButton.clicked.connect(self.close)
        self.saveButton.clicked.connect(self.savePrefix)

    def savePrefix(self):
        if self.addOrEdit:
            item=QListWidgetItem()
            item.setText(self.prefixEdit.text() + ": <" + str(self.uriEdit.text()) + ">")
            item.setData(256, self.uriEdit.text())
            item.setData(257, self.prefixEdit.text())
            self.prefixList.addItem(item)
            self.prefixList.sortItems()
        else:
            for item in self.prefixList.selectedItems():
                item.setText(self.prefixEdit.text()+": <"+str(self.uriEdit.text())+">")
                item.setData(256,self.uriEdit.text())
                item.setData(257, self.prefixEdit.text())
        self.close()
