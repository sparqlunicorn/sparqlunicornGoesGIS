from rdflib import *
from ..util.sparqlutils import SPARQLUtils
from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QCompleter, QMessageBox
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
)

MESSAGE_CATEGORY = 'ValidateGraphTask'


## Loads a graph from an RDF file either by providing an internet address or a file path.
class ValidateGraphTask(QgsTask):

    def __init__(self, description, filename, loadgraphdlg, dlg, maindlg, query, triplestoreconf, progress, closedlg):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress = progress
        self.dlg = dlg
        self.maindlg = maindlg
        self.triplestoreconf = triplestoreconf
        self.loadgraphdlg = loadgraphdlg
        self.query = query
        self.graph = None
        self.geoconcepts = None
        self.closedlg = closedlg
        self.exception = None
        self.errorlog=set()
        self.filename = filename

    def run(self):
        self.graph=SPARQLUtils.loadGraph(self.filename)
        if self.graph != None:
            print("WE HAVE A GRAPH")
            for s, p, o in self.graph:
                QgsMessageLog.logMessage('BEFORE "{}"'.format(o), MESSAGE_CATEGORY, Qgis.Info)
                if isinstance(o, Literal):
                    QgsMessageLog.logMessage('ISLITERAL "{}"'.format(o) + " - " + str(o.datatype), MESSAGE_CATEGORY,
                                             Qgis.Info)
                    QgsMessageLog.logMessage(str(o.datatype), MESSAGE_CATEGORY, Qgis.Info)
                    if str(o.datatype) in SPARQLUtils.supportedLiteralTypes:
                        detected=SPARQLUtils.detectLiteralType()
                        if not detected!=SPARQLUtils.supportedLiteralTypes[str(o.datatype)]:
                            self.errorlog.add("Error in triple: "+str(s)+" "+str(p)+" "+str(o)+":\n [ERR-LITTYPE]: Detected literal content "+str(detected)+" does not match claimed literal type "+str(o.datatype))
        return True

    def finished(self, result):
        msgBox = QMessageBox()
        msgBox.setText("".join(self.errorlog))
        msgBox.exec()
