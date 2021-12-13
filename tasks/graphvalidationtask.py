from rdflib import *
from pyshacl import validate
from ..util.sparqlutils import SPARQLUtils
from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import (
    QgsTask, QgsMessageLog,
)

MESSAGE_CATEGORY = 'GraphValidationTask'


## Loads a graph from an RDF file either by providing an internet address or a file path.
class GraphValidationTask(QgsTask):

    def __init__(self, description, filename, ruleset, triplestoreconf, progress):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress = progress
        self.ruleset=ruleset
        self.triplestoreconf = triplestoreconf
        self.graph = None
        self.rulesetgraph= None
        self.geoconcepts = None
        self.exception = None
        self.errorlog=set()
        self.processinglog={}
        self.report=""
        self.errortypemap={}
        self.filename = filename

    def run(self):
        self.graph=SPARQLUtils.loadGraph(self.filename)
        self.rulesetgraph=SPARQLUtils.loadGraph(self.ruleset)
        self.processinglog["literals"] = {}
        self.processinglog["literals"]["geoliterals"] = {}
        self.processinglog["literals"]["geoliterals"]["amount"] = 0
        if self.graph != None:
            print("WE HAVE A GRAPH")
            for s, p, o in self.graph:
                QgsMessageLog.logMessage('BEFORE "{}"'.format(o), MESSAGE_CATEGORY, Qgis.Info)
                if isinstance(o, Literal):
                    QgsMessageLog.logMessage('ISLITERAL "{}"'.format(o) + " - " + str(o.datatype), MESSAGE_CATEGORY,
                                             Qgis.Info)
                    QgsMessageLog.logMessage(str(o.datatype), MESSAGE_CATEGORY, Qgis.Info)
                    if str(o.datatype) in SPARQLUtils.supportedLiteralTypes:
                        self.processinglog["literals"]["geoliterals"]["amount"]+=1
                        detected=SPARQLUtils.detectLiteralType(o.value)
                        if detected!=SPARQLUtils.supportedLiteralTypes[str(o.datatype)]:
                            #self.processinglog["literals"]["geoliterals"]["amount"] = self.processinglog["literals"]["geoliterals"]["amount"] + 1
                            self.errorlog.add("Error in triple: "+str(s)+" "+str(p)+" "+str(o)+":\n [ERR-LITTYPE]: Detected literal content "+str(detected)+" does not match claimed literal type "+str(o.datatype))
            if self.rulesetgraph!=None:
                self.report=validate(self.graph,self.rulesetgraph,None,None)
        return True

    def finished(self, result):
        self.progress.close()
        if self.errorlog==set():
            msgBox = QMessageBox()
            msgBox.setText("The graph validation task detected no errors!<br>Validation detected the following attributes:<ul><li>"+str(self.processinglog["literals"]["geoliterals"]["amount"])+" Geoliterals</li></ul>")
            msgBox.exec()
        else:
            msgBox = QMessageBox()
            msgBox.setText("The graph validation task detected "+str(len(self.errorlog))+"errors:\n"+("\n".join(self.errorlog))+" "+str(self.report))
            msgBox.exec()
