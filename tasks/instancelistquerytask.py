from ..util.sparqlutils import SPARQLUtils
from qgis.PyQt.QtGui import QStandardItem
from qgis.core import Qgis
from qgis.core import (
 QgsTask, QgsMessageLog
)

MESSAGE_CATEGORY = 'InstanceListQueryTask'

class InstanceListQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl,dlg,treeNode,triplestoreconf,graph=None):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.dlg=dlg
        self.graph=graph
        self.triplestoreconf=triplestoreconf
        self.treeNode=treeNode
        self.queryresult={}

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        typeproperty="http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        if "typeproperty" in self.triplestoreconf:
            typeproperty=self.triplestoreconf["typeproperty"]
        nodetype=self.treeNode.data(257)
        if nodetype==SPARQLUtils.collectionclassnode:
            QgsMessageLog.logMessage('Started task "{}"'.format(
                    "SELECT ?con ?label WHERE { " + str(
                        self.treeNode.data(256)) + "http://www.w3.org/2000/01/rdf-schema#member ?con . OPTIONAL { ?con rdfs:label ?label . } }"), MESSAGE_CATEGORY, Qgis.Info)
            thequery="SELECT ?con ?label WHERE {  <" + str(
                        self.treeNode.data(256)) + "> <http://www.w3.org/2000/01/rdf-schema#member> ?con . OPTIONAL { ?con rdfs:label ?label . } }"
        else:
            QgsMessageLog.logMessage('Started task "{}"'.format(
                "SELECT ?con ?label WHERE { ?con "+typeproperty+" " + str(
                        self.treeNode.data(256)) + " . OPTIONAL { ?con rdfs:label ?label . } }"), MESSAGE_CATEGORY, Qgis.Info)
            thequery="SELECT ?con ?label WHERE { ?con <"+typeproperty+"> <" + str(
                        self.treeNode.data(256)) + "> . OPTIONAL { ?con rdfs:label ?label . } }"
        if self.graph==None:
            results = SPARQLUtils.executeQuery(self.triplestoreurl,thequery,self.triplestoreconf)
        else:
            results=self.graph.query(thequery)
        #QgsMessageLog.logMessage("Query results: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
        for result in results["results"]["bindings"]:
            self.queryresult[result["con"]["value"]]={}
            if "label" in result:
                self.queryresult[result["con"]["value"]]["label"] = result["label"]["value"]+" ("+SPARQLUtils.labelFromURI(result["con"]["value"],self.triplestoreconf["prefixesrev"])+")"
            else:
                self.queryresult[result["con"]["value"]]["label"]=SPARQLUtils.labelFromURI(result["con"]["value"],self.triplestoreconf["prefixesrev"])
        return True

    def finished(self, result):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.treeNode.text()), MESSAGE_CATEGORY, Qgis.Info)
        if self.treeNode.data(258)==None:
            self.treeNode.setData(str(len(self.queryresult)),258)
            self.treeNode.setText(self.treeNode.text()+" ["+str(len(self.queryresult))+"]")
        self.treeNode.setData(SPARQLUtils.instancesloadedindicator,259)
        for concept in self.queryresult:
            item = QStandardItem()
            item.setData(concept, 256)
            item.setText(self.queryresult[concept]["label"])
            if self.treeNode.data(257)==SPARQLUtils.geoclassnode or self.treeNode.data(257)==SPARQLUtils.collectionclassnode:
                item.setData(SPARQLUtils.geoinstancenode,257)
                item.setIcon(SPARQLUtils.earthinstanceicon)
                item.setToolTip("GeoInstance " + str(item.text()) + ": <br>" + SPARQLUtils.treeNodeToolTip)
            else:
                item.setData(SPARQLUtils.instancenode,257)
                item.setIcon(SPARQLUtils.instanceicon)
                item.setToolTip("Instance " + str(item.text()) + ": <br>" + SPARQLUtils.treeNodeToolTip)
            self.treeNode.appendRow(item)
