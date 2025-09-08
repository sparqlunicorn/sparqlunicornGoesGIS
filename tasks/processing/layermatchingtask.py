from ...util.ui.uiutils import UIUtils
from ...util.layerutils import LayerUtils
from ...util.matchingtools import MatchingTools
from ...util.sparqlutils import SPARQLUtils
from qgis.PyQt.QtGui import QStandardItem
from qgis.core import Qgis,QgsTask, QgsMessageLog

MESSAGE_CATEGORY = 'InstanceAmountQueryTask'

class LayerMatchingTask(QgsTask):

    def __init__(self, description, matchproperty,matchlayer,matchcolumn,matchingmethod,dlg,triplestoreconf,matchingtype,tablemodel,matchinglanguage):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.matchproperty=matchproperty
        self.matchlayer=matchlayer
        self.matchcolumn=matchcolumn
        self.matchingmethod=matchingmethod
        self.matchingtype=matchingtype
        self.matchinglanguage=matchinglanguage
        self.triplestoreurl = triplestoreconf["resource"]
        self.triplestoreconf=triplestoreconf
        self.tablemodel=tablemodel
        self.columnvallist=None
        self.dlg=dlg
        self.amount=-1
        self.resmap={}

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        typeproperty="http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        if "typeproperty" in self.triplestoreconf:
            typeproperty=self.triplestoreconf["typeproperty"]
        if self.matchproperty is None:
            self.matchproperty="http://www.w3.org/2000/01/rdf-schema#label"
        self.columnvallist = LayerUtils.getLayerColumnAsList(self.matchlayer, self.matchcolumn)
        if "Exact Matching" in self.matchingmethod or "1:1 Matching" in self.matchingmethod or "Regular Expression" in self.matchingmethod:
            thequery=f'SELECT ?con ?val WHERE {{ ?con <{typeproperty}> <{self.matchingtype}> . ?con <{self.matchproperty}> ?val . '
            matchvalstatement="VALUES ?val { "
            for val in self.columnvallist:
                if self.matchinglanguage is not None:
                    matchvalstatement += f'"{val}"@{self.matchinglanguage} '
                else:
                    matchvalstatement+=f'"{val}" '
            matchvalstatement+="}"
            thequery+=matchvalstatement+" }"
        else:
            thequery=f'SELECT ?con ?val WHERE {{ ?con <{typeproperty}> <{self.matchingtype}> . ?con <{self.matchproperty}> ?val . FILTER(lang(?val)="{self.matchinglanguage}") }}'
        results = SPARQLUtils.executeQuery(self.triplestoreurl,thequery,self.triplestoreconf)
        self.resmap={}
        for result in results["results"]["bindings"]:
            if "val" in result and "con" in result:
                self.resmap[result["val"]["value"]]={"con":str(result["con"]["value"]),"val":str(result["val"]["value"])}
        matched={}
        matchcounter=0
        for value in self.columnvallist:
            if value in self.resmap:
                matched[value]=self.resmap[value]
                matchcounter+=1
        for value in self.columnvallist:
            if value not in matched:
                curmap=MatchingTools.matchStringMapToReference(self.resmap.keys(),value,self.matchingmethod)

        return True

    def finished(self, result):
        counter=0
        while self.tablemodel.rowCount()>0:
            self.tablemodel.removeRow(0)
        if len(self.resmap)==0:
            self.tablemodel.insertRow(counter)
            itemchecked = QStandardItem()
            itemchecked.setText("No results found!")
            self.tablemodel.setItem(counter, 0, itemchecked)
            self.dlg.enrichmentSearchResultLabel.setText("<html><b>The matching task found no results for your selection</b></html>")
        else:
            for val in self.resmap:
                self.tablemodel.insertRow(counter)
                itemchecked = QStandardItem()
                itemchecked.setText(self.resmap[val]["con"])
                itemchecked.setIcon(UIUtils.instanceicon)
                self.tablemodel.setItem(counter, 0, itemchecked)
                itemchecked = QStandardItem()
                itemchecked.setText(self.resmap[val]["val"])
                itemchecked.setIcon(UIUtils.datatypepropertyicon)
                self.tablemodel.setItem(counter, 1, itemchecked)
                counter+=1
        if self.columnvallist is not None:
            self.dlg.enrichmentSearchResultLabel.setText(
                f"<html><b>The matching task found {len(self.resmap)} results for your selection. That is {round(((len(self.resmap)/len(self.columnvallist))*100),2)}% ({len(self.resmap)}/{len(self.columnvallist)}) of all instances in the original layer</html>")
        self.dlg.stackedWidget.setCurrentWidget(self.dlg.stackedWidget.widget(1))
        SPARQLUtils.handleException(MESSAGE_CATEGORY)
