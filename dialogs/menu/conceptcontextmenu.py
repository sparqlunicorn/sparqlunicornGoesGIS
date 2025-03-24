from qgis.PyQt.QtWidgets import QApplication, QMenu, QAction
from qgis.PyQt.QtGui import QDesktopServices
from qgis.core import (
    QgsApplication
)
from qgis.PyQt.QtCore import QUrl

from ..dataview.graphrelationviewdialog import GraphRelationViewDialog
from ..tool.advancedquerydialog import AdvancedQueryDialog
from ...dialogs.util.bboxdialog import BBOXDialog
from ...util.ui.uiutils import UIUtils
from ...tasks.query.data.querylayertask import QueryLayerTask
from ..dataview.instancedatadialog import InstanceDataDialog
from ...tasks.query.discovery.subclassquerytask import SubClassQueryTask
from ...tasks.query.instance.instanceamountquerytask import InstanceAmountQueryTask
from ...tasks.query.instance.instancelistquerytask import InstanceListQueryTask
from ..dataview.dataschemadialog import DataSchemaDialog
from ..util.querylimitedinstancesdialog import QueryLimitedInstancesDialog
from ...util.sparqlutils import SPARQLUtils

MESSAGE_CATEGORY = 'ContextMenu'

class ConceptContextMenu(QMenu):

    def __init__(self,dlg,triplestoreconf,prefixes,position,context,item,preferredlang=None,menu=None):
        super(ConceptContextMenu, self).__init__()
        self.triplestoreconf=triplestoreconf
        self.dlg=dlg
        self.preferredlang=preferredlang
        self.item=item
        self.prefixes=prefixes
        if menu is None:
            menu = QMenu("Menu", context)
        actionclip = QAction("Copy IRI to clipboard")
        if item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.instancenode or item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.geoinstancenode:
            actionclip.setIcon(UIUtils.instancelinkicon)
        elif item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.classnode or item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.geoclassnode:
            actionclip.setIcon(UIUtils.classlinkicon)
        elif item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.linkedgeoclassnode:
            actionclip.setIcon(UIUtils.linkedgeoclassicon)
        elif item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.linkedgeoinstancenode:
            actionclip.setIcon(UIUtils.linkedgeoinstanceicon)
        elif item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.collectionclassnode:
            actionclip.setIcon(UIUtils.featurecollectionlinkicon)
        menu.addAction(actionclip)
        actionclip.triggered.connect(lambda: ConceptContextMenu.copyClipBoard(item))
        action = QAction("Open in Webbrowser")
        action.setIcon(UIUtils.geoclassicon)
        menu.addAction(action)
        action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(item.data(UIUtils.dataslot_conceptURI))))
        if item.data(UIUtils.dataslot_nodetype) != SPARQLUtils.instancenode and item.data(UIUtils.dataslot_nodetype) != SPARQLUtils.geoinstancenode\
                and item.data(UIUtils.dataslot_nodetype) != SPARQLUtils.linkedgeoinstancenode:
            actioninstancecount = QAction("Check instance count")
            actioninstancecount.setIcon(UIUtils.countinstancesicon)
            menu.addAction(actioninstancecount)
            actioninstancecount.triggered.connect(self.instanceCount)
            actiondataschema = QAction("Query data schema")
            if item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.classnode:
                actiondataschema.setIcon(UIUtils.classschemaicon)
            elif item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.collectionclassnode:
                actiondataschema.setIcon(UIUtils.featurecollectionschemaicon)
            elif item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.linkedgeoclassnode:
                actiondataschema.setIcon(UIUtils.linkedgeoclassschemaicon)
            else:
                actiondataschema.setIcon(UIUtils.geoclassschemaicon)
            menu.addAction(actiondataschema)
            actiondataschema.triggered.connect(lambda: DataSchemaDialog(
                item.data(UIUtils.dataslot_conceptURI),
                item.data(UIUtils.dataslot_nodetype),
                item.text(),
                triplestoreconf["resource"],
                triplestoreconf, self.prefixes,
                "Data Schema View for " + SPARQLUtils.labelFromURI(str(item.data(UIUtils.dataslot_conceptURI)),
                                                                   triplestoreconf["prefixesrev"])
            ))
            actionrelgeo = QAction("Check related concepts")
            actionrelgeo.setIcon(UIUtils.countinstancesicon)
            menu.addAction(actionrelgeo)
            actionAdvancedQuery = QAction("Advanced Query")
            actionAdvancedQuery.setIcon(UIUtils.addfeaturecollectionicon)
            actionAdvancedQuery.triggered.connect(self.advancedQueryDialog)
            actionAdvancedQuery.setVisible(False)
            menu.addAction(actionAdvancedQuery)
            actionrelgeo.triggered.connect(self.relatedGeoConcepts)
            actionqueryinstances = QAction("Query all instances")
            actionqueryinstances.setIcon(UIUtils.queryinstancesicon)
            menu.addAction(actionqueryinstances)
            actionqueryinstances.triggered.connect(self.instanceList)
            if "subclassquery" in triplestoreconf:
                action2 = QAction("Load subclasses")
                action2.setIcon(UIUtils.subclassicon)
                menu.addAction(action2)
                action2.triggered.connect(self.loadSubClasses)
            #actionsubclassquery = QAction("Create subclass query")
            #actionsubclassquery.setIcon(UIUtils.subclassicon)
            #menu.addAction(actionsubclassquery)
            #actionsubclassquery.triggered.connect(self.dlg.subclassQuerySelectAction)
            actionquerysomeinstances = QAction("Add some instances as new layer")
            actionquerysomeinstances.setIcon(UIUtils.addfeaturecollectionicon)
            menu.addAction(actionquerysomeinstances)
            actionquerysomeinstances.triggered.connect(self.queryLimitedInstances)
            actionaddallInstancesAsLayer = QAction("Add all instances as new layer")
            actionaddallInstancesAsLayer.setIcon(UIUtils.addfeaturecollectionicon)
            menu.addAction(actionaddallInstancesAsLayer)
            actionaddallInstancesAsLayer.triggered.connect(lambda: self.dlg.dataAllInstancesAsLayer(False,None))
            actionallInstancesAsRDF = QAction("Instances as graph data")
            actionallInstancesAsRDF.setIcon(UIUtils.addfeaturecollectionicon)
            menu.addAction(actionallInstancesAsRDF)
            actionallInstancesAsRDF.triggered.connect(lambda: self.dlg.dataAllInstancesAsLayer(True,None))
        else:
            actiondataschemainstance = QAction("Query data")
            if item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.instancenode:
                actiondataschemainstance.setIcon(UIUtils.instanceicon)
            elif item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.geoinstancenode:
                actiondataschemainstance.setIcon(UIUtils.geoinstanceicon)
            elif item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.linkedgeoinstancenode:
                actiondataschemainstance.setIcon(UIUtils.linkedgeoinstanceicon)
            menu.addAction(actiondataschemainstance)
            actiondataschemainstance.triggered.connect(self.dataInstanceView)
            actionaddInstanceAsLayer = QAction("Add instance as new layer")
            if item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.instancenode:
                actionaddInstanceAsLayer.setIcon(UIUtils.addinstanceicon)
            elif item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.geoinstancenode:
                actionaddInstanceAsLayer.setIcon(UIUtils.addgeoinstanceicon)
            elif item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.linkedgeoinstancenode:
                actionaddInstanceAsLayer.setIcon(UIUtils.addinstanceicon)
            menu.addAction(actionaddInstanceAsLayer)
            actionaddInstanceAsLayer.triggered.connect(self.dlg.dataInstanceAsLayer)
            actionallInstanceAsRDF = QAction("Instance as graph data")
            actionallInstanceAsRDF.setIcon(UIUtils.addfeaturecollectionicon)
            menu.addAction(actionallInstanceAsRDF)
            actionallInstanceAsRDF.triggered.connect(lambda: self.dlg.dataAllInstancesAsLayer(True,None))
        if item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.linkedgeoclassnode or item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.geoclassnode:
            actionquerybbox=QAction("Query layer in bbox")
            actionquerybbox.setIcon(UIUtils.bboxicon)
            actionquerybbox.triggered.connect(self.getBBOX)
            menu.addAction(actionquerybbox)
        if item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.linkedgeoclassnode:
            actionquerylinkedgeoconcept = QAction("Query joined layer with linked geoconcept")
            actionquerylinkedgeoconcept.setIcon(UIUtils.linkedgeoclassicon)
            menu.addAction(actionquerylinkedgeoconcept)
            actionquerylinkedgeoconcept.triggered.connect(self.queryLinkedGeoConcept)
        elif item.data(UIUtils.dataslot_nodetype) == SPARQLUtils.linkedgeoinstancenode:
            actionquerylinkedgeoinstance = QAction("Query joined layer with linked geoinstance")
            actionquerylinkedgeoinstance.setIcon(UIUtils.linkedgeoinstanceicon)
            menu.addAction(actionquerylinkedgeoinstance)
            actionquerylinkedgeoinstance.triggered.connect(self.queryLinkedGeoInstance)
        #actionapplicablestyles = QAction("Find applicable styles")
        #menu.addAction(actionapplicablestyles)
        #actionapplicablestyles.triggered.connect(self.appStyles)
        menu.exec(context.viewport().mapToGlobal(position))

    @staticmethod
    def createListContextMenu(item,menu=None):
        if menu is None:
            menu = QMenu("Menu")
        actionclip = QAction("Copy IRI to clipboard")
        menu.addAction(actionclip)
        actionclip.triggered.connect(lambda: ConceptContextMenu.copyClipBoard(item))
        action = QAction("Open in Webbrowser")
        menu.addAction(action)
        action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl(item.data(UIUtils.dataslot_conceptURI))))
        return menu

    def getBBOX(self):
        bboxdia=BBOXDialog(None,self.triplestoreconf)
        if bboxdia.exec():
            bboxcon=bboxdia.curquery
            self.dlg.dataAllInstancesAsLayer(False,bboxcon)

    def queryLimitedInstances(self):
        concept = self.item.data(UIUtils.dataslot_conceptURI)
        nodetype = self.item.data(UIUtils.dataslot_nodetype)
        dia= QueryLimitedInstancesDialog(self.triplestoreconf,concept,nodetype)
        if dia.exec_():
            if dia.thequery is not None:
                self.qlayerinstance = QueryLayerTask(
                    "All Instances to Layer: " + str(concept),
                    concept,
                    self.triplestoreconf["resource"],
                    dia.thequery,
                    self.triplestoreconf, True, SPARQLUtils.labelFromURI(concept), None)
                QgsApplication.taskManager().addTask(self.qlayerinstance)


    def appStyles(self):
        curindex = self.currentProxyModel.mapToSource(self.currentContext.selectionModel().currentIndex())
        concept = self.currentContextModel.itemFromIndex(curindex).data(UIUtils.dataslot_conceptURI)
        label = self.currentContextModel.itemFromIndex(curindex).text()
        # self.dataschemaDialog = DataSchemaDialog(concept,label,self.triplestoreconf["resource"],self.triplestoreconf,self.prefixes,self.comboBox.currentIndex())
        # self.dataschemaDialog.setWindowTitle("Data Schema View for "+str(concept))
        # self.dataschemaDialog.exec_()

    def dataInstanceView(self):
        concept = self.item.data(UIUtils.dataslot_conceptURI)
        nodetype = self.item.data(UIUtils.dataslot_nodetype)
        label = self.item.text()
        self.instancedataDialog = InstanceDataDialog(concept,nodetype,label,self.triplestoreconf["resource"],self.triplestoreconf,self.prefixes)
        self.instancedataDialog.setWindowTitle("Data Instance View for "+SPARQLUtils.labelFromURI(str(concept),self.triplestoreconf["prefixesrev"]))
        #self.instancedataDialog.exec_()

    def queryLinkedGeoConcept(self):
        concept = self.item.data(UIUtils.dataslot_conceptURI)
        nodetype = self.item.data(UIUtils.dataslot_nodetype)
        linkedproperty=self.item.data(UIUtils.dataslot_linkedconceptrel)
        label = self.item.text()
        typeproperty="http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        if "typeproperty" in self.triplestoreconf:
            typeproperty=self.triplestoreconf["typeproperty"]
        self.qlayerinstance = QueryLayerTask(
            "Linked GeoClass to Layer: " + str(concept),
            concept,
            self.triplestoreconf["resource"],
            "SELECT ?"+str(" ?".join(self.triplestoreconf["mandatoryvariables"]))+" ?item2 ?rel ?val ?rel2 ?val2 \n WHERE\n {\n ?item <"+str(typeproperty)+"> <"+str(concept)+"> . \n ?item ?rel ?val .\n ?item <"+str(linkedproperty)+"> ?item2 .\n ?item2 ?rel2 ?val2 .\n "+str(self.triplestoreconf["geotriplepattern"][0]).replace("?item","?item2")+" \n } ORDER BY ?item",
            self.triplestoreconf, True, SPARQLUtils.labelFromURI(concept), None,0,True,None)
        QgsApplication.taskManager().addTask(self.qlayerinstance)

    def queryLinkedGeoInstance(self):
        concept = self.item.data(UIUtils.dataslot_conceptURI)
        linkedproperty=self.item.data(UIUtils.dataslot_linkedconceptrel)
        thequery="SELECT ?"+str(" ?".join(self.triplestoreconf["mandatoryvariables"]))
        thequery=thequery.replace("?item", "")
        self.qlayerinstance = QueryLayerTask(
            "Linked Geo Instance to Layer: " + str(concept),
            concept,
            self.triplestoreconf["resource"],
            thequery+" ?item2 ?rel ?val ?rel2 ?val2 \n WHERE\n {\n <"+str(concept)+"> ?rel ?val .\n <"+str(concept)+"> <"+str(linkedproperty)+"> ?item2 .\n ?item2 ?rel2 ?val2 .\n "+str(self.triplestoreconf["geotriplepattern"][0]).replace("?item","?item2")+" \n }",
            self.triplestoreconf, True, SPARQLUtils.labelFromURI(concept), None,0,True,None)
        QgsApplication.taskManager().addTask(self.qlayerinstance)

    def advancedQueryDialog(self):
        concept = self.item.data(UIUtils.dataslot_conceptURI)
        label = self.item.text()
        AdvancedQueryDialog(self.triplestoreconf,concept,label)

    def relatedGeoConcepts(self):
        concept = self.item.data(UIUtils.dataslot_conceptURI)
        label = self.item.text()
        GraphRelationViewDialog(self.triplestoreconf,concept,label)
        #if not label.endswith("]"):
        #    self.qtaskinstance = FindRelatedConceptQueryTask(
        #        "Getting related geo concepts for " + str(concept),
        #        self.triplestoreconf["resource"], self, concept,self.triplestoreconf)
        #    QgsApplication.taskManager().addTask(self.qtaskinstance)

    def instanceCount(self):
        concept = self.item.data(UIUtils.dataslot_conceptURI)
        nodetype = self.item.data(UIUtils.dataslot_nodetype)
        amount=self.item.data(UIUtils.dataslot_instanceamount)
        if amount is None:
            self.qtaskinstance = InstanceAmountQueryTask(
                "Getting instance count for " + str(concept),
                self.triplestoreconf["resource"], self, self.item,self.triplestoreconf,nodetype)
            QgsApplication.taskManager().addTask(self.qtaskinstance)

    def instanceList(self):
        concept = self.item.data(UIUtils.dataslot_conceptURI)
        nodetype = self.item.data(UIUtils.dataslot_nodetype)
        alreadyloadedindicator = self.item.data(UIUtils.dataslot_instancesloaded)
        amount=self.item.data(UIUtils.dataslot_instanceamount)
        if alreadyloadedindicator!=SPARQLUtils.instancesloadedindicator:
            if amount is None:
                self.qtaskinstance = InstanceAmountQueryTask(
                    "Getting instance count for " + str(concept),
                    self.triplestoreconf["resource"], self, self.item, self.triplestoreconf, nodetype)
                QgsApplication.taskManager().addTask(self.qtaskinstance)
            self.qtaskinstanceList = InstanceListQueryTask(
                "Getting instance count for " + str(concept),
                self.triplestoreconf["resource"], self, self.item,self.triplestoreconf)
            QgsApplication.taskManager().addTask(self.qtaskinstanceList)

    def loadSubClasses(self):
        concept = self.item.data(UIUtils.dataslot_conceptURI)
        if "subclassquery" in self.triplestoreconf:
            subclassproperty="http://www.w3.org/2000/01/rdf-schema#subClassOf"
            if "subclassproperty" in self.triplestoreconf:
                subclassproperty=self.triplestoreconf["subclassproperty"]
            if "wikidata" in self.triplestoreconf["resource"]:
                query=self.triplestoreconf["subclassquery"].replace("%%concept%%",str("wd:" + concept[concept.find('(')+1:-1])).replace("%%subclassproperty%%",str(subclassproperty))
            else:
                query=self.triplestoreconf["subclassquery"].replace("%%concept%%","<"+str(concept)+">").replace("%%subclassproperty%%",str(subclassproperty))
            prefixestoadd=""
            for endpoint in self.triplestoreconf["prefixes"]:
                    prefixestoadd += "PREFIX " + endpoint + ": <" + self.triplestoreconf["prefixes"][endpoint] + "> \n"
            self.qtasksub = SubClassQueryTask("Querying subclasses of " + str(concept),
                                    self.triplestoreconf["resource"],
                                    prefixestoadd + query,None,self,
                                    self.item,concept,self.triplestoreconf)
            QgsApplication.taskManager().addTask(self.qtasksub)

    @staticmethod
    def copyClipBoard(item):
        concept = item.data(UIUtils.dataslot_conceptURI)
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(concept, mode=cb.Clipboard)
