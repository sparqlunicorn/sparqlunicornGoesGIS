from ..util.sparqlutils import SPARQLUtils
from qgis.core import Qgis
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog
)

MESSAGE_CATEGORY = 'FindStyleQueryTask'

class FindStyleQueryTask(QgsTask):

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
                "SELECT ?con ?style WHERE { ?con geo:style ?style . }"), MESSAGE_CATEGORY, Qgis.Info)
            thequery="SELECT ?con ?style WHERE { ?con geo:style ?style . }"
        else:
            QgsMessageLog.logMessage('Started task "{}"'.format(
                "SELECT ?con ?style WHERE { ?con geo:style ?style . }"), MESSAGE_CATEGORY, Qgis.Info)
            thequery="SELECT ?con ?style WHERE { ?con geo:style ?style . }"
        if self.graph==None:
            results = SPARQLUtils.executeQuery(self.triplestoreurl,thequery)
        else:
            results=self.graph.query(thequery)
        QgsMessageLog.logMessage("Query results: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
        #if results != False:
        #    self.amount = results["results"]["bindings"][0]["amount"]["value"]
        #else:
        #    self.amount=0
        return True

    def finished(self, result):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.treeNode.text()+" ["+str(self.amount)+"]"), MESSAGE_CATEGORY, Qgis.Info)
        #if self.amount!=-1:
        #    self.treeNode.setText(self.treeNode.text()+" ["+str(self.amount)+"]")
