from ...util.doc.ontdocgeneration import OntDocGeneration
from ...util.sparqlutils import SPARQLUtils
from ...util.graphutils import GraphUtils
from ...util.ui.uiutils import UIUtils
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsTask
from rdflib import Graph

MESSAGE_CATEGORY = 'OntDocTask'

class OntDocTask(QgsTask):

    def __init__(self, description, graphname, namespace,prefixes,outpath, progress):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress = progress
        self.prefixes=prefixes
        self.graphname=graphname
        self.namespace=namespace
        self.outpath=outpath

    def run(self):
        if isinstance(self.filenames,str):
            self.graph=SPARQLUtils.loadGraph(self.graphname)
        else:
            self.graph=Graph()
            for file in self.graphname:
                SPARQLUtils.loadGraph(file,self.graph)
        ontdoc=OntDocGeneration(self.prefixes, self.namespace, self.namespace[self.namespace.rfind('/')+1:], self.outpath, self.graph)
        ontdoc.generateOntDocForNameSpace(self.outpath,self.namespace)
        return True

    def finished(self, result):
        if result == True:
            msgBox = QMessageBox()
            msgBox.setText("Ontology documentation finished in folder "+str(self.outpath))
            msgBox.exec()
        else:
            msgBox = QMessageBox()
            msgBox.setText("Ontology documentation failed!")
            msgBox.exec()
        self.progress.close()