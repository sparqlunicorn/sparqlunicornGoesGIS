from time import sleep
from rdflib import *
import json
import requests
from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QCompleter,QMessageBox
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
    )

MESSAGE_CATEGORY = 'LoadGraphTask'

## Loads a graph from an RDF file either by providing an internet address or a file path.
class LoadGraphTask(QgsTask):

    def __init__(self, description, filename, loadgraphdlg,dlg,maindlg, query,triplestoreconf,progress):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.progress=progress
        self.dlg=dlg
        self.maindlg=maindlg
        self.triplestoreconf=triplestoreconf
        self.loadgraphdlg=loadgraphdlg
        self.query=query
        self.graph=None
        self.geoconcepts=None
        self.exception=None
        self.filename=filename
        self.geojson=None

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()),MESSAGE_CATEGORY, Qgis.Info)
        self.graph = Graph()
        try:
            if self.filename.startswith("http"):
                self.graph.load(self.filename)
            else:
                filepath=self.filename.split(".")
                result = self.graph.parse(self.filename, format=filepath[len(filepath)-1])
        except Exception as e:
            QgsMessageLog.logMessage('Failed "{}"'.format(self.description()),MESSAGE_CATEGORY, Qgis.Info)
            self.exception=str(e)
            return False
        self.geoconcepts=[]
        if self.graph!=None:
            print("WE HAVE A GRAPH")
            results = self.graph.query(self.query)
            for row in results:
                self.geoconcepts.append(str(row[0]))
        return True


    def finished(self, result):
        if result==True:
            self.dlg.layerconcepts.clear()
            self.dlg.comboBox.setCurrentIndex(0);
            self.maindlg.currentgraph=self.graph
            self.dlg.layercount.setText("["+str(len(self.geoconcepts))+"]")		
            for geo in self.geoconcepts:
                self.dlg.layerconcepts.addItem(geo)
            comp=QCompleter(self.dlg.layerconcepts)
            comp.setCompletionMode(QCompleter.PopupCompletion)
            comp.setModel(self.dlg.layerconcepts.model())
            self.dlg.layerconcepts.setCompleter(comp)
            self.dlg.inp_sparql2.setPlainText(self.triplestoreconf[0]["querytemplate"][0]["query"].replace("%%concept%%",self.geoconcepts[0]))
            self.dlg.inp_sparql2.columnvars={}
            self.maindlg.loadedfromfile=True
            self.maindlg.justloadingfromfile=False
            self.loadgraphdlg.close()
        else:
            msgBox=QMessageBox()
            msgBox.setText(self.exception)
            msgBox.exec()
        self.progress.close()
