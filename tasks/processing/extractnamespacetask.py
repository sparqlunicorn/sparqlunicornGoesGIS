from qgis.core import QgsTask
from rdflib import Graph
from qgis.PyQt.QtWidgets import QMessageBox

from ...dialogs.info.errormessagebox import ErrorMessageBox
from ...util.sparqlutils import SPARQLUtils

MESSAGE_CATEGORY = 'ExtractNamespaceTask'

## Loads a graph from an RDF file either by providing an internet address or a file path.
class ExtractNamespaceTask(QgsTask):

    def __init__(self, description, graphname,resultcbox, progress=None):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress = progress
        self.graphname=graphname
        self.resultcbox=resultcbox
        self.namespaces=set()

    def run(self):
        try:
            g = Graph()
            g.parse(self.graphname, format="ttl")
            for sub in g.subjects():
                ns=str(sub)[0:str(sub).rfind("/") + 1]
                self.namespaces.add(ns)
            return True
        except Exception as e:
            self.exception=e
            return False

    def finished(self, result):
        if result!=False:
            self.resultcbox.clear()
            self.resultcbox.addItems(sorted(self.namespaces))
            if self.progress!=None:
                self.progress.close()
        else:
            msgBox = ErrorMessageBox("Exception in ExtractNamespaceTask",str(self.exception))
            msgBox.exec()
