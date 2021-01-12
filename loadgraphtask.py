from time import sleep
from rdflib import *
import json
import requests
import urllib
from qgis.PyQt.QtGui import QStandardItem
from qgis.PyQt.QtCore import QSettings
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
        s = QSettings() #getting proxy from qgis options settings
        self.proxyEnabled = s.value("proxy/proxyEnabled")
        self.proxyType = s.value("proxy/proxyType")
        self.proxyHost = s.value("proxy/proxyHost")
        self.proxyPort = s.value("proxy/proxyPort")
        self.proxyUser = s.value("proxy/proxyUser")
        self.proxyPassword = s.value("proxy/proxyPassword")

    def run(self):
        if self.proxyHost!=None and self.proxyHost!="" and self.proxyPort!=None and self.proxyPort!="":
            QgsMessageLog.logMessage('Proxy? '+str(self.proxyHost), MESSAGE_CATEGORY, Qgis.Info)
            proxy = urllib.request.ProxyHandler({'http': self.proxyHost})
            opener = urllib.request.build_opener(proxy)
            urllib.request.install_opener(opener)
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
            self.dlg.geoClassListModel.clear()
            self.dlg.comboBox.setCurrentIndex(0);
            self.maindlg.currentgraph=self.graph
            self.dlg.layercount.setText("["+str(len(self.geoconcepts))+"]")		
            for geo in self.geoconcepts:
                item=QStandardItem()
                item.setData(geo,1)
                item.setText(geo[geo.rfind('/')+1:])
                self.dlg.geoClassListModel.appendRow(item)
            #comp=QCompleter(self.dlg.layerconcepts)
            #comp.setCompletionMode(QCompleter.PopupCompletion)
            #comp.setModel(self.dlg.layerconcepts.model())
            #self.dlg.layerconcepts.setCompleter(comp)
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
