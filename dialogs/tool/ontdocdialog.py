from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QProgressDialog, QFileDialog,QLineEdit,QMessageBox
from qgis.core import QgsApplication
from qgis.core import Qgis,QgsTask, QgsMessageLog
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QStandardItemModel
from ...tasks.processing.extractnamespacetask import ExtractNamespaceTask
from ...tasks.processing.ontdoctask import OntDocTask

from ...util.ui.uiutils import UIUtils
import os.path

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/ontdocdialog.ui'))

##
#  Class representing the graph validation dialog.
class OntDocDialog(QtWidgets.QDialog, FORM_CLASS):
    ## The triple store configuration file
    triplestoreconf = None
    ## Prefix map
    prefixes = None
    ## LoadGraphTask for loading a graph from a file or uri
    qtask = None

    def __init__(self, languagemap,triplestoreconf={}, prefixes=None, parent=None,title="Ontology Documentation"):
        """Constructor."""
        super(OntDocDialog, self).__init__()
        self.setupUi(self)
        self.triplestoreconf=triplestoreconf
        self.prefixes=prefixes
        self.createDocumentationButton.clicked.connect(self.createDocumentation)
        self.inputRDFFileWidget.fileChanged.connect(self.extractNamespaces)
        self.groupBox.hide()
        self.namespaceCBox.setModel(QStandardItemModel())
        self.tsk=None
        UIUtils.createLanguageSelectionCBox(self.preferredLabelLangCBox,languagemap)

    def extractNamespaces(self,filename):
        self.tsk=ExtractNamespaceTask("Extracting namespaces from "+str(filename),filename,self.namespaceCBox,self.prefixes,None)
        QgsApplication.taskManager().addTask(self.tsk)

    def createDocumentation(self):
        progress = QProgressDialog("Creating ontology documentation... ", "Abort",
                                   0, 0, self)
        progress.setWindowTitle("Ontology Documentation")
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowIcon(UIUtils.sparqlunicornicon)
        progress.setCancelButton(None)
        maincolor=self.mainColorSelector.color().name()
        titlecolor=self.titleColorSelector.color().name()
        graphname=self.inputRDFFileWidget.filePath()
        QgsMessageLog.logMessage("Graph "+str(graphname), "Ontdocdialog", Qgis.Info)
        if graphname==None or graphname=="":
                graphname="test"
        namespace=self.namespaceCBox.currentText()
        if namespace==None or namespace=="":
                namespace="http://lod.squirrel.link/data/"
        self.qtask = OntDocTask("Creating ontology documentation... ",
                                         graphname, namespace,self.prefixes,self.licenseCBox.currentText(),
                                        self.preferredLabelLangCBox.currentData(UIUtils.dataslot_language),
                                        self.outFolderWidget.filePath(), maincolor ,titlecolor,progress)
        QgsApplication.taskManager().addTask(self.qtask)