from ..util.sparqlutils import SPARQLUtils
from ..util.graphutils import GraphUtils
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import (QgsTask)
from rdflib import Graph

MESSAGE_CATEGORY = 'LoadGraphTask'

## Loads a graph from an RDF file either by providing an internet address or a file path.
class LoadGraphTask(QgsTask):

    def __init__(self, description, graphname, filenames, loadgraphdlg, dlg, maindlg, query, triplestoreconf, progress, closedlg):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress = progress
        self.graphname=graphname
        self.dlg = dlg
        self.maindlg = maindlg
        self.triplestoreconf = triplestoreconf
        self.loadgraphdlg = loadgraphdlg
        self.query = query
        self.graph = None
        self.geoconcepts = None
        self.closedlg = closedlg
        self.exception = None
        self.detectnamespaces=True
        self.filenames = filenames
        self.geojson = None
        self.gutils=GraphUtils("")

    def run(self):
        if isinstance(self.filenames,str):
            self.graph=SPARQLUtils.loadGraph(self.filenames)
        else:
            self.graph=Graph()
            for file in self.filenames:
                SPARQLUtils.loadGraph(file,self.graph)
        self.geoconcepts = []
        if self.graph != None:
            print("WE HAVE A GRAPH")
            self.gutils.detectTripleStoreConfiguration(self.graphname, self.graph, self.detectnamespaces,
                                                       {"normal": {}, "reversed": {}}, self.progress)
            results = self.graph.query(self.query)
            for row in results:
                self.geoconcepts.append(str(row[0]))
            return True
        return False

    def finished(self, result):
        if result == True:
            self.dlg.geoTreeViewModel.clear()
            self.maindlg.currentgraph = self.graph
            self.dlg.comboBox.addItem(str(self.graphname)+" [File]")
            index = len(self.triplestoreconf)
            self.triplestoreconf.append({})
            self.triplestoreconf[index] = self.gutils.configuration
            self.triplestoreconf[index]["endpoint"]=self.graph
            self.maindlg.loadedfromfile = True
            self.maindlg.justloadingfromfile = False
            if self.closedlg:
                self.loadgraphdlg.close()
        else:
            msgBox = QMessageBox()
            msgBox.setText(self.exception)
            msgBox.exec()
        self.progress.close()
