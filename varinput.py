from qgis.PyQt.QtWidgets import QDialog, QLabel, QLineEdit,QPushButton,QListWidget,QComboBox,QMessageBox,QRadioButton,QListWidgetItem,QTableWidgetItem,QCheckBox
from qgis.PyQt.QtGui import QTextCursor
from qgis.PyQt import uic
from qgis.core import QgsProject
from PyQt5.QtCore import Qt
from .searchdialog import SearchDialog
import json
import requests
import os.path

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'varinput.ui'))

class VarInputDialog(QDialog, FORM_CLASS):      

    inputfield=None
    
    chooseField=None
    
    chooseLayer=None

    columnvars=None

    def __init__(self,parent,inputfield,columnvars):
        super(QDialog, self).__init__()
        self.setupUi(self)
        layers = QgsProject.instance().layerTreeRoot().children()
        self.inputfield=inputfield
        self.columnvars=columnvars
        self.chooseLayer.clear()
        for layer in layers:
            self.chooseLayer.addItem(layer.name())
        self.chooseLayer.currentIndexChanged.connect(self.layerselectaction)
        self.chooseField.clear()   
        self.applyButton.clicked.connect(self.applyVar)
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
        if layer.featureCount()==0:
            msgBox=QMessageBox()
            msgBox.setText("The layer column does not contain any features, therefore no query variable will be created!")
            msgBox.exec()
            self.close()
            return
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