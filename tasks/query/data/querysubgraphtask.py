from rdflib import Graph
from ....util.export.graphexporter import GraphExporter
from ....util.sparqlutils import SPARQLUtils
from qgis.core import Qgis,QgsTask, QgsMessageLog
from qgis.PyQt.QtWidgets import QFileDialog

MESSAGE_CATEGORY = 'QuerySubGraphTask'

class QuerySubGraphTask(QgsTask):
    """This shows how to subclass QgsTask"""

    def __init__(self, description,concept, triplestoreurl, query, triplestoreconf, progress=None,querydepth=0):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress = progress
        self.concept=concept
        self.querydepth=querydepth
        self.exception=None
        self.exportToFunction = {"CYPHER":GraphExporter.convertTTLToCypher,"GRAPHML": GraphExporter.convertTTLToGraphML, "GDF": GraphExporter.convertTTLToTGF,"GEXF": GraphExporter.convertTTLToGEXF, "TGF": GraphExporter.convertTTLToTGF,
                                 "TTL": GraphExporter.serializeRDF, "TRIG": GraphExporter.serializeRDF, "xml": GraphExporter.serializeRDF,
                                 "TRIX": GraphExporter.serializeRDF, "NT": GraphExporter.serializeRDF, "N3": GraphExporter.serializeRDF,
                                 "NQ": GraphExporter.serializeRDF}
        self.triplestoreurl = triplestoreurl
        self.triplestoreconf = triplestoreconf
        if self.progress!=None:
            newtext = "\n".join(self.progress.labelText().split("\n")[0:-1])
            self.progress.setLabelText(newtext + "\nCurrent Task: Query execution (1/2)")
        self.query = query

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.query.replace("<","_").replace(">","_")),
            MESSAGE_CATEGORY, Qgis.Info)
        self.results = SPARQLUtils.executeQuery(self.triplestoreurl,SPARQLUtils.selectQueryToConstructQuery(self.query),self.triplestoreconf)
        if self.results==False:
            self.exception=SPARQLUtils.exception
            return False
        else:
            g = Graph()
            g.parse(data=self.results, format="ttl")
            self.results=g
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.results),
            MESSAGE_CATEGORY, Qgis.Info)
        if self.progress!=None and self.results!=False:
            newtext = "\n".join(self.progress.labelText().split("\n")[0:-1])
            self.progress.setLabelText(newtext + "\nCurrent Task: Processing results (2/2)")
        return True

    def finished(self, result):
        QgsMessageLog.logMessage('Finishing up..... ',
                                 MESSAGE_CATEGORY, Qgis.Info)
        QgsMessageLog.logMessage(str(self.results),
                                 MESSAGE_CATEGORY, Qgis.Info)
        if self.progress!=None:
            self.progress.close()
        if self.exception!=None:
            SPARQLUtils.handleException(MESSAGE_CATEGORY)
            return
        filename = QFileDialog().getSaveFileName(None,"Save TTL result",self.concept+".ttl","Linked Data (*.n3 *.nt *.trig *.ttl *.xml) Graph Data (*.gdf *.gexf *.graphml *.tgf)")
        QgsMessageLog.logMessage(str(self.results),
                                 MESSAGE_CATEGORY, Qgis.Info)
        if filename:
            ex=filename[0][filename[0].rfind('.')+1:].upper()
            if ex in self.exportToFunction:
                if ex not in GraphExporter.rdfformats:
                    with open(filename[0], 'w', encoding='utf-8') as f:
                        self.exportToFunction[ex](self.results, f, None, ex)
                        f.close()
                else:
                    self.exportToFunction[ex](self.results, filename[0], None, ex)

