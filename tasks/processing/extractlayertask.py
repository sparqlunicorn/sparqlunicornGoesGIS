from ...dialogs.info.errormessagebox import ErrorMessageBox
from ...util.export.layer.layerexporter import LayerExporter
from qgis.utils import iface
from qgis.core import Qgis,QgsTask, QgsMessageLog
from qgis.PyQt.QtWidgets import QMessageBox
from rdflib import Graph, URIRef, RDF
from ...util.sparqlutils import SPARQLUtils
from ...util.layerutils import LayerUtils
from qgis.core import QgsProject, QgsVectorLayer
import json

MESSAGE_CATEGORY = 'ExtractLayerTask'

class ExtractLayerTask(QgsTask):

    def __init__(self, description, graphname,toextract,triplestoreconf,prefixes=None, progress=None):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress = progress
        self.graphname = graphname
        self.prefixes=prefixes
        self.triplestoreconf=triplestoreconf
        self.toextract=toextract
        self.layers=[]
        QgsMessageLog.logMessage(str(self.toextract),
                                 MESSAGE_CATEGORY, Qgis.Info)
        QgsMessageLog.logMessage(str(self.graphname),
                                 MESSAGE_CATEGORY, Qgis.Info)


    def run(self):
        #try:
        g = Graph()
        g.parse(self.graphname, format="ttl")
        for toex in self.toextract:
            if "owl" not in str(toex) and "rdf" not in str(toex):
                #QgsMessageLog.logMessage(str(toex),MESSAGE_CATEGORY, Qgis.Info)
                layergraph = Graph()
                for sub in g.subjects(RDF.type, URIRef(toex),True):
                    QgsMessageLog.logMessage(str(sub),MESSAGE_CATEGORY, Qgis.Info)
                    for trip in g.triples((sub,None,None)):
                        layergraph.add(trip)
                res=LayerUtils.subGraphToLayer(layergraph,g,False, self.triplestoreconf, True, False)
                #QgsMessageLog.logMessage(str(res[0]), MESSAGE_CATEGORY, Qgis.Info)
                self.layers.append(QgsVectorLayer(json.dumps(res[0], sort_keys=True), "unicorn_" + str(SPARQLUtils.labelFromURI(str(toex))), "ogr"))
        return True
        #except Exception as e:
        #    self.exception = e
        #    QgsMessageLog.logMessage(str(e),
        #                             MESSAGE_CATEGORY, Qgis.Info)
        #    return False
        #return True

    def finished(self, result):
        if self.progress!=None:
            self.progress.close()
        if result:
            QgsMessageLog.logMessage(str(len(self.layers)),
                                     MESSAGE_CATEGORY, Qgis.Info)
            for layer in self.layers:
                QgsProject.instance().addMapLayer(layer)
            iface.messageBar().pushMessage("Successfully extracted layers from "+str(self.graphname)+"!", "OK",level=Qgis.Success)
            msgBox = QMessageBox()
            msgBox.setText("Layer extracted from "+str(self.graphname))
            msgBox.exec()
        else:
            msgBox = ErrorMessageBox("Layer Extraction Error","")
            msgBox.setText("An error occurred while extracting layers from  "+str(self.graphname))
            msgBox.exec()


