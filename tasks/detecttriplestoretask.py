import json
import os
from ..util.graphutils import GraphUtils
from qgis.utils import iface
from qgis.core import Qgis,QgsTask, QgsMessageLog
from qgis.PyQt.QtWidgets import QMessageBox

MESSAGE_CATEGORY = 'DetectTripleStoreTask'

class DetectTripleStoreTask(QgsTask):
    """This shows how to subclass QgsTask"""

    def __init__(self, description, triplestoreconf, endpoint, triplestorename, credentialUserName, credentialPassword,authmethod, testURL, testConfiguration, prefixes,
                 prefixstore, tripleStoreChooser, comboBox, permanentAdd,detectnamespaces, parentdialog, progress):
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
        self.comboBox = comboBox
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
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description+" "+str(self.testURL)+" "+str(self.testConfiguration)), MESSAGE_CATEGORY, Qgis.Info)
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
                self.comboBox.addItem(self.triplestorename)
                if self.tripleStoreChooser != None:
                    self.tripleStoreChooser.addItem(self.triplestorename)
                index = len(self.triplestoreconf)
                self.triplestoreconf.append({})
                self.triplestoreconf[index] = self.gutils.configuration
                self.addTripleStore = False
                self.prefixes.append("")
                for prefix in self.gutils.configuration["prefixes"]:
                    self.prefixes[len(self.prefixes)-1] += "PREFIX " + prefix + ":<" + self.gutils.configuration["prefixes"][prefix] + ">\n"
                if self.permanentAdd != None and self.permanentAdd:
                    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
                    f = open(os.path.join(__location__, 'triplestoreconf_personal.json'), "w")
                    f.write(json.dumps(self.triplestoreconf, indent=2))
                    f.close()
                if self.parentdialog != None:
                    self.parentdialog.close()
        elif self.gutils.feasibleConfiguration:
            msgBox = QMessageBox()
            msgBox.setText("Automatic Detection Successful")
            msgBox.setWindowTitle("Automatic Detection Successful")
            msgBox.exec()
        else:
            msgBox = QMessageBox()
            msgBox.setText("Automatic Detection Failed")
            msgBox.setWindowTitle("Automatic Detection Failed")
            msgBox.exec()
        iface.messageBar().pushMessage("Detect Triple Store Configuration", "OK", level=Qgis.Success)
