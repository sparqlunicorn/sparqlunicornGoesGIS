from qgis.PyQt.QtWidgets import QDialog, QMessageBox
from qgis.PyQt import uic
import os.path

from ...util.ui.uiutils import UIUtils

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/varinputdialog.ui'))

## Class representing the variable input dialog which maps geodataset columns to SPARQL query variables.
class VarInputDialog(QDialog, FORM_CLASS):
    # The inputfield to which the result variable is saved
    inputfield = None
    # The field of the geodataset which has been chosen to be represented by the variable
    chooseField = None
    # The laayer which column is chosen to be represented by the variable
    chooseLayer = None
    # The map of already exisiting variables which represent geodataset columns
    columnvars = None

    ## 
    #  @brief Initializes the dialog by loading existing layers.
    #  
    #  @param self The object pointer 
    #  @param parent A parent window if available
    #  @param inputfield The inputfield to which the variable will be saved
    #  @param columnvars A map of already existing variable mappings  
    def __init__(self, parent, inputfield, columnvars,languagemap):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(UIUtils.columnasvaricon)
        self.inputfield = inputfield
        self.columnvars = columnvars
        self.applyButton.clicked.connect(self.applyVar)
        self.chooseField.setLayer(self.chooseLayer.currentLayer())
        UIUtils.createLanguageSelectionCBox(self.labelLang,languagemap)


    ## 
    #  @brief Inserts a variable into the query as stated in the query dialog.
    #  
    #  @param self The object pointer
    #  
    #  @details The variable will be inserted and the corresponding SPARQL VALUES statement will be generated in the background
    #  
    def applyVar(self):
        layer = self.chooseLayer.currentLayer()
        layername = self.chooseLayer.currentText()
        fieldname = self.chooseField.currentText()
        if layer.featureCount() == 0:
            msgBox = QMessageBox()
            msgBox.setText(
                "The layer column does not contain any features, therefore no query variable will be created!")
            msgBox.exec()
            self.close()
            return
        if self.varNameEdit.text() != "":
            varname = "?_" + self.varNameEdit.text()
        else:
            varname = f'?_{layername.replace(" ", "")}_{fieldname.replace(" ", "")}'
        self.inputfield.insertPlainText(varname)
        queryinsert = "VALUES " + varname + " {"
        attlist = {""}
        for f in layer.getFeatures():
            attlist.add(f[fieldname])
        for att in attlist:
            if att != "":
                if self.varType.currentText() == "URI" or (
                        self.varType.currentText() == "Automatic" and att.startswith("http")):
                    queryinsert += f"<{att}>"
                elif self.varType.currentText() == "Integer" or self.varType.currentText() == "Double":
                    queryinsert += att
                elif self.varType.currentText() == "Date":
                    queryinsert += f'"{att}"^^xsd:date'
                elif self.varType.currentText() == "String" or self.varType.currentText() == "Automatic":
                    queryinsert += f'"{att}"'
                    if self.isLabelLabel.isChecked():
                        queryinsert += "@" + self.labelLang.text()
                queryinsert += " "
        queryinsert += "}"
        self.columnvars[varname] = queryinsert
        self.close()
