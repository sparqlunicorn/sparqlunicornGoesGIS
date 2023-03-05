from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QProgressDialog, QFileDialog,QLineEdit,QMessageBox
from qgis.core import QgsApplication
from qgis.core import Qgis,QgsTask, QgsMessageLog
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem

from ..util.baselayerdialog import BaseLayerDialog
from ...tasks.processing.extractnamespacetask import ExtractNamespaceTask
from ...tasks.processing.ontdoctask import OntDocTask

from ...util.ui.uiutils import UIUtils
import os.path

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/ontdocdialog.ui'))

baselayers={
    "OpenStreetMap (OSM)":{"url":"https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png","default":True,"type":"tile"},
    "AWMC Maptiles":{"url":"https://cawm.lib.uiowa.edu/tiles/{z}/{x}/{y}.png","default":False,"type":"tile"},
    "BaseMap DE":{"url":"https://sgx.geodatenzentrum.de/wms_topplus_web_open","default":False,"type":"wms","layername":"web"},
    "Stamen Toner":{"url":"https://stamen-tiles.a.ssl.fastly.net/toner/{z}/{x}/{y}.png","default":False,"type":"tile"},
    "Stamen Terrain":{"url":"https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png","default":False,"type":"tile"},
    "Stamen Watercolor":{"url":"https://stamen-tiles.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.png","default":False,"type":"tile"}
}

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
        self.namespaceCBox.setModel(QStandardItemModel())
        self.tabWidget.setTabVisible(1,False)
        model = QStandardItemModel()
        self.baseLayerListView.setModel(model)
        self.addbaseLayerButton.clicked.connect(lambda: BaseLayerDialog(self.baseLayerListView,baselayers).exec())
        self.baseLayerListView.doubleClicked.connect(lambda item: BaseLayerDialog(self.baseLayerListView,baselayers,item,item.data(266),item.data(265)).exec())
        for lay in baselayers:
            item = QStandardItem(str(lay)+" <"+str(baselayers[lay]["url"])+">")
            item.setCheckable(True)
            if baselayers[lay]["default"]:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            item.setData(baselayers[lay]["url"],265)
            item.setData(lay,266)
            model.appendRow(item)
        self.tsk=None
        UIUtils.createLanguageSelectionCBox(self.preferredLabelLangCBox,languagemap)

    def extractNamespaces(self,filename):
        self.tsk=ExtractNamespaceTask("Extracting namespaces from "+str(filename),filename,self.namespaceCBox,self.prefixes,None)
        QgsApplication.taskManager().addTask(self.tsk)

    def createDocumentation(self):
        progress = QProgressDialog("Creating ontology documentation... ", "Abort",0, 0, self)
        progress.setWindowTitle("Ontology Documentation")
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowIcon(UIUtils.sparqlunicornicon)
        progress.setCancelButton(None)
        maincolor=self.mainColorSelector.color().name()
        titlecolor=self.titleColorSelector.color().name()
        graphname=self.inputRDFFileWidget.filePath()
        logoname=self.logoFileWidget.filePath()
        QgsMessageLog.logMessage("Graph "+str(graphname), "Ontdocdialog", Qgis.Info)
        if graphname==None or graphname=="":
                graphname="test"
        namespace=self.namespaceCBox.currentText()
        if namespace==None or namespace=="":
                namespace="http://lod.squirrel.link/data/"
        baselayerss={}
        model=self.baseLayerListView.model()
        for index in range(model.rowCount()):
            item = model.item(index)
            if item.isCheckable() and item.checkState() == Qt.Checked:
                baselayerss[item.data(266)]=baselayers[item.data(266)]
        self.qtask = OntDocTask("Creating ontology documentation... ",
                                         graphname, namespace,self.prefixes,self.licenseCBox.currentText(),
                                        self.preferredLabelLangCBox.currentData(UIUtils.dataslot_language),
                                        self.outFolderWidget.filePath(),self.additionalCollections.checkState(),baselayerss, maincolor, titlecolor,progress,logoname)
        QgsApplication.taskManager().addTask(self.qtask)