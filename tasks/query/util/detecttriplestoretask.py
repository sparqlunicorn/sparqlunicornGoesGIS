
from ....dialogs.info.detecttriplestoreresultdialog import DetectTripleStoreResultDialog
from ....dialogs.info.errormessagebox import ErrorMessageBox
from ....util.sparqlutils import SPARQLUtils
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
            DetectTripleStoreResultDialog(self.parentdialog,self.triplestoreconf,self.triplestorename,self.tripleStoreChooser,self.prefixes,self.gutils.configuration,
                                              self.permanentAdd,self.gutils.message,self.gutils.missingproperties).exec()
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
