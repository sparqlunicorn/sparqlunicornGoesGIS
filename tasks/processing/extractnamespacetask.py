from qgis.core import QgsTask
from rdflib import Graph

MESSAGE_CATEGORY = 'LoadGraphTask'

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
                self.namespaces.add(str(sub)[0:str(sub).rfind("/") + 1])
            return True
        except:
            return False

    def finished(self, result):
        self.resultcbox.clear()
        self.resultcbox.addItems(sorted(self.namespaces))
        if self.progress!=None:
            self.progress.close()
