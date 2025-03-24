import os

from PyQt.QtWidgets import QMessageBox
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QDialog, QCompleter
from qgis.PyQt.QtGui import QRegularExpressionValidator
from qgis.PyQt.QtGui import QStandardItem

from ...util.ui.uiutils import UIUtils

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/baselayerdialog.ui'))

# Class representing a search dialog which may be used to search for concepts or properties.
class BaseLayerDialog(QDialog, FORM_CLASS):
    def __init__(self, baseurlList,baseurlstore,item=None, name=None, uri=None):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.item=item
        self.baseurlstore=baseurlstore
        self.prefixList = baseurlList
        self.baseLayerURLEdit.setValidator(QRegularExpressionValidator(UIUtils.baselayerurlregex, self))
        self.baseLayerURLEdit.textChanged.connect(lambda: UIUtils.check_state(self.baseLayerURLEdit))
        self.addOrEdit = True
        self.name=name
        if name != None:
            self.addOrEdit = False
            self.baseLayerNameEdit.setText(name)
        else:
            self.baseLayerNameEdit.setText("My new baselayer")
        if uri != None:
            self.addOrEdit = False
            self.baseLayerURLEdit.setText(uri)
        else:
            self.baseLayerURLEdit.setText("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png")
        self.okButton.clicked.connect(self.saveBaseLayer)

    def saveBaseLayer(self):
        if "{x}" not in self.baseLayerURLEdit.text() or "{y}" not in self.baseLayerURLEdit.text() or "{y}" not in self.baseLayerURLEdit.text():
            msgBox=QMessageBox()
            msgBox.setText("The Base Layer URL is invalid!\n Please check the availability of {x} {y} {z} parameters in your URL")
            msgBox.exec()
        else:
            if self.addOrEdit and self.baseLayerNameEdit.text() not in self.baseurlstore:
                item=QStandardItem()
                item.setText(self.baseLayerNameEdit.text() + ": <" + str(self.baseLayerURLEdit.text()) + ">")
                item.setData(self.baseLayerURLEdit.text(),265)
                item.setData(self.baseLayerNameEdit.text(),266)
                item.setCheckable(True)
                item.setCheckState(Qt.Unchecked)
                self.baseurlstore[self.baseLayerNameEdit.text()] = {"url": self.baseLayerURLEdit.text()}
                self.prefixList.model().appendRow(item)
            else:
                self.prefixList.model().itemFromIndex(self.item).setData(self.baseLayerURLEdit.text(),265)
                self.prefixList.model().itemFromIndex(self.item).setData(self.baseLayerNameEdit.text(),266)
                self.prefixList.model().itemFromIndex(self.item).setText(self.baseLayerNameEdit.text()+": <"+str(self.baseLayerURLEdit.text())+">")
                del self.baseurlstore[self.name]
                self.baseurlstore[self.baseLayerNameEdit.text()]={"url":self.baseLayerURLEdit.text()}
            self.close()