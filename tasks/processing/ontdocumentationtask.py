from util.sparqlutils import SPARQLUtils
from util.graphutils import GraphUtils
from util.ui.uiutils import UIUtils
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsTask
from rdflib import Graph

MESSAGE_CATEGORY = 'OntDocumentationTask'

class OntDocumentationTask(QgsTask):

    def __init__(self, description, graphname, namespace, progress):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress = progress
        self.graphname=graphname
        self.namespace=namespace

    def run(self):
        if isinstance(self.filenames,str):
            self.graph=SPARQLUtils.loadGraph(self.filenames)
        else:
            self.graph=Graph()
            for file in self.filenames:
                SPARQLUtils.loadGraph(file,self.graph)
        self.geoconcepts = []
        if self.graph != None:
            self.gutils.detectTripleStoreConfiguration(self.graphname, self.graph, self.detectnamespaces,
                                                       {"normal": {}, "reversed": {}}, self.progress)
            results = self.graph.query(self.query)
            for row in results:
                self.geoconcepts.append(str(row[0]))
            return True
        return False

    def finished(self, result):
        if result == True:
            self.maindlg.currentgraph = self.graph
            self.dlg.comboBox.addItem(UIUtils.rdffileicon, str(self.graphname)+" [File]")
            index = len(self.triplestoreconf)
            self.triplestoreconf.append({})
            self.triplestoreconf[index] = self.gutils.configuration
            self.triplestoreconf[index]["resource"]={"type":"file","instance":self.graph,"url":self.filenames}
            self.maindlg.loadedfromfile = True
            self.maindlg.justloadingfromfile = False
            if self.closedlg:
                self.loadgraphdlg.close()
        else:
            msgBox = QMessageBox()
            msgBox.setText(self.exception)
            msgBox.exec()
        self.progress.close()