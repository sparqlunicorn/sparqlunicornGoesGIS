from ...dialogs.info.errormessagebox import ErrorMessageBox
from ...util.sparqlutils import SPARQLUtils
from ...util.graphutils import GraphUtils
from ...util.ui.uiutils import UIUtils
from qgis.core import QgsTask
from rdflib import Graph
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

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
        path = os.path.join(__location__, "../../tmp/graphcache/" + str(
            str(self.filenames).replace("/", "_").replace("['", "").replace("']", "").replace(
                "\\", "_").replace(":", "_")) + ".ttl")
        if isinstance(self.filenames,str):

            if os.path.isfile(path):
                self.graph.parse(path)
            else:
                self.graph=SPARQLUtils.loadGraph(self.filenames)
                self.graph.serialize(path, format="ttl")
        else:
            self.graph=Graph()
            for file in self.filenames:
                SPARQLUtils.loadGraph(file,self.graph)
            self.graph.serialize(path,format="ttl")
        self.geoconcepts = []
        if self.graph is not None:
            self.gutils.detectTripleStoreConfiguration(self.graphname, self.graph, self.detectnamespaces,
                                                       {"normal": {}, "reversed": {}}, self.progress)
            if "typeproperty" in self.gutils.missingproperties:
                self.gutils.configuration["typeproperty"]="http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
            if "subclassproperty" in self.gutils.missingproperties:
                self.gutils.configuration["subclassproperty"] = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
            #results = self.graph.query(self.query)
            #for row in results:
            #    self.geoconcepts.append(str(row[0]))
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
            msgBox = ErrorMessageBox("LoadGraph Error","")
            msgBox.setText(self.exception)
            msgBox.exec()
        self.progress.close()
