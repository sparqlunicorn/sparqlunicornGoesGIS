from PyQt5.QtWidgets import QProgressDialog
from qgis.PyQt.QtWidgets import QApplication, QMenu, QAction, QFileDialog
from qgis.PyQt.QtGui import QDesktopServices
from qgis._core import Qgis
from qgis.core import (
    QgsApplication, QgsMessageLog
)
from qgis.PyQt.QtCore import Qt, QUrl
from ..instancedatadialog import InstanceDataDialog
from ...tasks.querylayertask import QueryLayerTask
from ...tasks.subclassquerytask import SubClassQueryTask
from ...util.ui.uiutils import UIUtils
from ...tasks.instanceamountquerytask import InstanceAmountQueryTask
from ...tasks.instancelistquerytask import InstanceListQueryTask
from ..dataschemadialog import DataSchemaDialog
from ..querylimitedinstancesdialog import QueryLimitedInstancesDialog
from ...util.sparqlutils import SPARQLUtils

MESSAGE_CATEGORY = 'ContextMenu'

class TabContextMenu(QMenu):

    def __init__(self,name,parent,position,triplestoreconf):
        super().__init__(name,parent)
        self.triplestoreconf=triplestoreconf
        actionsaveRDF = QAction("Save Contents as RDF")
        self.addAction(actionsaveRDF)
        actionsaveRDF.triggered.connect(self.saveTreeToRDF)
        actionsaveClassesRDF = QAction("Save Classes as RDF")
        self.addAction(actionsaveClassesRDF)
        actionsaveClassesRDF.triggered.connect(self.saveClassesTreeToRDF)
        actionsaveVisibleRDF = QAction("Save Visible Contents as RDF")
        self.addAction(actionsaveVisibleRDF)
        actionsaveVisibleRDF.triggered.connect(self.saveVisibleTreeToRDF)
        self.exec_(position)

    def saveClassesTreeToRDF(self, context):
        filename, _filter = QFileDialog.getSaveFileName(
                self, "Select   output file ", "", "Linked Data (*.ttl *.n3 *.nt *.graphml)", )
        if filename == "":
                return
        result=set()
        UIUtils.iterateTree(context.invisibleRootItem(),result,False,True,self.triplestoreconf,context)
        QgsMessageLog.logMessage('Started task "{}"'.format(""+str(result)), MESSAGE_CATEGORY, Qgis.Info)
        with open(filename, 'w') as output_file:
            output_file.write("".join(result))
        return result

    def saveVisibleTreeToRDF(self, context):
        filename, _filter = QFileDialog.getSaveFileName(
                self, "Select   output file ", "", "Linked Data (*.ttl *.n3 *.nt *.graphml)", )
        if filename == "":
                return
        result=set()
        UIUtils.iterateTree(context.invisibleRootItem(),result,True,False,self.triplestoreconf,context)
        QgsMessageLog.logMessage('Started task "{}"'.format(""+str(result)), MESSAGE_CATEGORY, Qgis.Info)
        with open(filename, 'w') as output_file:
            output_file.write("".join(result))
        return result

    def saveTreeToRDF(self, context):
        filename, _filter = QFileDialog.getSaveFileName(
                self, "Select   output file ", "", "Linked Data (*.ttl *.n3 *.nt *.graphml)", )
        if filename == "":
                return
        result=set()
        UIUtils.iterateTree(context.invisibleRootItem(),result,False,False,self.triplestoreconf,context)
        QgsMessageLog.logMessage('Started task "{}"'.format(""+str(result)), MESSAGE_CATEGORY, Qgis.Info)
        with open(filename, 'w') as output_file:
            output_file.write("".join(result))
        return result

class ConceptContextMenu(QMenu):

    def __init__(self,triplestoreconf,position,context,item,menu=None):
        super(ConceptContextMenu, self).__init__()
        if menu==None:
            menu = QMenu("Menu", context)
        menu=ConceptContextMenu.createListContextMenu(item,menu)
        if item.data(257) != SPARQLUtils.instancenode and item.data(257) != SPARQLUtils.geoinstancenode:
            actioninstancecount = QAction("Check instance count")
            menu.addAction(actioninstancecount)
            actioninstancecount.triggered.connect(self.instanceCount)
            actiondataschema = QAction("Query data schema")
            menu.addAction(actiondataschema)
            actiondataschema.triggered.connect(lambda: DataSchemaDialog(
                item.data(256),
                item.data(257),
                item.text(),
                triplestoreconf["endpoint"],
                triplestoreconf, self.prefixes, self.comboBox.currentIndex(),
                "Data Schema View for " + SPARQLUtils.labelFromURI(str(item.data(256)),
                                                                   triplestoreconf[
                                                                       "prefixesrev"])
            ).exec_())
            actionqueryinstances = QAction("Query all instances")
            menu.addAction(actionqueryinstances)
            actionqueryinstances.triggered.connect(self.instanceList)
            if "subclassquery" in triplestoreconf:
                action2 = QAction("Load subclasses")
                menu.addAction(action2)
                action2.triggered.connect(self.loadSubClasses)
            actionsubclassquery = QAction("Create subclass query")
            menu.addAction(actionsubclassquery)
            actionsubclassquery.triggered.connect(self.subclassQuerySelectAction)
            actionquerysomeinstances = QAction("Add some instances as new layer")
            menu.addAction(actionquerysomeinstances)
            actionquerysomeinstances.triggered.connect(lambda: QueryLimitedInstancesDialog(
                triplestoreconf,
                item.data(256),
                item.data(257)
            ).exec_())
            actionaddallInstancesAsLayer = QAction("Add all instances as new layer")
            menu.addAction(actionaddallInstancesAsLayer)
            actionaddallInstancesAsLayer.triggered.connect(self.dataAllInstancesAsLayer)
        else:
            actiondataschema = QAction("Query data")
            menu.addAction(actiondataschema)
            actiondataschema.triggered.connect(self.dataInstanceView)
            actionaddInstanceAsLayer = QAction("Add instance as new layer")
            menu.addAction(actionaddInstanceAsLayer)
            actionaddInstanceAsLayer.triggered.connect(self.dataInstanceAsLayer)
        actionapplicablestyles = QAction("Find applicable styles")
        menu.addAction(actionapplicablestyles)
        actionapplicablestyles.triggered.connect(self.appStyles)
        menu.exec_(context.viewport().mapToGlobal(position))

    @staticmethod
    def createListContextMenu(item,menu=None):
        if menu==None:
            menu = QMenu("Menu")
        actionclip = QAction("Copy IRI to clipboard")
        menu.addAction(actionclip)
        actionclip.triggered.connect(ConceptContextMenu.copyClipBoard)
        action = QAction("Open in Webbrowser")
        menu.addAction(action)
        action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(item.data(256))))
        return menu

    def appStyles(self):
        curindex = self.currentProxyModel.mapToSource(self.currentContext.selectionModel().currentIndex())
        concept = self.currentContextModel.itemFromIndex(curindex).data(256)
        label = self.currentContextModel.itemFromIndex(curindex).text()
        # self.dataschemaDialog = DataSchemaDialog(concept,label,self.triplestoreconf[self.comboBox.currentIndex()]["endpoint"],self.triplestoreconf,self.prefixes,self.comboBox.currentIndex())
        # self.dataschemaDialog.setWindowTitle("Data Schema View for "+str(concept))
        # self.dataschemaDialog.exec_()

    def dataInstanceView(self):
        curindex = self.currentProxyModel.mapToSource(self.currentContext.selectionModel().currentIndex())
        concept = self.currentContextModel.itemFromIndex(curindex).data(256)
        nodetype = self.currentContextModel.itemFromIndex(curindex).data(257)
        label = self.currentContextModel.itemFromIndex(curindex).text()
        self.instancedataDialog = InstanceDataDialog(concept,nodetype,label,self.triplestoreconf[self.comboBox.currentIndex()]["endpoint"],self.triplestoreconf,self.prefixes,self.comboBox.currentIndex())
        self.instancedataDialog.setWindowTitle("Data Instance View for "+SPARQLUtils.labelFromURI(str(concept),self.triplestoreconf[self.comboBox.currentIndex()]["prefixesrev"]))
        self.instancedataDialog.exec_()

    def dataInstanceAsLayer(self):
        curindex = self.currentProxyModel.mapToSource(self.currentContext.selectionModel().currentIndex())
        concept = self.currentContextModel.itemFromIndex(curindex).data(256)
        nodetype = self.currentContextModel.itemFromIndex(curindex).data(257)
        if nodetype==SPARQLUtils.geoinstancenode:
            if "geotriplepattern" in self.triplestoreconf[self.comboBox.currentIndex()]:
                self.qlayerinstance = QueryLayerTask(
                    "Instance to Layer: " + str(concept),
                    self.triplestoreconf[self.comboBox.currentIndex()]["endpoint"],
                    "SELECT ?"+" ?".join(self.triplestoreconf[self.comboBox.currentIndex()]["mandatoryvariables"])+" ?rel ?val\n WHERE\n {\n BIND( <" + str(concept) + "> AS ?item)\n ?item ?rel ?val . " +
                    self.triplestoreconf[self.comboBox.currentIndex()]["geotriplepattern"][0] + "\n }",
                    self.triplestoreconf[self.comboBox.currentIndex()], False, SPARQLUtils.labelFromURI(concept), None)
            else:
                self.qlayerinstance = QueryLayerTask(
                "Instance to Layer: " + str(concept),
                self.triplestoreconf[self.comboBox.currentIndex()]["endpoint"],
                "SELECT ?item ?rel ?val \n WHERE\n {\n BIND( <"+str(concept)+"> AS ?item)\n ?item ?rel ?val . \n }",
                self.triplestoreconf[self.comboBox.currentIndex()],True, SPARQLUtils.labelFromURI(concept),None)
        else:
            self.qlayerinstance = QueryLayerTask(
                "Instance to Layer: " + str(concept),
                self.triplestoreconf[self.comboBox.currentIndex()]["endpoint"],
                "SELECT ?item ?rel ?val\n WHERE\n {\n BIND( <"+str(concept)+"> AS ?item)\n ?item ?rel ?val .\n }",
                self.triplestoreconf[self.comboBox.currentIndex()],True, SPARQLUtils.labelFromURI(concept),None)
        QgsApplication.taskManager().addTask(self.qlayerinstance)

    def dataAllInstancesAsLayer(self):
        curindex = self.currentProxyModel.mapToSource(self.currentContext.selectionModel().currentIndex())
        concept = self.currentContextModel.itemFromIndex(curindex).data(256)
        nodetype = self.currentContextModel.itemFromIndex(curindex).data(257)
        progress = QProgressDialog(
            "Querying all instances for " + concept,"Abort", 0, 0, self)
        progress.setWindowTitle("Query all instances")
        progress.setWindowModality(Qt.WindowModal)
        if nodetype==SPARQLUtils.geoclassnode:
            if "geotriplepattern" in self.triplestoreconf[self.comboBox.currentIndex()]:
                self.qlayerinstance = QueryLayerTask(
                "All Instances to Layer: " + str(concept),
                    self.triplestoreconf[self.comboBox.currentIndex()]["endpoint"],
                "SELECT ?"+" ?".join(self.triplestoreconf[self.comboBox.currentIndex()]["mandatoryvariables"])+" ?rel ?val\n WHERE\n {\n ?item <"+str(self.triplestoreconf[self.comboBox.currentIndex()]["typeproperty"])+"> <"+str(concept)+"> . ?item ?rel ?val . "+self.triplestoreconf[self.comboBox.currentIndex()]["geotriplepattern"][0]+"\n }",
                self.triplestoreconf[self.comboBox.currentIndex()],False, SPARQLUtils.labelFromURI(concept),progress)
            else:
                self.qlayerinstance = QueryLayerTask(
                "All Instances to Layer: " + str(concept),
                    self.triplestoreconf[self.comboBox.currentIndex()]["endpoint"],
                "SELECT ?item ?rel ?val\n WHERE\n {\n ?item <"+str(self.triplestoreconf[self.comboBox.currentIndex()]["typeproperty"])+"> <"+str(concept)+"> .\n ?item ?rel ?val .\n }",
                self.triplestoreconf[self.comboBox.currentIndex()],True, SPARQLUtils.labelFromURI(concept),progress)
        else:
            self.qlayerinstance = QueryLayerTask(
                "All Instances to Layer: " + str(concept),
                self.triplestoreconf[self.comboBox.currentIndex()]["endpoint"],
                "SELECT ?item ?rel ?val\n WHERE\n {\n ?item <"+str(self.triplestoreconf[self.comboBox.currentIndex()]["typeproperty"])+"> <"+str(concept)+"> . ?item ?rel ?val .\n }",
                self.triplestoreconf[self.comboBox.currentIndex()],True, SPARQLUtils.labelFromURI(concept),progress)
        QgsApplication.taskManager().addTask(self.qlayerinstance)

    def instanceCount(self):
        curindex = self.currentProxyModel.mapToSource(self.currentContext.selectionModel().currentIndex())
        concept = self.currentContextModel.itemFromIndex(curindex).data(256)
        label = self.currentContextModel.itemFromIndex(curindex).text()
        if not label.endswith("]"):
            self.qtaskinstance = InstanceAmountQueryTask(
                "Getting instance count for " + str(concept),
                self.triplestoreconf[self.comboBox.currentIndex()]["endpoint"], self, self.currentContextModel.itemFromIndex(curindex),self.triplestoreconf[self.comboBox.currentIndex()])
            QgsApplication.taskManager().addTask(self.qtaskinstance)

    def instanceList(self):
        curindex = self.currentProxyModel.mapToSource(self.currentContext.selectionModel().currentIndex())
        concept = self.currentContextModel.itemFromIndex(curindex).data(256)
        alreadyloadedindicator = self.currentContextModel.itemFromIndex(curindex).data(259)
        if alreadyloadedindicator!=SPARQLUtils.instancesloadedindicator:
            self.qtaskinstanceList = InstanceListQueryTask(
                "Getting instance count for " + str(concept),
                self.triplestoreconf[self.comboBox.currentIndex()]["endpoint"], self, self.currentContextModel.itemFromIndex(curindex),self.triplestoreconf[self.comboBox.currentIndex()])
            QgsApplication.taskManager().addTask(self.qtaskinstanceList)

    def loadSubClasses(self):
        curindex = self.currentProxyModel.mapToSource(self.currentContext.selectionModel().currentIndex())
        concept = self.currentContextModel.itemFromIndex(curindex).data(256)
        if "subclassquery" in self.triplestoreconf[self.comboBox.currentIndex()]:
            if "wikidata" in self.triplestoreconf[self.comboBox.currentIndex()]["endpoint"]:
                query=self.triplestoreconf[self.comboBox.currentIndex()]["subclassquery"].replace("%%concept%%",str("wd:" + concept[concept.find('(')+1:-1]))
            else:
                query=self.triplestoreconf[self.comboBox.currentIndex()]["subclassquery"].replace("%%concept%%","<"+str(concept)+">")
            prefixestoadd=""
            for endpoint in self.triplestoreconf[self.comboBox.currentIndex()]["prefixes"]:
                    prefixestoadd += "PREFIX " + endpoint + ": <" + self.triplestoreconf[self.comboBox.currentIndex()]["prefixes"][
                        endpoint] + "> \n"
            self.qtasksub = SubClassQueryTask("Querying QGIS Layer from " + self.triplestoreconf[self.comboBox.currentIndex()]["endpoint"],
                                    self.triplestoreconf[self.comboBox.currentIndex()]["endpoint"],
                                    prefixestoadd + query,None,self,
                                    self.currentContextModel.itemFromIndex(curindex),concept,self.triplestoreconf[self.comboBox.currentIndex()])
            QgsApplication.taskManager().addTask(self.qtasksub)

    def subclassQuerySelectAction(self):
        endpointIndex = self.comboBox.currentIndex()
        if endpointIndex == 0:
            self.justloadingfromfile = False
            return
        curindex = self.currentProxyModel.mapToSource(self.currentContext.selectionModel().currentIndex())
        if self.currentContext.selectionModel().currentIndex() is not None and self.currentContextModel.itemFromIndex(
                curindex) is not None:
            concept = self.currentContextModel.itemFromIndex(curindex).data(256)
            querytext = self.triplestoreconf[endpointIndex]["querytemplate"][self.queryTemplates.currentIndex()][
            "query"].replace("?item a <%%concept%%>", "?item a ?con . ?con rdfs:subClassOf* <"+concept+"> ")
            self.inp_sparql2.setPlainText(querytext)
            self.inp_sparql2.columnvars = {}

    @staticmethod
    def copyClipBoard(item):
        concept = item.data(256)
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(concept, mode=cb.Clipboard)
