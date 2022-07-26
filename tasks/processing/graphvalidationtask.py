from rdflib import *
import os
from pyshacl import validate
from ...util.sparqlutils import SPARQLUtils
from qgis.core import Qgis,QgsTask, QgsMessageLog
from qgis.PyQt.QtWidgets import QMessageBox

MESSAGE_CATEGORY = 'GraphValidationTask'

rulesets={"GeoSPARQL 1.0 Validation":["../validation/geosparql10_validation.ttl"],"GeoSPARQL 1.1 Validation":["../validation/geosparql11_validation.ttl"],"GeoSPARQL Extended Ruleset Validation":["../validation/geosparql11ext_validation.ttl"]}
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

## Loads a graph from an RDF file either by providing an internet address or a file path.
class GraphValidationTask(QgsTask):

    def __init__(self, description, filenames, ruleset, triplestoreconf, progress,parent):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress = progress
        self.ruleset=ruleset
        self.parent=parent
        if self.ruleset in rulesets:
            self.ruleset=os.path.join(__location__, rulesets[self.ruleset][0])
        self.triplestoreconf = triplestoreconf
        self.graph = None
        self.rulesetgraph= None
        self.geoconcepts = None
        self.exception = None
        self.errorlog=set()
        self.processinglog={}
        self.report=""
        self.errortypemap={}
        self.filenames = filenames

    def run(self):
        if isinstance(self.filenames,str):
            self.graph=SPARQLUtils.loadGraph(self.filenames)
        else:
            self.graph=Graph()
            for file in self.filenames:
                SPARQLUtils.loadGraph(file,self.graph)
        self.rulesetgraph=SPARQLUtils.loadGraph(self.ruleset)
        self.processinglog["literals"] = {}
        self.processinglog["literals"]["geoliterals"] = {}
        self.processinglog["literals"]["geoliterals"]["amount"] = 0
        QgsMessageLog.logMessage("Ruleset: "+self.ruleset, MESSAGE_CATEGORY, Qgis.Info)
        QgsMessageLog.logMessage("Rulesetgraph: "+str(self.rulesetgraph), MESSAGE_CATEGORY, Qgis.Info)
        if self.graph != None:
            print("WE HAVE A GRAPH")
            for s, p, o in self.graph:
                #QgsMessageLog.logMessage('BEFORE "{}"'.format(o), MESSAGE_CATEGORY, Qgis.Info)
                if isinstance(o, Literal):
                    #QgsMessageLog.logMessage('ISLITERAL "{}"'.format(o) + " - " + str(o.datatype), MESSAGE_CATEGORY,
                    #                         Qgis.Info)
                    #QgsMessageLog.logMessage(str(o.datatype), MESSAGE_CATEGORY, Qgis.Info)
                    if str(o.datatype) in SPARQLUtils.supportedLiteralTypes:
                        self.processinglog["literals"]["geoliterals"]["amount"]+=1
                        detected=SPARQLUtils.detectGeoLiteralType(o.value)
                        if detected!=SPARQLUtils.supportedLiteralTypes[str(o.datatype)]:
                            #self.processinglog["literals"]["geoliterals"]["amount"] = self.processinglog["literals"]["geoliterals"]["amount"] + 1
                            self.errorlog.add("Error in triple: "+str(s)+" "+str(p)+" "+str(o)+":\n [ERR-LITTYPE]: Detected literal content "+str(detected)+" does not match claimed literal type "+str(o.datatype))
            if self.rulesetgraph!=None:
                self.report=validate(self.graph,self.rulesetgraph,None,None)
                QgsMessageLog.logMessage("Report: "+str(self.report), MESSAGE_CATEGORY, Qgis.Info)
        return True

    def finished(self, result):
        self.progress.close()
        if self.report!="":
            conforms, results_graph, results_text = self.report
            if self.errorlog==set():
                msgBox = QMessageBox()
                msgBox.setText("The graph validation task detected no errors!<br>Validation detected the following attributes:<ul><li>"+str(self.processinglog["literals"]["geoliterals"]["amount"])+" Geoliterals</li></ul>SHACL validation report: "+str(conforms)+"<br/>"+str(results_text))
                msgBox.exec()
            else:
                msgBox = QMessageBox()
                msgBox.setText("The graph validation task detected "+str(len(self.errorlog))+"errors:\n"+("\n".join(self.errorlog))+"\nSHACL validation report: "+str(conforms)+"\n"+str(results_text))
                msgBox.exec()
        else:
            if self.errorlog==set():
                msgBox = QMessageBox()
                msgBox.setText("The graph validation task detected no errors!<br>Validation detected the following attributes:<ul><li>"+str(self.processinglog["literals"]["geoliterals"]["amount"])+" Geoliterals</li></ul>")
                msgBox.exec()
            else:
                msgBox = QMessageBox()
                msgBox.setText("The graph validation task detected "+str(len(self.errorlog))+"errors:\n"+("\n".join(self.errorlog)))
                msgBox.exec()
        self.parent.close()