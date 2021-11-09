from ..util.sparqlutils import SPARQLUtils
from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QLabel
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog
)

MESSAGE_CATEGORY = 'DataSampleQueryTask'

class DataSampleQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl,dlg,concept,relation,column,row):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.dlg=dlg
        self.column=column
        self.row=row
        self.concept=concept
        self.relation=relation
        self.queryresult={}

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        QgsMessageLog.logMessage('Started task "{}"'.format(self.concept+" "+self.relation),MESSAGE_CATEGORY, Qgis.Info)
        if "wikidata" in self.triplestoreurl:
            wikicon=self.treeNode.data(256).split("(")[1].replace(" ","_").replace(")", "")
            QgsMessageLog.logMessage('Started task "{}"'.format(
                "WIKIDATA: SELECT DISTINCT (COUNT(?val) as ?amount) ?val  WHERE { ?con http://www.wikidata.org/prop/direct/P31 http://www.wikidata.org/entity/" + str(
                    wikicon) + " . ?con "+str(self.relation)+" ?val . }"), MESSAGE_CATEGORY, Qgis.Info)
            results = SPARQLUtils.executeQuery(self.triplestoreurl, "SELECT (COUNT(?val) as ?amount) ?val WHERE { ?con <http://www.wikidata.org/prop/direct/P31> <http://www.wikidata.org/entity/" + str(
                    wikicon) + "> . ?con "+str(self.relation)+" ?val . }")
        else:
            QgsMessageLog.logMessage('Started task "{}"'.format(
                "SELECT DISTINCT (COUNT(?val) as ?amount) ?val WHERE { ?con <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <" + str(self.concept) + "> . ?con <"+str(self.relation)+"> ?val } GROUP BY ?val LIMIT 100"), MESSAGE_CATEGORY, Qgis.Info)
            results = SPARQLUtils.executeQuery(self.triplestoreurl,"SELECT DISTINCT (COUNT(?val) as ?amount) ?val WHERE { ?con <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <" + str(self.concept) + "> . ?con <"+str(self.relation)+"> ?val } GROUP BY ?val LIMIT 100")
        for result in results["results"]["bindings"]:
            QgsMessageLog.logMessage('Started task "{}"'.format(result), MESSAGE_CATEGORY, Qgis.Info)
            self.queryresult[result["val"]["value"]]={}
            self.queryresult[result["val"]["value"]]["label"]=result["val"]["value"][result["val"]["value"].rfind('/') + 1:]
            self.queryresult[result["val"]["value"]]["amount"]=result["amount"]["value"]
            if "datatype" in result["val"]:
                self.queryresult[result["val"]["value"]]["datatype"]=result["val"]["datatype"]
        return True

    def finished(self,result):
        resstring=""
        counter=1
        for res in self.queryresult:
            if "http" in res:
                resstring+="<a href=\""+str(res)+"\"><b>"+str(self.queryresult[res]["label"])+" ["+str(self.queryresult[res]["amount"])+"]</b></a> "
            elif "datatype" in self.queryresult[res]:
                resstring+="<a href=\""+str(self.queryresult[res]["datatype"])+"\"><b>"+str(self.queryresult[res]["label"])+" ["+str(self.queryresult[res]["amount"])+"]</b></a> "
            else:
                resstring+="<b>"+str(self.queryresult[res]["label"])+" ["+str(self.queryresult[res]["amount"])+"]</b> "
            if counter%5==0:
                resstring+="<br/>"
            counter+=1
        item = QLabel()
        item.setOpenExternalLinks(True)
        item.setText(resstring)
        self.dlg.dataSchemaTableView.takeItem(self.row,self.column)
        self.dlg.dataSchemaTableView.setCellWidget(self.row,self.column,item)
