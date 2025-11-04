from collections import defaultdict

from qgis.core import QgsTask
from rdflib import Graph
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon, QStandardItem
from qgis.PyQt.QtGui import QStandardItemModel
from qgis.gui import QgsCheckableComboBox
from qgis.core import QgsMessageLog
from qgis.core import Qgis

from ...util.sparqlutils import SPARQLUtils
from ...util.ui.uiutils import UIUtils
from ...dialogs.info.errormessagebox import ErrorMessageBox

MESSAGE_CATEGORY = 'ExtractNamespaceTask'

## Loads a graph from an RDF file either by providing an internet address or a file path.
class ExtractNamespaceTask(QgsTask):

    def __init__(self, description, graphname,resultcbox,startConceptCBox,prefixes=None, progress=None):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.prefixes=prefixes
        self.progress = progress
        self.graphname=graphname
        self.resultcbox=resultcbox
        self.startConceptCBox=startConceptCBox
        self.namespaces=set()
        self.classset=None
        self.nstodataclass={}
        self.recognizedns=set()

    def run(self):
        try:
            g = Graph()
            g.parse(self.graphname, format="ttl")
            namespacetosub=defaultdict(set)
            for sub in g.subjects(None,None,True):
                ns=SPARQLUtils.instanceToNS(sub)
                if self.prefixes is not None and "reversed" in self.prefixes and ns in self.prefixes["reversed"]:
                    self.recognizedns.add(ns)
                else:
                    self.namespaces.add(ns)
                #if ns not in namespacetosub:
                #    namespacetosub[ns]=set()
                namespacetosub[ns].add(sub)
            res= self.identifyDataClasses(g, namespacetosub)
            self.nstodataclass=res["nsd"]
            self.classset=res["clsset"]
            return True
        except Exception as e:
            self.exception=e
            return False

    def identifyDataClasses(self,graph,namespacetosub):
        nstodataclass={}
        classset=set()
        #QgsMessageLog.logMessage(str(namespacetosub), MESSAGE_CATEGORY, Qgis.Info)
        for ns in namespacetosub:
            nstodataclass[ns] = 0
            for nssub in namespacetosub[ns]:
                nondataclasses,dataclasses = 0,0
                #QgsMessageLog.logMessage(str(nssub), MESSAGE_CATEGORY, Qgis.Info)
                for tup in graph.predicate_objects(nssub):
                    if str(tup[0])=="http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and (str(tup[1])=="http://www.w3.org/2000/01/rdf-schema#Class" or str(tup[1])=="http://www.w3.org/2002/07/owl#Class" or str(tup[1])=="http://www.w3.org/2002/07/owl#Ontology"):
                        nondataclasses+=1
                    elif str(tup[0])=="http://www.w3.org/2000/01/rdf-schema#subClassOf" or str(tup[0])=="http://www.w3.org/2000/01/rdf-schema#label":
                        nondataclasses+=1
                    else:
                        dataclasses+=1
                    if str(tup[0])=="http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                        classset.add(str(tup[1]))
                        #QgsMessageLog.logMessage(str(nssub)+" "+str(tup), MESSAGE_CATEGORY, Qgis.Info)
                #QgsMessageLog.logMessage(str(ns)+" "+str(dataclasses), MESSAGE_CATEGORY, Qgis.Info)
                nstodataclass[ns]+=dataclasses
        #QgsMessageLog.logMessage(str(nstodataclass), MESSAGE_CATEGORY, Qgis.Info)
        return {"nsd":nstodataclass,"clsset":classset}


    def finishedCheckableComboBox(self):
        for cls in sorted(self.classset):
            if "http" in str(cls):
                self.startConceptCBox.addItemWithCheckState(SPARQLUtils.labelFromURI(cls, self.prefixes),Qt.CheckState.Checked,str(cls))
    def finishedExtractNS(self):
        self.resultcbox.clear()
        model = QStandardItemModel()
        self.resultcbox.setModel(model)
        prefclassmodel = QStandardItemModel()
        self.startConceptCBox.setModel(prefclassmodel)
        item = QStandardItem()
        item.setData(None, UIUtils.dataslot_conceptURI)
        item.setIcon(UIUtils.removeicon)
        item.setText("No Start Concept")
        prefclassmodel.appendRow(item)
        for cls in sorted(self.classset):
            if "http" in str(cls):
                item = QStandardItem()
                item.setData(cls, UIUtils.dataslot_conceptURI)
                item.setIcon(UIUtils.classicon)
                item.setText(SPARQLUtils.labelFromURI(cls, self.prefixes))
                prefclassmodel.appendRow(item)
        for ns in sorted(self.namespaces):
            if len(ns.strip()) > 0 and "http" in ns:
                if ns in self.nstodataclass and self.nstodataclass[ns] > 0:
                    item = QStandardItem()
                    item.setData(ns, UIUtils.dataslot_conceptURI)
                    item.setIcon(UIUtils.featurecollectionicon)
                    item.setText(ns)
                    model.appendRow(item)
                else:
                    self.recognizedns.add(ns)
        for ns in sorted(self.recognizedns):
            if len(ns.strip()) > 0 and "http" in ns:
                item = QStandardItem()
                item.setData(ns, UIUtils.dataslot_conceptURI)
                item.setText(ns)
                item.setIcon(UIUtils.linkeddataicon)
                model.appendRow(item)

    def finished(self, result):
        if result!=False:
            if isinstance(self.startConceptCBox,QgsCheckableComboBox):
                self.finishedCheckableComboBox()
            else:
                self.finishedExtractNS()
            if self.progress is not None:
                self.progress.close()
        else:
            msgBox = ErrorMessageBox("Exception in ExtractNamespaceTask",str(self.exception))
            msgBox.exec()
