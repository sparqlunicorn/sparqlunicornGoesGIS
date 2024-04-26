from ....util.ui.uiutils import UIUtils
from ....util.sparqlutils import SPARQLUtils
from qgis.core import Qgis,QgsTask, QgsMessageLog
from qgis.PyQt.QtGui import QStandardItem
from qgis.PyQt.QtWidgets import QHeaderView
from qgis.PyQt.QtCore import Qt, QSize

MESSAGE_CATEGORY = 'FindRelatedConceptQueryTask'

class FindRelatedConceptQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl,dlg,concept,label,nodetype,triplestoreconf,searchResult,preferredlang="en"):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.searchResultModel=dlg
        self.nodetype=nodetype
        self.preferredlang=preferredlang
        self.searchResult=searchResult
        self.triplestoreconf=triplestoreconf
        self.concept=concept
        self.label=label
        self.queryresult={}
        self.queryresult2 = {}
        while self.searchResultModel.rowCount()>0:
            self.searchResultModel.removeRow(0)
        self.searchResultModel.insertRow(0)
        curitem = QStandardItem()
        curitem.setText("Loading...")
        self.searchResultModel.setItem(0, 0, curitem)

    def findConnectedConceptsFromProperty(self):
        leftsidequery="SELECT DISTINCT ?val ?label WHERE { ?sub <"+str(self.concept)+"> ?obj .\n"\
               +" OPTIONAL { ?sub <"+str(self.triplestoreconf["typeproperty"])+"> ?val . \n"\
               +" OPTIONAL { "+SPARQLUtils.resolvePropertyToTriplePattern("%%labelproperty%%","?label","?val",self.triplestoreconf,None,None)+"  FILTER(LANG(?label)=\""+str(self.preferredlang)+"\")}\n" \
               +" OPTIONAL { "+SPARQLUtils.resolvePropertyToTriplePattern("%%labelproperty%%","?label","?val",self.triplestoreconf,None,None)+" }\n } }"
        rightsidequery="SELECT DISTINCT ?val ?label WHERE { ?sub <"+str(self.concept)+"> ?obj .\n"\
               + " OPTIONAL { ?obj <" + str(self.triplestoreconf["typeproperty"]) + "> ?val .\n" \
               + " OPTIONAL { "+SPARQLUtils.resolvePropertyToTriplePattern("%%labelproperty%%","?label","?val",self.triplestoreconf,None,None)+"  FILTER(LANG(?label)=\"" + str(self.preferredlang) + "\")}\n" \
               + " OPTIONAL { "+SPARQLUtils.resolvePropertyToTriplePattern("%%labelproperty%%","?label","?val",self.triplestoreconf,None,None)+" }\n } }"
        results = SPARQLUtils.executeQuery(self.triplestoreurl, leftsidequery, self.triplestoreconf)
        results2 = SPARQLUtils.executeQuery(self.triplestoreurl, rightsidequery, self.triplestoreconf)
        self.queryresult={}
        self.queryresult2 = {}
        if results!=False:
            for result in results["results"]["bindings"]:
                if "val" in result and result["val"]["value"]!="":
                    if result["val"]["value"] not in self.queryresult:
                        self.queryresult[result["val"]["value"]]={}
                    if "label" in result:
                        self.queryresult[result["val"]["value"]] = result["label"]["value"]
                    else:
                        self.queryresult[result["val"]["value"]] = SPARQLUtils.labelFromURI(result["val"]["value"])
        if results2!=False:
            for result in results2["results"]["bindings"]:
                if "val" in result and result["val"]["value"]!="":
                    if result["val"]["value"] not in self.queryresult2:
                        self.queryresult2[result["val"]["value"]]={}
                    if "label" in result:
                        self.queryresult2[result["val"]["value"]] = result["label"]["value"]
                    else:
                        self.queryresult2[result["val"]["value"]] = SPARQLUtils.labelFromURI(result["val"]["value"])

    def findConnectedConceptsFromClass(self):
        rightsidequery = "SELECT DISTINCT ?rel ?val ?label ?rellabel WHERE {\n ?con <" + str(self.triplestoreconf["typeproperty"]) + "> <" + str(
            self.concept) + "> .\n ?con ?rel ?item .\n ?item  <" + str(
            self.triplestoreconf["typeproperty"]) + "> ?val .\n "+\
            SPARQLUtils.resolvePropertyToTriplePattern("%%labelproperty%%","?label","?val",self.triplestoreconf,"OPTIONAL","FILTER(LANG(?label) = \""+str(self.preferredlang)+"\")")+"\n "+\
            SPARQLUtils.resolvePropertyToTriplePattern("%%labelproperty%%", "?label", "?val", self.triplestoreconf, "OPTIONAL","") + "\n " +\
            SPARQLUtils.resolvePropertyToTriplePattern("%%labelproperty%%", "?rellabel", "?rel", self.triplestoreconf, "OPTIONAL","FILTER(LANG(?rellabel) = \"" + str(self.preferredlang) + "\")",True) + "\n " +\
            SPARQLUtils.resolvePropertyToTriplePattern("%%labelproperty%%", "?rellabel", "?rel", self.triplestoreconf, "OPTIONAL","",True) + "\n }"
        leftsidequery = "SELECT DISTINCT ?rel ?val ?label ?rellabel WHERE {\n ?tocon <" + str(self.triplestoreconf["typeproperty"]) + "> ?val .\n ?tocon ?rel ?con .\n ?con <" + str(self.triplestoreconf["typeproperty"]) + "> <" + str(
            self.concept) + "> .\n "+\
            SPARQLUtils.resolvePropertyToTriplePattern("%%labelproperty%%", "?label", "?val", self.triplestoreconf,"OPTIONAL", "FILTER(LANG(?label) = \"" + str(self.preferredlang) + "\")") + "\n " + \
            SPARQLUtils.resolvePropertyToTriplePattern("%%labelproperty%%", "?label", "?val", self.triplestoreconf,"OPTIONAL", "") + "\n " + \
            SPARQLUtils.resolvePropertyToTriplePattern("%%labelproperty%%", "?rellabel", "?rel", self.triplestoreconf,"OPTIONAL", "FILTER(LANG(?rellabel) = \"" + str(self.preferredlang) + "\")",True) + "\n " + \
            SPARQLUtils.resolvePropertyToTriplePattern("%%labelproperty%%", "?rellabel", "?rel", self.triplestoreconf,"OPTIONAL", "",True) + "\n }"
        #QgsMessageLog.logMessage("SELECT ?rel WHERE { ?con "+str(self.triplestoreconf["typeproperty"])+" "+str(self.concept)+" . ?con ?rel ?item . OPTIONAL { ?item "+str(self.triplestoreconf["typeproperty"])+" ?val . } }", MESSAGE_CATEGORY, Qgis.Info)
        results = SPARQLUtils.executeQuery(self.triplestoreurl,leftsidequery,self.triplestoreconf)
        results2 = SPARQLUtils.executeQuery(self.triplestoreurl, rightsidequery, self.triplestoreconf)
        #QgsMessageLog.logMessage("Query results: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
        self.queryresult={}
        self.queryresult2 = {}
        for result in results["results"]["bindings"]:
            if "rel" in result and "val" in result and result["rel"]["value"]!="":
                if result["rel"]["value"] not in self.queryresult:
                    self.queryresult[result["rel"]["value"]]={}
                self.queryresult[result["rel"]["value"]][result["val"]["value"]]={}
                if "rellabel" in result:
                    self.queryresult[result["rel"]["value"]][result["val"]["value"]]["rellabel"] = result["rellabel"][
                        "value"]
                else:
                    self.queryresult[result["rel"]["value"]][result["val"]["value"]]["rellabel"] = ""
                if "label" in result:
                    self.queryresult[result["rel"]["value"]][result["val"]["value"]]["label"]=result["label"]["value"]
                else:
                    self.queryresult[result["rel"]["value"]][result["val"]["value"]]["label"]=""
        for result in results2["results"]["bindings"]:
            if "rel" in result and "val" in result and result["rel"]["value"]!="":
                if result["rel"]["value"] not in self.queryresult:
                    self.queryresult2[result["rel"]["value"]]={}
                self.queryresult2[result["rel"]["value"]][result["val"]["value"]]={}
                if "rellabel" in result:
                    self.queryresult2[result["rel"]["value"]][result["val"]["value"]]["rellabel"] = result["rellabel"][
                        "value"]
                else:
                    self.queryresult2[result["rel"]["value"]][result["val"]["value"]]["rellabel"] = ""
                if "label" in result:
                    self.queryresult2[result["rel"]["value"]][result["val"]["value"]]["label"]=result["label"]["value"]
                else:
                    self.queryresult2[result["rel"]["value"]][result["val"]["value"]]["label"] = ""

    def run(self):
        #QgsMessageLog.logMessage('Started task "{}"'.format(self.description), MESSAGE_CATEGORY, Qgis.Info)
        #QgsMessageLog.logMessage('Started task "{}"'.format(self.nodetype), MESSAGE_CATEGORY, Qgis.Info)
        if self.nodetype==SPARQLUtils.classnode or self.nodetype==SPARQLUtils.geoclassnode:
            self.findConnectedConceptsFromClass()
        else:
            self.findConnectedConceptsFromProperty()
        return True

    def processPropertyResult(self):
        counter=0
        for val in self.queryresult:
            self.searchResultModel.insertRow(counter)
            curitem = QStandardItem()
            if self.queryresult[val] != "":
                curitem.setText(
                    str(self.queryresult[val]) + " (" + SPARQLUtils.labelFromURI(str(val)) + ")")
            else:
                curitem.setText(SPARQLUtils.labelFromURI(str(val)))
            curitem.setToolTip(str(val))
            curitem.setIcon(UIUtils.classicon)
            curitem.setData(str(val), UIUtils.dataslot_conceptURI)
            curitem.setData(SPARQLUtils.classnode, UIUtils.dataslot_nodetype)
            self.searchResultModel.setItem(counter, 0, curitem)
            curitem = QStandardItem()
            UIUtils.detectItemNodeType(curitem, self.concept, self.triplestoreconf, None, None, None,
                                       SPARQLUtils.labelFromURI(self.concept) + "         ", self.concept)
            if self.label is not None and self.label != "":
                curitem.setText(self.label)
            self.searchResultModel.setItem(counter, 1, curitem)
            counter+=1
        for val in self.queryresult2:
            self.searchResultModel.insertRow(counter)
            curitem = QStandardItem()
            UIUtils.detectItemNodeType(curitem, self.concept, self.triplestoreconf, None, None, None,
                                       SPARQLUtils.labelFromURI(self.concept) + "         ", self.concept)
            if self.label is not None and self.label != "":
                curitem.setText(self.label)
            self.searchResultModel.setItem(counter, 1, curitem)
            curitem = QStandardItem()
            if self.queryresult2[val] != "":
                curitem.setText(str(self.queryresult2[val]) + " (" + SPARQLUtils.labelFromURI(str(val)) + ")")
            else:
                curitem.setText(SPARQLUtils.labelFromURI(str(val)))
            curitem.setToolTip(str(val))
            curitem.setIcon(UIUtils.classicon)
            curitem.setData(str(val), UIUtils.dataslot_conceptURI)
            curitem.setData(SPARQLUtils.classnode, UIUtils.dataslot_nodetype)
            self.searchResultModel.setItem(counter, 2, curitem)
            counter+=1
        self.searchResultModel.setHeaderData(0, Qt.Horizontal, "Incoming Concept")
        self.searchResultModel.setHeaderData(1, Qt.Horizontal, "Relation")
        self.searchResultModel.setHeaderData(2, Qt.Horizontal, "Outgoing Concept")
        header=self.searchResult.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

    def processClassResult(self):
        counter=0
        for rel in self.queryresult:
            for val in self.queryresult[rel]:
                self.searchResultModel.insertRow(counter)
                curitem=QStandardItem()
                if self.queryresult[rel][val]["label"]!="":
                    curitem.setText(str(self.queryresult[rel][val]["label"])+" ("+SPARQLUtils.labelFromURI(str(val))+")")
                else:
                    curitem.setText(SPARQLUtils.labelFromURI(str(val)))
                curitem.setToolTip(str(val))
                curitem.setIcon(UIUtils.classicon)
                curitem.setData(str(val),UIUtils.dataslot_conceptURI)
                curitem.setData(SPARQLUtils.classnode, UIUtils.dataslot_nodetype)
                self.searchResultModel.setItem(counter, 0, curitem)
                curitem=QStandardItem()
                UIUtils.detectItemNodeType(curitem, rel, self.triplestoreconf, None, None, None,
                                           SPARQLUtils.labelFromURI(rel)+"         ", rel)
                if self.queryresult[rel][val]["rellabel"]!="":
                    curitem.setText(str(self.queryresult[rel][val]["rellabel"])+" ("+SPARQLUtils.labelFromURI(rel)+")")
                self.searchResultModel.setItem(counter, 1, curitem)
                curitem=QStandardItem()
                if self.label is not None and self.label!= "":
                    curitem.setText(self.label)
                else:
                    curitem.setText(SPARQLUtils.labelFromURI(str(self.concept)))
                curitem.setIcon(UIUtils.classicon)
                curitem.setData(str(self.concept),UIUtils.dataslot_conceptURI)
                curitem.setData(SPARQLUtils.classnode, UIUtils.dataslot_nodetype)
                self.searchResultModel.setItem(counter, 2, curitem)
                self.searchResultModel.setItem(counter, 3, QStandardItem())
                self.searchResultModel.setItem(counter, 4, QStandardItem())
                counter+=1
        for rel in self.queryresult2:
            for val in self.queryresult2[rel]:
                self.searchResultModel.insertRow(counter)
                curitem=QStandardItem()
                UIUtils.detectItemNodeType(curitem,rel,self.triplestoreconf,None,None,None,SPARQLUtils.labelFromURI(rel)+"         ",rel)
                if self.queryresult2[rel][val]["rellabel"]!="":
                    curitem.setText(str(self.queryresult2[rel][val]["rellabel"])+" ("+SPARQLUtils.labelFromURI(rel)+")")
                self.searchResultModel.setItem(counter, 3, curitem)
                curitem=QStandardItem()
                if self.label is not None and self.label!= "":
                    curitem.setText(self.label)
                else:
                    curitem.setText(SPARQLUtils.labelFromURI(str(self.concept)))
                curitem.setIcon(UIUtils.classicon)
                curitem.setData(str(self.concept),UIUtils.dataslot_conceptURI)
                curitem.setData(SPARQLUtils.classnode, UIUtils.dataslot_nodetype)
                self.searchResultModel.setItem(counter, 2, curitem)
                curitem=QStandardItem()
                if self.queryresult2[rel][val]["label"]!="":
                    curitem.setText(str(self.queryresult2[rel][val]["label"])+" ("+SPARQLUtils.labelFromURI(str(val))+")")
                else:
                    curitem.setText(SPARQLUtils.labelFromURI(str(val)))
                curitem.setToolTip(str(val))
                curitem.setIcon(UIUtils.classicon)
                curitem.setData(SPARQLUtils.classnode, UIUtils.dataslot_nodetype)
                curitem.setData(str(val),UIUtils.dataslot_conceptURI)
                self.searchResultModel.setItem(counter, 4, curitem)
                self.searchResultModel.setItem(counter, 0, QStandardItem())
                self.searchResultModel.setItem(counter, 1, QStandardItem())
                counter+=1
        self.searchResultModel.setHeaderData(0, Qt.Horizontal, "Incoming Concept")
        self.searchResultModel.setHeaderData(1, Qt.Horizontal, "Incoming Relation")
        self.searchResultModel.setHeaderData(2, Qt.Horizontal, "Concept")
        self.searchResultModel.setHeaderData(3, Qt.Horizontal, "Outgoing Relation")
        self.searchResultModel.setHeaderData(4, Qt.Horizontal, "Outgoing Concept")
        header=self.searchResult.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

    def finished(self, result):
        #QgsMessageLog.logMessage('Started task "{}"'.format(
        #    str(self.concept)), MESSAGE_CATEGORY, Qgis.Info)
        while self.searchResultModel.rowCount()>0:
            self.searchResultModel.removeRow(0)
        if self.nodetype==SPARQLUtils.classnode or self.nodetype==SPARQLUtils.geoclassnode:
            self.processClassResult()
        else:
            self.processPropertyResult()
        SPARQLUtils.handleException(MESSAGE_CATEGORY)
