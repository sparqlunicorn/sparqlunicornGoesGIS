from ..util.sparqlutils import SPARQLUtils
from qgis.PyQt.QtGui import QStandardItem, QIcon
from qgis.core import Qgis
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog
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
        thequery=""
        if "wikidata" in self.triplestoreurl:
            wikicon=self.treeNode.data(256).split("(")[1].replace(" ","_").replace(")", "")
            QgsMessageLog.logMessage('Started task "{}"'.format(
                "WIKIDATA: SELECT ?con ?label WHERE { ?con http://www.wikidata.org/prop/direct/P31 http://www.wikidata.org/entity/" + str(
                    wikicon) + " . }"), MESSAGE_CATEGORY, Qgis.Info)
            thequery="SELECT ?con ?label WHERE { ?con <http://www.wikidata.org/prop/direct/P31> <http://www.wikidata.org/entity/" + str(
                    wikicon) + "> .  OPTIONAL { ?con rdfs:label ?label . } }"
        else:
            QgsMessageLog.logMessage('Started task "{}"'.format(
                "SELECT ?con ?label WHERE { ?con http://www.w3.org/1999/02/22-rdf-syntax-ns#type " + str(
                    self.treeNode.data(256)) + " . OPTIONAL { ?con rdfs:label ?label . } }"), MESSAGE_CATEGORY, Qgis.Info)
            thequery="SELECT ?con ?label WHERE { ?con <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <" + str(
                    self.treeNode.data(256)) + "> . OPTIONAL { ?con rdfs:label ?label . } }"
        if self.graph==None:
            results = SPARQLUtils.executeQuery(self.triplestoreurl,thequery,self.triplestoreconf)
        else:
            results=self.graph.query(thequery)
        #QgsMessageLog.logMessage("Query results: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
        for result in results["results"]["bindings"]:
            self.queryresult[result["con"]["value"]]={}
            if "label" in result:
                self.queryresult[result["con"]["value"]]["label"] = result["label"]["value"]
            else:
                self.queryresult[result["con"]["value"]]["label"]=SPARQLUtils.labelFromURI(result["con"]["value"])
        return True

    def finished(self, result):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.treeNode.text()), MESSAGE_CATEGORY, Qgis.Info)
        for concept in self.queryresult:
            item = QStandardItem()
            item.setData(concept, 256)
            if self.treeNode.data(257)=="GeoClass":
                item.setData("Instance",257)
                item.setIcon(QIcon(":/icons/resources/icons/earthinstance.png"))            
            else:
                item.setData("Instance",257)
                item.setIcon(QIcon(":/icons/resources/icons/instance.png"))
            item.setText(self.queryresult[concept]["label"])
            self.treeNode.appendRow(item)