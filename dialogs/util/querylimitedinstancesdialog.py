from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt import uic
from qgis.core import QgsApplication
import os

from ...util.ui.uiutils import UIUtils
from ...tasks.query.querylayertask import QueryLayerTask
from ...util.sparqlutils import SPARQLUtils

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/querylimitedinstancesdialog.ui'))

# Class representing a search dialog which may be used to search for concepts or properties.
class QueryLimitedInstancesDialog(QDialog, FORM_CLASS):

    def __init__(self, triplestoreconf,concept,nodetype,title="Query limited instances"):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.setWindowTitle(title)
        self.setWindowIcon(UIUtils.queryinstancesicon)
        self.triplestoreconf=triplestoreconf
        self.concept=concept
        self.nodetype=nodetype
        self.queryButton.clicked.connect(self.queryWithLimit)
        self.cancelButton.clicked.connect(self.close)

    def queryWithLimit(self):
        limitstatement = " LIMIT " + str(self.amountOfInstancesEdit.value())
        if self.skipFirstInstancesEdit.value() > 0:
            limitstatement += " OFFSET " + str(self.skipFirstInstancesEdit.value())
        if self.nodetype == SPARQLUtils.geoclassnode:
            if "geotriplepattern" in self.triplestoreconf:
                thequery="SELECT ?" + " ?".join(self.triplestoreconf[
                                               "mandatoryvariables"]) + " ?rel ?val\n WHERE\n {\n { SELECT ?item WHERE { ?item <" + str(
                        self.triplestoreconf["typeproperty"]) + "> <" + str(
                        self.concept) + "> . } "+limitstatement+" } ?item ?rel ?val . " +self.triplestoreconf["geotriplepattern"][0] + "\n }"
                self.qlayerinstance = QueryLayerTask(
                    "All Instances to Layer: " + str(self.concept),
                    self.concept,
                    self.triplestoreconf["resource"],
                    thequery,
                    self.triplestoreconf, False, SPARQLUtils.labelFromURI(self.concept), None)
            else:
                thequery="SELECT ?item ?rel ?val\n WHERE\n {\n { SELECT ?item WHERE { ?item <" + str(
                        self.triplestoreconf["typeproperty"]) + "> <" + str(
                        self.concept) + "> . } "+limitstatement+" }\n ?item ?rel ?val .\n }"
                self.qlayerinstance = QueryLayerTask(
                    "All Instances to Layer: " + str(self.concept),
                    self.concept,
                    self.triplestoreconf["resource"],
                    thequery,
                    self.triplestoreconf, True, SPARQLUtils.labelFromURI(self.concept), None)
        else:
            thequery="SELECT ?item ?rel ?val\n WHERE\n {\n { SELECT ?item WHERE { ?item <" + str(
                    self.triplestoreconf["typeproperty"]) + "> <" + str(
                    self.concept) + "> . } "+limitstatement+"} ?item ?rel ?val .\n }"
            self.qlayerinstance = QueryLayerTask(
                "All Instances to Layer: " + str(self.concept),
                self.concept,
                self.triplestoreconf["resource"],
                thequery,
                self.triplestoreconf, True, SPARQLUtils.labelFromURI(self.concept), None)
        QgsApplication.taskManager().addTask(self.qlayerinstance)
        self.accept()