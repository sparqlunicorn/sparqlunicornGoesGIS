
from ...util.export.layer.layerexporter import LayerExporter
from qgis.utils import iface
from qgis.core import Qgis,QgsTask, QgsMessageLog
from qgis.PyQt.QtWidgets import QMessageBox
from rdflib import Graph, URIRef, RDF
from ...util.sparqlutils import SPARQLUtils

MESSAGE_CATEGORY = 'ExtractLayerTask'

class ExtractLayerTask(QgsTask):

    def __init__(self, description, graphname,toextract,triplestoreconf,resultfolder=".",prefixes=None, progress=None):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress = progress
        self.graphname = graphname
        self.prefixes=resultfolder
        self.triplestoreconf=triplestoreconf
        self.toextract=toextract


    def run(self):
        def run(self):
            try:
                g = Graph()
                g.parse(self.graphname, format="ttl")
                namespacetosub = {}
                for toex in self.toextract:
                    for sub in g.subjects(None, RDF.type, URIRef(toex)):
                        for predobj in sub.predicate_objects():

                        ns = SPARQLUtils.instanceToNS(sub)
                        if self.prefixes is not None and "reversed" in self.prefixes and ns in self.prefixes["reversed"]:
                            self.recognizedns.add(ns)
                        else:
                            self.namespaces.add(ns)
                        if ns not in namespacetosub:
                            namespacetosub[ns] = set()
                        namespacetosub[ns].add(sub)
                res = self.identifyDataClasses(g, namespacetosub)
                self.nstodataclass = res["nsd"]
                self.classset = res["clsset"]
                return True
            except Exception as e:
                self.exception = e
                return False
        return True

    def finished(self, result):
        self.progress.close()
        if result:
            iface.messageBar().pushMessage("Exported layer successfully to " + str(self.filename[0]) + "!", "OK",
                                           level=Qgis.Success)
            msgBox = QMessageBox()
            msgBox.setText("Layer converted to and saved as "+str(self.filename[0]))
            msgBox.exec()
        else:
            msgBox = QMessageBox()
            msgBox.setText("An error occurred while converting the layer converted to "+str(self.filename[0]))
            msgBox.exec()


