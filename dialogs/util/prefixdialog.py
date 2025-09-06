import os
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QCompleter
from qgis.PyQt.QtGui import QRegularExpressionValidator
from qgis.PyQt.QtWidgets import QListWidgetItem

from ...util.ui.uiutils import UIUtils

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/prefixdialog.ui'))

# Class representing a search dialog which may be used to search for concepts or properties.
class PrefixDialog(QDialog, FORM_CLASS):

    def __init__(self,prefixList,globalPrefixList=None,prefix=None,uri=None):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.prefixList=prefixList
        self.globalPrefixList=globalPrefixList
        self.prefixEdit.setValidator(QRegularExpressionValidator(UIUtils.prefixregex, self))
        self.prefixEdit.textChanged.connect(lambda: self.checkSuggestion())
        if globalPrefixList is not None and "normal" in globalPrefixList:
            self.prefixEdit.setCompleter(QCompleter(globalPrefixList["normal"].keys()))
        self.uriEdit.setValidator(QRegularExpressionValidator(UIUtils.urlregex, self))
        self.uriEdit.textChanged.connect(lambda: UIUtils.check_state(self.uriEdit))
        if globalPrefixList is not None and "reversed" in globalPrefixList:
            self.uriEdit.setCompleter(QCompleter(globalPrefixList["reversed"].keys()))
        self.addOrEdit=True
        if prefix is not None:
            self.addOrEdit=False
            self.prefixEdit.setText(prefix)
        if uri is not None:
            self.addOrEdit=False
            self.uriEdit.setText(uri)
        self.saveButton.clicked.connect(self.savePrefix)

    def checkSuggestion(self):
        if self.globalPrefixList is not None and self.prefixEdit.text()==self.prefixEdit.completer().currentCompletion() \
                and self.prefixEdit.text() in self.globalPrefixList["normal"]:
            self.uriEdit.setText(self.globalPrefixList["normal"][self.prefixEdit.text()])
        UIUtils.check_state(self.prefixEdit)

    def savePrefix(self):
        if self.addOrEdit:
            item=QListWidgetItem()
            item.setText(f"{self.prefixEdit.text()}: <{self.uriEdit.text()}>")
            item.setData(256, self.uriEdit.text())
            item.setData(257, self.prefixEdit.text())
            self.prefixList.addItem(item)
            self.prefixList.sortItems()
        else:
            for item in self.prefixList.selectedItems():
                item.setText(f"{self.prefixEdit.text()}: <{self.uriEdit.text()}>")
                item.setData(256,self.uriEdit.text())
                item.setData(257, self.prefixEdit.text())
        self.close()
