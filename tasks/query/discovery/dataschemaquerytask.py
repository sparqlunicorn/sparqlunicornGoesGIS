from collections.abc import Iterable

from ....util.ui.uiutils import UIUtils
from ....util.sparqlutils import SPARQLUtils
from qgis.core import QgsTask
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QStandardItem

MESSAGE_CATEGORY = 'DataSchemaQueryTask'

class DataSchemaQueryTask(QgsTask):
    """This shows how to subclass QgsTask"""

    def __init__(self, description, triplestoreurl, query, searchTerm,prefixes, searchResultModel,triplestoreconf, progress,dlg,styleprop=None,conceptstoenrich=None):
        super().__init__(description, QgsTask.CanCancel)
        #QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.query = query
        self.styleprop=styleprop
        self.dlg=dlg
        self.conceptstoenrich=conceptstoenrich
        self.progress = progress
        self.prefixes= prefixes
        self.invprefixes=SPARQLUtils.invertPrefixes(triplestoreconf["prefixes"])
        self.labels = None
        self.searchResultModel=searchResultModel
        self.triplestoreconf=triplestoreconf
        if self.progress!=None:
            newtext = "\n".join(self.progress.labelText().split("\n")[0:-1])
            self.progress.setLabelText(newtext + "\nCurrent Task: Executing query (1/2)")
        self.progress = progress
        self.urilist = None
        self.sortedatt = None
        self.searchTerm = searchTerm
        self.results = None

    def run(self):
        #QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        #QgsMessageLog.logMessage('Started task "{}"'.format(self.searchTerm), MESSAGE_CATEGORY, Qgis.Info)
        if self.searchTerm == "":
            return False
        whattoenrichquery="""SELECT (COUNT(distinct ?con) AS ?countcon) (COUNT(?rel) AS ?countrel) ?rel ?valtype
            WHERE { 
            ?con %%typeproperty%% %%concept%% .
            ?con ?rel ?val .
            BIND( datatype(?val) AS ?valtype ) }
            GROUP BY ?rel ?valtype
            ORDER BY DESC(?countrel)"""
        if self.conceptstoenrich!=None:
            cons="VALUES ?con {"
            for con in self.conceptstoenrich:
                cons+="<"+str(con)+"> "
            cons+="}\n"
            self.query=whattoenrichquery.replace("?con %%typeproperty%% %%concept%% .",cons)
        if isinstance(self.prefixes, Iterable):
            results = SPARQLUtils.executeQuery(self.triplestoreurl,"".join(self.prefixes) + self.query,self.triplestoreconf)
        else:
            results = SPARQLUtils.executeQuery(self.triplestoreurl, str(self.prefixes).replace("None","") + self.query,
                                                   self.triplestoreconf)
        if results == False or len(results["results"]["bindings"]) == 0:
            return False
        #self.searchResult.model().clear()
        if self.progress!=None:
            newtext = "\n".join(self.progress.labelText().split("\n")[0:-1])
            self.progress.setLabelText(newtext + "\nCurrent Task: Processing results (2/2)")
        maxcons = -1
        if "countcon" in results["results"]["bindings"][0]:
            maxcons=int(results["results"]["bindings"][0]["countcon"]["value"])
        self.sortedatt = {}
        for result in results["results"]["bindings"]:
            if maxcons!=0 and str(maxcons)!="0":
                if "countrel" in result:
                    self.sortedatt[result["rel"]["value"]] = {"amount": round(
                        (int(result["countrel"]["value"]) / maxcons) * 100, 2), "concept":result["rel"]["value"]}
                else:
                    self.sortedatt[result["rel"]["value"]] = {"concept": result["rel"]["value"]}
                if "valtype" in result and result["valtype"]["value"]!="":
                    self.sortedatt[result["rel"]["value"]]["valtype"]=result["valtype"]["value"]
        if "propertylabelquery" in self.triplestoreconf:
            self.sortedatt=SPARQLUtils.getLabelsForClasses(self.sortedatt, self.triplestoreconf["propertylabelquery"], self.triplestoreconf,
                                        self.triplestoreurl)
        else:
            self.sortedatt = SPARQLUtils.getLabelsForClasses(self.sortedatt,
                                                          None,
                                                          self.triplestoreconf,
                                                          self.triplestoreurl)
        return True

    def finished(self, result):
        while self.searchResultModel.rowCount()>0:
            self.searchResultModel.removeRow(0)
        if self.sortedatt != None:
            if len(self.sortedatt)==0:
                self.searchResultModel.insertRow(0)
                item = QStandardItem()
                item.setText("No results found")
                self.searchResultModel.setItem(0,0,item)
            else:
                UIUtils.fillAttributeTable(self.sortedatt, self.invprefixes, self.dlg, self.searchResultModel,
                                           SPARQLUtils.classnode,self.triplestoreconf,"Check this item if you want it to be queried",Qt.Checked)
        else:
            SPARQLUtils.handleException(MESSAGE_CATEGORY,"Dataschema search query not successful","The dataschema search query did not yield any results!")
        self.searchResultModel.setHeaderData(0, Qt.Horizontal, "Selection")
        self.searchResultModel.setHeaderData(1, Qt.Horizontal, "Attribute")
        self.searchResultModel.setHeaderData(2, Qt.Horizontal, "Sample Instances")
        self.progress.close()
        if self.conceptstoenrich!=None:
            self.dlg.propertyMatchingResultLabel.setText("<html><b>The following properties can be enriched for the "+str(len(self.conceptstoenrich))+" matched concepts</b></html>")
