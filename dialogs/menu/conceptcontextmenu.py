
from qgis.PyQt.QtWidgets import QAbstractItemView, QMessageBox, QApplication, QMenu, QAction
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtCore import Qt, QUrl
from qgis.core import (
    QgsApplication, QgsMessageLog
)
from ...tasks.instanceamountquerytask import InstanceAmountQueryTask
from ...tasks.instancelistquerytask import InstanceListQueryTask
from ..dataschemadialog import DataSchemaDialog
from ..querylimitedinstancesdialog import QueryLimitedInstancesDialog
from ...util.sparqlutils import SPARQLUtils


class TabContextMenu:

    def createTabeContextMenu(self):
        print("here")

class ConceptContextMenu:

    @staticmethod
    def createListContextMenu(triplestoreconf,position,context,item,menu=None):
        if menu==None:
            menu = QMenu("Menu")
        actionclip = QAction("Copy IRI to clipboard")
        menu.addAction(actionclip)
        actionclip.triggered.connect(ConceptContextMenu.copyClipBoard)
        action = QAction("Open in Webbrowser")
        menu.addAction(action)
        action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(item.data(256))))
        return menu

    def createTreeContextMenu(self,triplestoreconf,position,context,item,menu=None):
        if menu==None:
            menu = QMenu("Menu", context)
        menu=ConceptContextMenu.createListContextMenu(triplestoreconf,position,context,item,menu)
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

    @staticmethod
    def copyClipBoard(item):
        concept = item.data(256)
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(concept, mode=cb.Clipboard)