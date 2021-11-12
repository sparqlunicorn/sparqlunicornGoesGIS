from ..util.sparqlutils import SPARQLUtils
from qgis.core import Qgis
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog
)

MESSAGE_CATEGORY = 'InstanceAmountQueryTask'

class InstanceAmountQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl,dlg,treeNode,graph=None):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.dlg=dlg
        self.graph=graph
        self.treeNode=treeNode
        self.amount=-1

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        thequery=""
        if "wikidata" in self.triplestoreurl:
            wikicon=self.treeNode.data(256).split("(")[1].replace(" ","_").replace(")", "")
            QgsMessageLog.logMessage('Started task "{}"'.format(
                "WIKIDATA: SELECT (COUNT(?con) as ?amount) WHERE { ?con http://www.wikidata.org/prop/direct/P31 http://www.wikidata.org/entity/" + str(
                    wikicon) + " . }"), MESSAGE_CATEGORY, Qgis.Info)
            thequery="SELECT ?con ?style WHERE { ?con geo:style ?style . "+"OPTIONAL { ?style geost:polygonStyle ?polygonStyle .} ?style  geost:fillOpacity }"
        else:
            QgsMessageLog.logMessage('Started task "{}"'.format(
                "SELECT (COUNT(?con) as ?amount) WHERE { ?con http://www.w3.org/1999/02/22-rdf-syntax-ns#type " + str(
                    self.treeNode.data(256)) + " . }"), MESSAGE_CATEGORY, Qgis.Info)
            thequery="SELECT ?con ?style WHERE { ?con geo:style ?style . }"
        if self.graph!=None:
            results = SPARQLUtils.executeQuery(self.triplestoreurl,thequery)
        else:
            results=self.graph.query(thequery)
        QgsMessageLog.logMessage("Query results: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
        if results != False:
            self.amount = results["results"]["bindings"][0]["amount"]["value"]
        else:
            self.amount=0
        return True

    def finished(self, result):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.treeNode.text()+" ["+str(self.amount)+"]"), MESSAGE_CATEGORY, Qgis.Info)
        if self.amount!=-1:
            self.treeNode.setText(self.treeNode.text()+" ["+str(self.amount)+"]")
