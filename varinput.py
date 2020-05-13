from qgis.PyQt.QtWidgets import QDialog, QLabel, QLineEdit,QPushButton,QListWidget,QComboBox,QMessageBox,QRadioButton,QListWidgetItem,QTableWidgetItem,QCheckBox
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

    columnvars=None

    def __init__(self,parent,inputfield,columnvars):
        super(QDialog, self).__init__()
        layers = QgsProject.instance().layerTreeRoot().children()
        # Populate the comboBox with names of all the loaded unicorn layers
        self.inputfield=inputfield
        self.resize(200,150)
        self.columnvars=columnvars
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
        self.isLabelLabel=QCheckBox("Is Label",self)
        self.isLabelLabel.move(250,40)
        self.labelLangLabel=QLabel("Label Lang: ",self)
        self.labelLangLabel.move(350,40)
        self.labelLang=QLineEdit(self)
        self.labelLang.move(430,40)
        self.varNameLabel=QLabel("Variable Name:",self)
        self.varNameLabel.move(10,70)
        self.varNameEdit=QLineEdit(self)
        self.varNameEdit.move(150,70)
        self.varTypeLabel=QLabel("Variable Type:",self)
        self.varTypeLabel.move(270,75)
        self.varType=QComboBox(self)
        self.varType.move(370,70)
        self.varType.addItem("Automatic")
        self.varType.addItem("String")
        self.varType.addItem("URI")
        self.varType.addItem("Double")
        self.varType.addItem("Integer")
        self.varType.addItem("Date")
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
        layers = QgsProject.instance().layerTreeRoot().children()
        index=self.chooseLayer.currentIndex()
        layer = layers[index].layer()
        layername=self.chooseLayer.currentText()
        fieldname=self.chooseField.currentText()
        if self.varNameEdit.text()!="":
            varname="?_"+self.varNameEdit.text()
        else:
            varname="?_"+layername.replace(" ","")+"_"+fieldname.replace(" ","")
        self.inputfield.insertPlainText(varname)
        queryinsert="VALUES "+varname+" {"
        attlist={""}
        for f in layer.getFeatures():
            attlist.add(f[fieldname])
        for att in attlist:
            if att!="":
                if self.varType.currentText()=="URI" or (self.varType.currentText()=="Automatic" and att.startswith("http")):
                    query+="<"+att+">"
                elif self.varType.currentText()=="Integer" or self.varType.currentText()=="Double":
                    query+=att
                elif self.varType.currentText()=="Date":
                    query+="\""+att+"\"^^xsd:date"
                elif self.varType.currentText()=="String" or self.varType.currentText()=="Automatic":
                    queryinsert+="\""+att+"\""
                    if self.isLabelLabel.isChecked():
                        queryinsert+="@"+self.labelLang.text()
                queryinsert+=" "
        queryinsert+="}"
        self.columnvars[varname]=queryinsert
        self.close()