from ...util.ui.uiutils import UIUtils
from ...util.sparqlutils import SPARQLUtils
from qgis.core import QgsProject,QgsTask, QgsMessageLog

MESSAGE_CATEGORY="FindFeatureInAreaTask"
class FindFeaturesInAreaTask(QgsTask):

    def __init__(self, description, triplestoreurl,dlg,treeNode,triplestoreconf,nodetype):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.triplestoreconf=triplestoreconf
        self.nodetype=nodetype
        self.dlg=dlg
        self.treeNode=treeNode
        self.amount=-1
        self.thequery=SPARQLUtils.queryPreProcessing("SELECT (COUNT(?con) as ?amount) WHERE { ?con %%typeproperty%% %%concept%% . }",self.triplestoreconf,str(
                self.treeNode.data(256)),self.nodetype==SPARQLUtils.collectionclassnode,triplestoreurl["type"]=="file")

    def run(self):
        results = SPARQLUtils.executeQuery(self.triplestoreurl,self.thequery,self.triplestoreconf)
        if results != False:
            self.amount = results["results"]["bindings"][0]["amount"]["value"]
        else:
            self.amount=0
        SPARQLUtils.handleException(MESSAGE_CATEGORY)
        return True

    def finished(self, result):
        if self.amount!=-1:
            self.treeNode.setText(self.treeNode.text()+" ["+str(self.amount)+"]")
            self.treeNode.setData(str(self.amount),UIUtils.dataslot_instanceamount)