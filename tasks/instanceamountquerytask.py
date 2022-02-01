from ..util.sparqlutils import SPARQLUtils
from qgis.core import Qgis,QgsTask, QgsMessageLog

MESSAGE_CATEGORY = 'InstanceAmountQueryTask'

class InstanceAmountQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl,dlg,treeNode,triplestoreconf,nodetype):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.triplestoreconf=triplestoreconf
        self.nodetype=nodetype
        self.dlg=dlg
        self.treeNode=treeNode
        self.amount=-1

    def run(self):
        #QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        thequery=SPARQLUtils.queryPreProcessing("SELECT (COUNT(?con) as ?amount) WHERE { ?con %%typeproperty%% %%concept%% . }",self.triplestoreconf,str(
                self.treeNode.data(256)),self.nodetype==SPARQLUtils.collectionclassnode)
        results = SPARQLUtils.executeQuery(self.triplestoreurl,thequery,self.triplestoreconf)
        #QgsMessageLog.logMessage("Query results: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
        if results != False:
            self.amount = results["results"]["bindings"][0]["amount"]["value"]
        else:
            self.amount=0
        return True

    def finished(self, result):
        #QgsMessageLog.logMessage('Started task "{}"'.format(
        #    self.treeNode.text()+" ["+str(self.amount)+"]"), MESSAGE_CATEGORY, Qgis.Info)
        if self.amount!=-1:
            self.treeNode.setText(self.treeNode.text()+" ["+str(self.amount)+"]")
            self.treeNode.setData(str(self.amount),258)
