from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt import uic
from qgis.core import QgsApplication
import os

from ..tasks.querylayertask import QueryLayerTask
from ..util.sparqlutils import SPARQLUtils

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/querylimitedinstancesdialog.ui'))

# Class representing a search dialog which may be used to search for concepts or properties.

class QueryLimitedInstancesDialog(QDialog, FORM_CLASS):

    def __init__(self, triplestoreconf,concept,nodetype):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.triplestoreconf=triplestoreconf
        self.concept=concept
        self.nodetype=nodetype
        self.queryButton.clicked.connect(self.queryWithLimit)
        self.cancelButton.clicked.connect(self.close)

    def queryWithLimit(self):
        if self.nodetype == SPARQLUtils.geoclassnode:
            if "geotriplepattern" in self.triplestoreconf:
                self.qlayerinstance = QueryLayerTask(
                    "All Instances to Layer: " + str(self.concept),
                    self.triplestoreconf["endpoint"],
                    "SELECT ?" + " ?".join(self.triplestoreconf[
                                               "mandatoryvariables"]) + " ?rel ?val\n WHERE\n {\n ?item <" + str(
                        self.triplestoreconf["typeproperty"]) + "> <" + str(
                        self.concept) + "> . ?item ?rel ?val . " +
                    self.triplestoreconf["geotriplepattern"][0] + "\n } LIMIT "+self.amountOfInstancesEdit.currentText(),
                    self.triplestoreconf, False, SPARQLUtils.labelFromURI(self.concept), None)
            else:
                self.qlayerinstance = QueryLayerTask(
                    "All Instances to Layer: " + str(self.concept),
                    self.triplestoreconf["endpoint"],
                    "SELECT ?item ?rel ?val\n WHERE\n {\n ?item <" + str(
                        self.triplestoreconf["typeproperty"]) + "> <" + str(
                        self.concept) + "> .\n ?item ?rel ?val .\n } LIMIT "+self.amountOfInstancesEdit.currentText(),
                    self.triplestoreconf, True, SPARQLUtils.labelFromURI(self.concept), None)
        else:
            self.qlayerinstance = QueryLayerTask(
                "All Instances to Layer: " + str(self.concept),
                self.triplestoreconf["endpoint"],
                "SELECT ?item ?rel ?val\n WHERE\n {\n ?item <" + str(
                    self.triplestoreconf["typeproperty"]) + "> <" + str(
                    self.concept) + "> . ?item ?rel ?val .\n } LIMIT "+self.amountOfInstancesEdit.currentText(),
                self.triplestoreconf, True, SPARQLUtils.labelFromURI(self.concept), None)
        QgsApplication.taskManager().addTask(self.qlayerinstance)