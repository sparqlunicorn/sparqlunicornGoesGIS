import json
import os

from ....dialogs.info.errormessagebox import ErrorMessageBox
from ....util.sparqlutils import SPARQLUtils
from ....util.ui.uiutils import UIUtils
from ....util.graphutils import GraphUtils
from qgis.utils import iface
from qgis.core import Qgis,QgsTask
from qgis.PyQt.QtWidgets import QMessageBox

MESSAGE_CATEGORY = 'DetectTripleStoreTask'

class DetectTripleStoreTask(QgsTask):
    """This shows how to subclass QgsTask"""

    def __init__(self, description, triplestoreconf, endpoint, triplestorename, credentialUserName, credentialPassword,authmethod, testURL, testConfiguration, prefixes,
                 prefixstore, tripleStoreChooser, permanentAdd,detectnamespaces, parentdialog,mainWin, progress):
        super().__init__(description, QgsTask.CanCancel)
        self.description = description
        self.exception = None
        self.prefixes = prefixes
        self.prefixstore = prefixstore
        self.detectnamespaces=detectnamespaces
        self.permanentAdd = permanentAdd
        self.progress = progress
        self.credentialUserName=credentialUserName
        self.credentialPassword=credentialPassword
        self.authmethod=authmethod
        self.triplestorename = triplestorename
        self.tripleStoreChooser = tripleStoreChooser
        self.mainWin=mainWin
        self.parentdialog = parentdialog
        self.triplestoreurl = endpoint
        self.triplestoreconf = triplestoreconf
        self.testURL = testURL
        self.message=""
        self.configuration = {}
        self.testConfiguration = testConfiguration
        self.message = ""
        self.feasibleConfiguration = False
        self.gutils=GraphUtils(self.testURL)

    def run(self):
        #QgsMessageLog.logMessage('Started task "{}"'.format(self.description+" "+str(self.testURL)+" "+str(self.testConfiguration)), MESSAGE_CATEGORY, Qgis.Info)
        if self.testURL and not self.testConfiguration:
            self.gutils.testTripleStoreConnection(self.triplestoreurl)
            return True
        if self.testConfiguration and not self.testURL:
            res = self.gutils.detectTripleStoreConfiguration(self.triplestorename,self.triplestoreurl,self.detectnamespaces,self.prefixstore,self.progress,self.credentialUserName,self.credentialPassword,self.authmethod)
        return True

    def finished(self, result):
        self.progress.close()
        if self.gutils.feasibleConfiguration and self.testConfiguration:
            msgBox = QMessageBox()
            msgBox.setStandardButtons(QMessageBox.Yes)
            msgBox.addButton(QMessageBox.No)
            msgBox.setWindowTitle("Automatic Detection Successful")
            msgBox.setText(self.gutils.message)
            if msgBox.exec() != QMessageBox.Yes:
                return
            else:
                if "type" in self.gutils.configuration and self.gutils.configuration["type"]=="geosparqlendpoint":
                    self.tripleStoreChooser.addItem(UIUtils.geoendpointicon, self.triplestorename + " [GeoSPARQL Endpoint]")
                else:
                    self.tripleStoreChooser.addItem(UIUtils.linkeddataicon,self.triplestorename+" [SPARQL Endpoint]")
                index = len(self.triplestoreconf)
                self.triplestoreconf.append({})
                self.triplestoreconf[index] = self.gutils.configuration
                self.addTripleStore = False
                self.prefixes.append("")
                for prefix in self.gutils.configuration["prefixes"]:
                    self.prefixes[len(self.prefixes)-1] += "PREFIX " + prefix + ":<" + self.gutils.configuration["prefixes"][prefix] + ">\n"
                if self.permanentAdd is not None and self.permanentAdd:
                    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
                    f = open(os.path.join(__location__, 'triplestoreconf_personal.json'), "w")
                    f.write(json.dumps(self.triplestoreconf, indent=2))
                    f.close()
                if self.tripleStoreChooser is not None:
                    #self.tripleStoreChooser.addItem(self.triplestorename)
                    self.tripleStoreChooser.setCurrentIndex(self.tripleStoreChooser.count()-1)
                if self.parentdialog is not None:
                    self.parentdialog.close()
        elif self.gutils.feasibleConfiguration:
            msgBox = QMessageBox()
            msgBox.setText("Automatic Detection Successful")
            msgBox.setWindowTitle("Automatic Detection Successful")
            msgBox.exec()
        else:
            msgBox = ErrorMessageBox("Automatic Detection Failed","")
            msgBox.setText("Automatic Detection Failed:\n"+str(SPARQLUtils.exception))
            msgBox.exec()
        iface.messageBar().pushMessage("Detect Triple Store Configuration", "OK", level=Qgis.Success)
