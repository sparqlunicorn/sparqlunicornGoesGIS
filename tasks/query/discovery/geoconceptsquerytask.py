from ....util.ui.uiutils import UIUtils
from ....util.sparqlutils import SPARQLUtils
from ....util.conf.configutils import ConfigUtils
from qgis.PyQt.QtGui import QStandardItem,QColor
from qgis.PyQt.QtWidgets import QHeaderView
from qgis.core import Qgis,QgsTask, QgsMessageLog
import os
from os.path import exists
import json
from rdflib.plugins.sparql import prepareQuery

MESSAGE_CATEGORY = 'GeoConceptsQueryTask'

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

class GeoConceptsQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl, query, triplestoreconf, sparql, queryvar, getlabels, layercount,
                 geoClassList, examplequery, geoClassListGui, completerClassList, dlg,preferredlang="en"):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.triplestoreconf = triplestoreconf
        self.dlg = dlg
        self.layercount = layercount
        self.getlabels = getlabels
        self.completerClassList = completerClassList
        self.completerClassList["completerClassList"] = {}
        self.queryvar = queryvar
        self.sparql = sparql
        self.preferredlang=preferredlang
        self.geoClassListGui = geoClassListGui
        self.amountoflabels = -1
        self.geoClassList = geoClassList
        self.geoTreeViewModel=self.dlg.geoTreeViewModel
        self.examplequery = examplequery
        self.resultlist = {}
        self.loadfromfile=False
        self.query =SPARQLUtils.queryPreProcessing(query,self.triplestoreconf,None,False,True)

    def run(self):
        if os.path.exists(os.path.join(__location__,"../../../tmp/geoconcepts/" + str(str(self.triplestoreconf["resource"]["url"]).replace("/", "_").replace("['","").replace("']","").replace("\\","_").replace(":","_")) + ".json")):
            self.loadfromfile=True
        else:
            results = SPARQLUtils.executeQuery(self.triplestoreurl,self.query,self.triplestoreconf)
            if results==False:
                return False
            for result in results["results"]["bindings"]:
                if self.queryvar in result:
                    self.resultlist[str(result[self.queryvar]["value"])]={"concept":str(result[self.queryvar]["value"])}
            if self.getlabels and "labelproperty" in self.triplestoreconf and self.triplestoreconf[
                "labelproperty"] != "":
                if "classlabelquery" in self.triplestoreconf:
                    self.resultlist = SPARQLUtils.getLabelsForClasses(self.resultlist, self.triplestoreconf["classlabelquery"],self.triplestoreconf,self.triplestoreurl,self.preferredlang)
                else:
                    self.resultlist = SPARQLUtils.getLabelsForClasses(self.resultlist, None,
                                                             self.triplestoreconf, self.triplestoreurl,self.preferredlang)
        return True

    def finished(self, result):
        self.geoClassList.clear()
        self.geoTreeViewModel.clear()
        self.geoClassListGui.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.geoClassListGui.header().setStretchLastSection(True)
        self.geoClassListGui.header().setMinimumSectionSize(self.dlg.classTreeView.width())
        self.rootNode=self.geoTreeViewModel.invisibleRootItem()
        path=os.path.join(__location__,
                         "../../../tmp/geoconcepts/" + str(str(self.triplestoreconf["resource"]["url"]).replace("/", "_")
                                                     .replace("\\","_").replace("['","").replace("']","").replace(":","_"))
                                                                              + ".json")
        if self.loadfromfile and exists(path):
            elemcount=UIUtils.loadTreeFromJSONFile(self.rootNode,path)
            self.dlg.conceptViewTabWidget.setTabText(0, "GeoConcepts (" + str(elemcount) + ")")
        else:
            self.dlg.conceptViewTabWidget.setTabText(0, "GeoConcepts (" + str(len(self.resultlist)) + ")")
            if self.examplequery is not None:
                self.sparql.setPlainText(self.examplequery)
                self.sparql.columnvars = {}
            for concept in self.resultlist:
                item = QStandardItem()
                item.setData(self.resultlist[concept]["concept"], UIUtils.dataslot_conceptURI)
                if "label" in self.resultlist[concept] and self.resultlist[concept]["label"]!="":
                    item.setText(self.resultlist[concept]["label"]+" ("+SPARQLUtils.labelFromURI(self.resultlist[concept]["concept"],self.triplestoreconf["prefixesrev"]) + ")")
                else:
                    item.setText(SPARQLUtils.labelFromURI(self.resultlist[concept]["concept"],self.triplestoreconf["prefixesrev"]))
                item.setForeground(QColor(0,0,0))
                item.setEditable(False)
                item.setIcon(UIUtils.geoclassicon)
                item.setData(SPARQLUtils.geoclassnode, UIUtils.dataslot_nodetype)
                item.setToolTip("GeoClass "+str(item.text())+": <br>"+SPARQLUtils.treeNodeToolTip)
                self.rootNode.appendRow(item)
                if self.triplestoreconf["name"] == "Wikidata" and "label" in self.resultlist[concept] and "(" in item.text():
                    self.completerClassList["completerClassList"][self.resultlist[concept]["concept"][self.resultlist[concept]["concept"].rfind('/') + 1:]] = "wd:" + \
                                                                                                      item.text().split(
                                                                                                          "(")[
                                                                                                          1].replace(
                                                                                                          " ",
                                                                                                          "_").replace(
                                                                                                          ")", "")
                else:
                    self.completerClassList["completerClassList"][
                        item.text()] = "<" + str(self.resultlist[concept]["concept"]) + ">"
            self.sparql.updateNewClassList()
            f = open(os.path.join(__location__, "../../../tmp/geoconcepts/" + str(
                str(self.triplestoreconf["resource"]["url"]).replace("/", "_").replace("\\","_").replace("['","").replace("']","").replace(":", "_")) + ".json"), "w")
            res = {"text": "root"}
            UIUtils.iterateTreeToJSON(self.rootNode, res, False, True, self.triplestoreconf, None)
            #QgsMessageLog.logMessage('Started task "{}"'.format(res), MESSAGE_CATEGORY, Qgis.Info)
            f.write(json.dumps(res, indent=2, default=ConfigUtils.dumper, sort_keys=True))
            f.close()