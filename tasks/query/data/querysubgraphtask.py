from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

from ....util.export.exporterutils import ExporterUtils
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
        self.results=None
        self.querydepth=querydepth
        self.exception=None
        self.triplestoreurl = triplestoreurl
        self.triplestoreconf = triplestoreconf
        if self.progress!=None:
            newtext = "\n".join(self.progress.labelText().split("\n")[0:-1])
            self.progress.setLabelText(newtext + "\nCurrent Task: Query execution (1/2)")
        self.query = query
        if triplestoreurl["type"]=="file":
            self.query=prepareQuery(self.query)


    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.query.replace("<","_").replace(">","_")),MESSAGE_CATEGORY, Qgis.Info)
        self.results = SPARQLUtils.executeQuery(self.triplestoreurl,SPARQLUtils.selectQueryToConstructQuery(self.query),self.triplestoreconf)
        if self.results==False:
            self.exception=SPARQLUtils.exception
            return False
        else:
            g = Graph()
            g.parse(data=self.results, format="ttl")
            self.results=g
        QgsMessageLog.logMessage('Started task "{}"'.format(self.results),MESSAGE_CATEGORY, Qgis.Info)
        if self.progress is not None and self.results!=False:
            newtext = "\n".join(self.progress.labelText().split("\n")[0:-1])
            self.progress.setLabelText(newtext + "\nCurrent Task: Processing results (2/2)")
        return True

    def finished(self, result):
        QgsMessageLog.logMessage('Finishing up..... ',MESSAGE_CATEGORY, Qgis.Info)
        QgsMessageLog.logMessage(str(self.results),MESSAGE_CATEGORY, Qgis.Info)
        if self.progress is not None:
            self.progress.close()
        if self.exception is not None:
            SPARQLUtils.handleException(MESSAGE_CATEGORY)
            return
        filename = QFileDialog().getSaveFileName(None,"Save TTL result",self.concept+".ttl",ExporterUtils.getExporterString())
        QgsMessageLog.logMessage(str(self.results),
                                 MESSAGE_CATEGORY, Qgis.Info)
        if filename:
            ex=filename[0][filename[0].rfind('.')+1:].upper()
            if ex in ExporterUtils.exportToFunction:
                if ex not in ExporterUtils.rdfformats:
                    with open(filename[0], 'w', encoding='utf-8') as f:
                        ExporterUtils.exportToFunction[ex](self.results, f, None,None, ex)
                else:
                    ExporterUtils.exportToFunction[ex](self.results, filename[0], None,None, ex)

