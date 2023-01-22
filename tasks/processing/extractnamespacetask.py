from qgis.core import QgsTask
from rdflib import Graph
from qgis.PyQt.QtGui import QIcon, QStandardItem
from qgis.PyQt.QtGui import QStandardItemModel

from ...util.sparqlutils import SPARQLUtils
from ...util.ui.uiutils import UIUtils
from ...dialogs.info.errormessagebox import ErrorMessageBox

MESSAGE_CATEGORY = 'ExtractNamespaceTask'

## Loads a graph from an RDF file either by providing an internet address or a file path.
class ExtractNamespaceTask(QgsTask):

    def __init__(self, description, graphname,resultcbox,prefixes=None, progress=None):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.prefixes=prefixes
        self.progress = progress
        self.graphname=graphname
        self.resultcbox=resultcbox
        self.namespaces=set()
        self.recognizedns=set()

    def run(self):
        try:
            g = Graph()
            g.parse(self.graphname, format="ttl")
            for sub in g.subjects(None,None,True):
                ns=SPARQLUtils.instanceToNS(sub)
                if self.prefixes!=None and "reversed" in self.prefixes and ns in self.prefixes["reversed"]:
                    self.recognizedns.add(ns)
                else:
                    self.namespaces.add(ns)
            return True
        except Exception as e:
            self.exception=e
            return False

    def finished(self, result):
        if result!=False:
            self.resultcbox.clear()
            model=QStandardItemModel()
            self.resultcbox.setModel(model)
            for ns in sorted(self.namespaces):
                if len(ns.strip())>0 and "http" in ns:
                    item = QStandardItem()
                    item.setData(ns, UIUtils.dataslot_conceptURI)
                    item.setText(ns)
                    item.setIcon(UIUtils.featurecollectionicon)
                    model.appendRow(item)
            for ns in sorted(self.recognizedns):
                if len(ns.strip())>0 and "http" in ns:
                    item = QStandardItem()
                    item.setData(ns, UIUtils.dataslot_conceptURI)
                    item.setText(ns)
                    item.setIcon(UIUtils.linkeddataicon)
                    model.appendRow(item)
            if self.progress!=None:
                self.progress.close()
        else:
            msgBox = ErrorMessageBox("Exception in ExtractNamespaceTask",str(self.exception))
            msgBox.exec()
