from util.layerutils import LayerUtils
from ..util.matchingtools import MatchingTools
from ..util.sparqlutils import SPARQLUtils
from qgis.core import Qgis,QgsTask, QgsMessageLog

MESSAGE_CATEGORY = 'InstanceAmountQueryTask'

class LayerMatchingTask(QgsTask):

    def __init__(self, description, triplestoreurl,matchproperty,matchlayer,matchcolumn,matchingmethod,dlg,treeNode,triplestoreconf):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.matchproperty=matchproperty
        self.matchlayer=matchlayer
        self.matchcolumn=matchcolumn
        self.matchingmethod=matchingmethod
        self.triplestoreurl = triplestoreurl
        self.triplestoreconf=triplestoreconf
        self.dlg=dlg
        self.treeNode=treeNode
        self.amount=-1

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        typeproperty="http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        thequery="SELECT ?val WHERE { ?con <"+typeproperty+"> <" + str(
                    self.treeNode.data(256)) + "> . ?con <"+self.matchproperty+"> ?val }"
        results = SPARQLUtils.executeQuery(self.triplestoreurl,thequery,self.triplestoreconf)
        #QgsMessageLog.logMessage("Query results: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
        resmap={}
        for result in results["results"]["bindings"]:
            if "val" in result:
                resmap[result["val"]["value"]]=True
        columnvallist=LayerUtils.getLayerColumnAsList(self.matchlayer,self.matchcolumn)
        matched={}
        matchcounter=0
        for value in columnvallist:
            if value in resmap:
                matched[value]=resmap[value]
                matchcounter+=1
        for value in columnvallist:
            if value not in matched:
                curmap=MatchingTools.matchStringMapToReference(resmap.keys(),value,self.matchingmethod)

        return True

    def finished(self, result):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.treeNode.text()+" ["+str(self.amount)+"]"), MESSAGE_CATEGORY, Qgis.Info)
        if self.amount!=-1:
            self.treeNode.setText(self.treeNode.text()+" ["+str(self.amount)+"]")
            self.treeNode.setData(str(self.amount),258)
