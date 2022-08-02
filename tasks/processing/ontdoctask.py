from ...util.doc.ontdocgeneration import OntDocGeneration
from ...util.sparqlutils import SPARQLUtils
from qgis.core import Qgis,QgsTask, QgsMessageLog
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsTask
from rdflib import Graph

MESSAGE_CATEGORY = 'OntDocTask'

class OntDocTask(QgsTask):

    def __init__(self, description, graphname, namespace,prefixes,license,labellang,outpath, progress):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress = progress
        self.prefixes=prefixes
        self.license=license
        self.labellang=labellang
        self.graphname=graphname
        self.namespace=namespace
        self.outpath=outpath

    def run(self):
        QgsMessageLog.logMessage("Graph "+str(self.graphname), "Ontdoctask", Qgis.Info)
        if isinstance(self.graphname,str):
            self.graph=SPARQLUtils.loadGraph(self.graphname)
        else:
            self.graph=Graph()
            for file in self.graphname:
                SPARQLUtils.loadGraph(file,self.graph)
        QgsMessageLog.logMessage("Graph "+str(self.graph), "Ontdoctask", Qgis.Info)
        nsshort=""
        if self.namespace in self.prefixes["reversed"]:
            nsshort=self.prefixes["reversed"][self.namespace]
        elif self.namespace.endswith("/"):
            nsshort=self.namespace[self.namespace[0:-1].rfind('/') + 1:]
        else:
            nsshort=self.namespace[self.namespace.rfind('/') + 1:]
        ontdoc=OntDocGeneration(self.prefixes, self.namespace, nsshort,self.license,self.labellang, self.outpath, self.graph)
        ontdoc.generateOntDocForNameSpace(self.namespace)
        return True

    def finished(self, result):
        self.progress.close()
        if result == True:
            msgBox = QMessageBox()
            msgBox.setText("Ontology documentation finished in folder "+str(self.outpath))
            msgBox.exec()
        else:
            msgBox = QMessageBox()
            msgBox.setText("Ontology documentation failed!")
            msgBox.exec()
