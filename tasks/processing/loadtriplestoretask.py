from ...util.sparqlutils import SPARQLUtils
from rdflib import Graph
from qgis.core import Qgis,QgsTask, QgsMessageLog
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

MESSAGE_CATEGORY = 'LoadTripleStoreTask'

## Loads a graph from an RDF file either by providing an internet address or a file path.
class LoadTripleStoreTask(QgsTask):

    def __init__(self, description, curtriplestoreconf,dlg):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.curtriplestoreconf = curtriplestoreconf
        self.dlg=dlg

    def run(self):
        QgsMessageLog.logMessage('Started task: Serializing loaded graph to '.format(self.description()) + str(self.curtriplestoreconf["resource"]["url"]),
                                 MESSAGE_CATEGORY, Qgis.Info)
        if ("resource" in self.curtriplestoreconf and "url" in self.curtriplestoreconf["resource"]
                and "type" in self.curtriplestoreconf["resource"]
                and self.curtriplestoreconf["resource"]["type"]=="file"
                and "instance" not in self.curtriplestoreconf["resource"]):
            self.graph=Graph()
            path = os.path.join(__location__, "../../tmp/graphcache/" + str(
                str(self.curtriplestoreconf["resource"]["url"]).replace("/", "_").replace("['", "")
                .replace("']","").replace("\\", "_").replace(":", "_")) + ".ttl")
            if os.path.isfile(path):
                QgsMessageLog.logMessage('Started task: Loading graph from '.format(self.description()) + str(path),MESSAGE_CATEGORY, Qgis.Info)
                self.graph.parse(path)
                self.curtriplestoreconf["instance"]=self.graph
            else:
                SPARQLUtils.loadGraph(self.curtriplestoreconf["resource"]["url"],self.graph)
                self.curtriplestoreconf["instance"]=self.graph
                QgsMessageLog.logMessage('Started task: Serializing loaded graph to '.format(self.description())+str(path), MESSAGE_CATEGORY, Qgis.Info)
                self.graph.serialize(path, format="ttl")
            return True
        return False

    def finished(self, result):
        if result == True:
            self.dlg.endpointselectaction(True)
