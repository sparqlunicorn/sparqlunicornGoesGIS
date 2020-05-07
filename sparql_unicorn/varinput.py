from qgis.PyQt.QtWidgets import QDialog, QLabel, QLineEdit,QPushButton,QListWidget,QComboBox,QMessageBox,QRadioButton,QListWidgetItem,QTableWidgetItem
from qgis.PyQt.QtGui import QTextCursor
from qgis.core import QgsProject
from PyQt5.QtCore import Qt
from .searchdialog import SearchDialog
import json
import requests

class VarInputDialog(QDialog):      

    inputfield=None
    
    chooseField=None
    
    chooseLayer=None

    def __init__(self,parent,inputfield):
        super(QDialog, self).__init__()
        layers = QgsProject.instance().layerTreeRoot().children()
        # Populate the comboBox with names of all the loaded unicorn layers
        self.inputfield=inputfield
        self.resize(200,200)
        layerLabel=QLabel("Choose Layer: ",self)
        layerLabel.move(10,10)
        self.chooseLayer=QComboBox(self)
        self.chooseLayer.move(150,10)
        self.chooseLayer.clear()
        for layer in layers:
            self.chooseLayer.addItem(layer.name())
        self.chooseLayer.currentIndexChanged.connect(self.layerselectaction)
        fieldLabel=QLabel("Choose Field: ",self)
        fieldLabel.move(10,40)
        self.chooseField=QComboBox(self)
        self.chooseField.move(150,40)
        self.chooseField.clear()
        applyButton=QPushButton("Apply",self)
        applyButton.move(10,100)    
        applyButton.clicked.connect(self.applyVar)
        self.layerselectaction()
        
        
    def layerselectaction(self):
        layers = QgsProject.instance().layerTreeRoot().children()
        index=self.chooseLayer.currentIndex()
        layer = layers[index].layer()
        fieldnames = [field.name() for field in layer.fields()]
        self.chooseField.clear()
        for field in fieldnames:
            self.chooseField.addItem(field)
 
    def applyVar(self):
        layername=self.chooseLayer.currentText().replace(" ","")
        fieldname=self.chooseField.currentText().replace(" ","")
        varname="?__"+layername+"__"+fieldname+"__"
        self.inputfield.insertPlainText(varname)
        self.close()
