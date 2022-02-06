from ..util.ui.uiutils import UIUtils
from ..util.sparqlutils import SPARQLUtils
from qgis.core import Qgis
from qgis.PyQt.QtGui import QStandardItem, QColor
from qgis.core import (
    QgsTask, QgsMessageLog
)

MESSAGE_CATEGORY = 'SubClassQueryTask'

class SubClassQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl, query, progress,dlg,treeNode,concept,triplestoreconf):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress=progress
        self.triplestoreurl = triplestoreurl
        self.query = query
        self.dlg=dlg
        self.con=concept
        self.treeNode=treeNode
        self.triplestoreconf=triplestoreconf
        self.amountoflabels = -1
        self.resultlist = {}

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        results = SPARQLUtils.executeQuery(self.triplestoreurl,self.query,self.triplestoreconf)
        if results==False:
            return False
        QgsMessageLog.logMessage('Started task "{}"'.format(results), MESSAGE_CATEGORY, Qgis.Info)
        for result in results["results"]["bindings"]:
            self.resultlist[str(result["subclass"]["value"])]={"concept":str(result["subclass"]["value"])}
        # self.layercount.setText("["+str(len(viewlist))+"]")
        if "classlabelquery" in self.triplestoreconf and self.triplestoreconf[
            "classlabelquery"] != "":
            self.resultlist = SPARQLUtils.getLabelsForClasses(self.resultlist, self.triplestoreconf["classlabelquery"],self.triplestoreconf,self.triplestoreurl)
            #print(labels)
            #self.amountoflabels = len(labels)
            #i = 0
            #sorted_labels = sorted(labels.items(), key=lambda x: x[1])
            #for lab in sorted_labels:
            #    self.resultlist.append(labels[lab[0]] + " (" + lab[0] + ")")
            #    i = i + 1
        return True

    def finished(self, result):
        for concept in self.resultlist:
            if self.resultlist[concept]!=self.con:
                item = QStandardItem()
                item.setData(concept, UIUtils.dataslot_conceptURI)
                if "label" in self.resultlist[concept]:
                    item.setText(self.resultlist[concept]["label"]+" ("+SPARQLUtils.labelFromURI(self.resultlist[concept])+")")
                else:
                    item.setText(SPARQLUtils.labelFromURI(self.resultlist[concept]))
                item.setForeground(QColor(0,0,0))
                item.setEditable(False)
                item.setIcon(UIUtils.classicon)
                item.setData(SPARQLUtils.classnode, UIUtils.dataslot_nodetype)
                self.treeNode.appendRow(item)
        if self.amountoflabels != -1:
            self.layercount.setText("[" + str(self.amountoflabels) + "]")
