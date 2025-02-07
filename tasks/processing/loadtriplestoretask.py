from ...util.sparqlutils import SPARQLUtils
from rdflib import Graph
from qgis.core import Qgis,QgsTask, QgsMessageLog
import os
import time

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

MESSAGE_CATEGORY = 'LoadTripleStoreTask'

CACHEDAYS=30

## Loads a graph from an RDF file either by providing an internet address or a file path.
class LoadTripleStoreTask(QgsTask):

    def __init__(self, description, curtriplestoreconf,endpointIndex,dlg):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.endpointIndex=endpointIndex
        self.curtriplestoreconf = curtriplestoreconf
        self.dlg=dlg
        self.graph = Graph()

    @staticmethod
    def is_file_older_than_x_days(path, days=1):
        modtime=os.path.getmtime(path)
        return ((time.time() - modtime) / 3600 > 24 * days)

    def run(self):
        #QgsMessageLog.logMessage('Started task: Serializing loaded graph to '.format(self.description()) + str(self.curtriplestoreconf["resource"]["url"]),
        #                         MESSAGE_CATEGORY, Qgis.Info)
        if ("resource" in self.curtriplestoreconf and "url" in self.curtriplestoreconf["resource"]
                and "type" in self.curtriplestoreconf["resource"]
                and self.curtriplestoreconf["resource"]["type"]=="file"
                and "instance" not in self.curtriplestoreconf["resource"]):
            path = os.path.join(__location__, "../../tmp/graphcache/" + str(
                str(self.curtriplestoreconf["resource"]["url"]).replace("/", "_").replace("['", "")
                .replace("']","").replace("\\", "_").replace(":", "_")) + ".ttl")
            if os.path.isfile(path) and not LoadTripleStoreTask.is_file_older_than_x_days(path,CACHEDAYS):
                QgsMessageLog.logMessage('FILE IS PRESENT AND NOT OLDER THAN '+str(CACHEDAYS),MESSAGE_CATEGORY, Qgis.Info)
                self.graph.parse(path)
                self.curtriplestoreconf["instance"]=self.graph
            else:
                QgsMessageLog.logMessage('FILE IS NOT PRESENT OR OLDER THAN '+str(CACHEDAYS),MESSAGE_CATEGORY, Qgis.Info)
                #QgsMessageLog.logMessage('Started task: Loading graph from URI '.format(self.description()) +self.curtriplestoreconf["resource"]["url"],
                #                         MESSAGE_CATEGORY, Qgis.Info)
                self.graph=SPARQLUtils.loadGraph(self.curtriplestoreconf["resource"]["url"])
                #QgsMessageLog.logMessage('Started task: Loaded graph from URI '.format(self.description()) + self.curtriplestoreconf["resource"]["url"],
                #                         MESSAGE_CATEGORY, Qgis.Info)
                self.curtriplestoreconf["instance"]=self.graph
                #QgsMessageLog.logMessage('Started task: Serializing loaded graph to '.format(self.description())+str(path), MESSAGE_CATEGORY, Qgis.Info)
                self.graph.serialize(path, format="ttl")
            return True
        return False

    def finished(self, result):
        if result == True:
            self.dlg.endpointselectaction(self.endpointIndex,True)
