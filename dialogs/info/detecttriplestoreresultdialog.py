from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtWidgets import QStyle
from qgis.PyQt.QtGui import QIcon
from ...util.ui.uiutils import UIUtils
import os
import json
from qgis.PyQt.QtGui import QRegExpValidator
from qgis.PyQt import uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/detecttriplestoreresultdialog.ui'))

class DetectTripleStoreResultDialog(QDialog, FORM_CLASS):

    def __init__(self,parentdialog,triplestoreconf,triplestorename,triplestorechooser,prefixes,configuration,permanentAdd,capabilities,missingproperties,typeproperty="http://www.w3.org/1999/02/22-rdf-syntax-ns#type",subclassofproperty="http://www.w3.org/2000/01/rdf-schema#subClassOf"):
        QDialog.__init__(self,parentdialog)
        self.setupUi(self)
        self.setWindowTitle("Triple Store Detection Result")
        self.setWindowIcon(QIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxInformation'))))
        self.parentdialog=parentdialog
        self.permanentAdd=permanentAdd
        self.missingproperties=missingproperties
        self.triplestoreconf=triplestoreconf
        self.triplestorename=triplestorename
        self.tripleStoreChooser=triplestorechooser
        self.prefixes=prefixes
        self.configuration=configuration
        self.capabilitiesLabel.setText(capabilities)
        if len(self.missingproperties)>0:
            self.propertiesMissingLabel.setText("<html><font color=red><b>The plugin could not detect type or subclass properties for this triple store.<br/> Please provide them for the ClassTree View to work properly</font></b></html>")
            if "typeproperty" not in self.missingproperties:
                self.typePropertyEdit.setText(self.configuration["typeproperty"])
            self.typePropertyEdit.setValidator(QRegExpValidator(UIUtils.urlregex, self))
            self.typePropertyEdit.textChanged.connect(lambda: UIUtils.check_state(self.typePropertyEdit))
            self.typePropertyEdit.textChanged.emit(self.typePropertyEdit.text())
            if "subclassproperty" not in self.missingproperties:
                self.typePropertyEdit.setText(self.configuration["subclassproperty"])
            self.subClassOfEdit.setText(self.configuration["subclassproperty"])
            self.subClassOfEdit.setValidator(QRegExpValidator(UIUtils.urlregex, self))
            self.subClassOfEdit.textChanged.connect(lambda: UIUtils.check_state(self.subClassOfEdit))
            self.subClassOfEdit.textChanged.emit(self.subClassOfEdit.text())
            self.geoPropertyEdit.setValidator(QRegExpValidator(UIUtils.urlregex, self))
            self.geoPropertyEdit.textChanged.connect(lambda: UIUtils.check_state(self.geoPropertyEdit))
            self.geoPropertyEdit.textChanged.emit(self.geoPropertyEdit.text())
            self.stackedWidget.show()
        else:
            self.stackedWidget.hide()
        self.addTripleStoreButton.clicked.connect(self.addConfiguration)
        self.cancelButton.clicked.connect(self.close)
        self.show()


    def addConfiguration(self):
        if self.missingproperties:
            if self.typePropertyEdit.text()=="":
                self.configuration["typeproperty"]="http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
            else:
                self.configuration["typeproperty"]=self.typePropertyEdit.text()
            if self.subClassOfEdit.text()=="":
                self.configuration["subclassproperty"]="http://www.w3.org/2000/01/rdf-schema#subClassOf"
            else:
                self.configuration["subclassproperty"]=self.subClassOfEdit.text()
        if "type" in self.configuration and self.configuration["type"] == "geosparqlendpoint":
            self.tripleStoreChooser.addItem(UIUtils.geoendpointicon, self.triplestorename + " [GeoSPARQL Endpoint]")
        else:
            self.tripleStoreChooser.addItem(UIUtils.linkeddataicon, self.triplestorename + " [SPARQL Endpoint]")
        index = len(self.triplestoreconf)
        self.triplestoreconf.append({})
        self.triplestoreconf[index] = self.configuration
        self.addTripleStore = False
        self.prefixes.append("")
        for prefix in self.configuration["prefixes"]:
            self.prefixes[len(self.prefixes) - 1] += "PREFIX " + prefix + ":<" + self.configuration["prefixes"][
                prefix] + ">\n"
        if self.permanentAdd is not None and self.permanentAdd:
            __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            f = open(os.path.join(__location__, 'triplestoreconf_personal.json'), "w")
            f.write(json.dumps(self.triplestoreconf, indent=2))
            f.close()
        if self.tripleStoreChooser is not None:
            # self.tripleStoreChooser.addItem(self.triplestorename)
            self.tripleStoreChooser.setCurrentIndex(self.tripleStoreChooser.count() - 1)
        if self.parentdialog is not None:
            self.parentdialog.close()
        self.close()