from ....util.ui.uiutils import UIUtils
from ....util.sparqlutils import SPARQLUtils
from qgis.PyQt.QtGui import QStandardItem
from qgis.core import Qgis,QgsTask, QgsMessageLog

MESSAGE_CATEGORY = 'InstanceListQueryTask'

class InstanceListQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl,dlg,treeNode,triplestoreconf,preferredlang="en"):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.preferredlang=preferredlang
        self.dlg=dlg
        self.hasgeocount=0
        self.linkedgeocount=0
        self.triplestoreconf=triplestoreconf
        self.treeNode=treeNode
        self.queryresult={}

    def run(self):
        typeproperty="http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        labelproperty="http://www.w3.org/2000/01/rdf-schema#label"
        if "typeproperty" in self.triplestoreconf:
            typeproperty=self.triplestoreconf["typeproperty"]
        if "labelproperty" in self.triplestoreconf:
            labelproperty=self.triplestoreconf["labelproperty"]
        nodetype=self.treeNode.data(UIUtils.dataslot_nodetype)
        labelpattern="OPTIONAL { ?con <"+labelproperty+"> ?label . FILTER(LANG(?label) =  \""+str(self.preferredlang)+"\") }\n OPTIONAL { ?con <"+labelproperty+"> ?label . }\n"
        geometryproperty=None
        if "geometryproperty" in self.triplestoreconf:
            if type(self.triplestoreconf["geometryproperty"]) is list:
                geometryproperty = self.triplestoreconf["geometryproperty"][0]
            else:
                geometryproperty = self.triplestoreconf["geometryproperty"]
        if nodetype==SPARQLUtils.collectionclassnode:
            #QgsMessageLog.logMessage('Started task "{}"'.format(
            #        "SELECT ?con ?label WHERE { " + str(
            #            self.treeNode.data(UIUtils.dataslot_conceptURI)) + "http://www.w3.org/2000/01/rdf-schema#member ?con . "+str(labelpattern)+" }"), MESSAGE_CATEGORY, Qgis.Info)
            if "geometryproperty" in self.triplestoreconf:
                thequery="SELECT ?con ?label ?hasgeo WHERE {  <" + str(
                        self.treeNode.data(UIUtils.dataslot_conceptURI)) + "> <http://www.w3.org/2000/01/rdf-schema#member> ?con .\n "+str(labelpattern)+"\n BIND(EXISTS { ""?con <" + str(
                            geometryproperty) + "> ?wkt"" } AS ?hasgeo) }"
            else:
                thequery="SELECT ?con ?label WHERE {  <" + str(
                        self.treeNode.data(UIUtils.dataslot_conceptURI)) + "> <http://www.w3.org/2000/01/rdf-schema#member> ?con . "+str(labelpattern)+" }"
        elif nodetype==SPARQLUtils.linkedgeoclassnode:
            thequery = "SELECT ?con ?label ?hasgeo ?linkedgeo WHERE {\n ?con <" + typeproperty + "> <" + str(
                self.treeNode.data(UIUtils.dataslot_conceptURI)) + "> .\n " + str(labelpattern) + "\n OPTIONAL {?con <" + str(
                geometryproperty) + "> ?hasgeo . }\n  OPTIONAL {?con <" + str(
                self.treeNode.data(UIUtils.dataslot_linkedconceptrel)) + "> ?linkedgeo . }\n }"
        else:
            if "geometryproperty" in self.triplestoreconf:
                if isinstance(self.triplestoreurl, str):
                    thequery = "SELECT ?con ?label ?hasgeo WHERE { ?con <" + typeproperty + "> <" + str(
                        self.treeNode.data(UIUtils.dataslot_conceptURI)) + "> . "+str(labelpattern)+" BIND(EXISTS {?con <" + str(
                        geometryproperty) + "> ?wkt } AS ?hasgeo)}"
                else:
                    thequery = "SELECT ?con ?label ?hasgeo WHERE { ?con <" + typeproperty + "> <" + str(
                        self.treeNode.data(UIUtils.dataslot_conceptURI)) + "> . "+str(labelpattern)+" OPTIONAL { ?con <" + str(
                        geometryproperty) + "> ?hasgeo } }"
            else:
                thequery = "SELECT ?con ?label WHERE { ?con <" + typeproperty + "> <" + str(
                    self.treeNode.data(
                        UIUtils.dataslot_conceptURI)) + "> . "+str(labelpattern)+" }"
        results = SPARQLUtils.executeQuery(self.triplestoreurl,thequery,self.triplestoreconf)
        if results!=False:
            for result in results["results"]["bindings"]:
                if result["con"]["value"] not in self.queryresult:
                    self.queryresult[result["con"]["value"]]={}
                if "hasgeo" in result and (result["hasgeo"]["value"]=="true" or result["hasgeo"]["value"]=="1" or (isinstance(result["hasgeo"]["value"],str) and result["hasgeo"]["value"]!="" and result["hasgeo"]["value"]!="0" and result["hasgeo"]["value"]!="false")):
                    self.queryresult[result["con"]["value"]]["hasgeo"] = True
                    self.hasgeocount+=1
                else:
                    self.queryresult[result["con"]["value"]]["hasgeo"] = False
                if "linkedgeo" in result and (result["linkedgeo"]["value"]=="true" or result["linkedgeo"]["value"]=="1" or (isinstance(result["linkedgeo"]["value"],str) and result["linkedgeo"]["value"]!="" and result["linkedgeo"]["value"]!="0" and result["linkedgeo"]["value"]!="false")):
                    self.queryresult[result["con"]["value"]]["linkedgeo"] = True
                    self.linkedgeocount += 1
                else:
                    self.queryresult[result["con"]["value"]]["linkedgeo"] = False
                if "label" in result:
                    self.queryresult[result["con"]["value"]]["label"] = result["label"]["value"]+" ("+SPARQLUtils.labelFromURI(result["con"]["value"],self.triplestoreconf["prefixesrev"])+")"
                else:
                    self.queryresult[result["con"]["value"]]["label"]=SPARQLUtils.labelFromURI(result["con"]["value"],self.triplestoreconf["prefixesrev"])
        return True

    def finished(self, result):
        if self.treeNode.data(UIUtils.dataslot_instanceamount)==None:
            self.treeNode.setData(str(len(self.queryresult)),UIUtils.dataslot_instanceamount)
            self.treeNode.setText(self.treeNode.text()+" ["+str(len(self.queryresult))+"]")
        if(self.hasgeocount>0 and self.hasgeocount<len(self.queryresult)) and self.treeNode.data(UIUtils.dataslot_nodetype)!=SPARQLUtils.collectionclassnode and self.treeNode.data(UIUtils.dataslot_nodetype)!=SPARQLUtils.linkedgeoclassnode:
            self.treeNode.setIcon(UIUtils.halfgeoclassicon)
            self.treeNode.setData(SPARQLUtils.halfgeoclassnode, UIUtils.dataslot_nodetype)
        elif self.hasgeocount==0 and self.treeNode.data(UIUtils.dataslot_nodetype)!=SPARQLUtils.collectionclassnode and self.treeNode.data(UIUtils.dataslot_nodetype)!=SPARQLUtils.linkedgeoclassnode:
            self.treeNode.setIcon(UIUtils.classicon)
            self.treeNode.setData(SPARQLUtils.classnode,UIUtils.dataslot_nodetype)
        self.treeNode.setData(SPARQLUtils.instancesloadedindicator,UIUtils.dataslot_instancesloaded)
        for concept in self.queryresult:
            item = QStandardItem()
            item.setData(concept, UIUtils.dataslot_conceptURI)
            item.setText(self.queryresult[concept]["label"])
            if (self.treeNode.data(UIUtils.dataslot_nodetype)==SPARQLUtils.geoclassnode \
                    or self.treeNode.data(UIUtils.dataslot_nodetype)==SPARQLUtils.collectionclassnode \
                    or self.treeNode.data(UIUtils.dataslot_nodetype) == SPARQLUtils.halfgeoclassnode \
                    or self.treeNode.data(UIUtils.dataslot_nodetype)==SPARQLUtils.linkedgeoclassnode) \
                    and self.queryresult[concept]["hasgeo"]:
                item.setData(SPARQLUtils.geoinstancenode,UIUtils.dataslot_nodetype)
                item.setIcon(UIUtils.geoinstanceicon)
                item.setToolTip("GeoInstance " + str(item.text()) + ": <br>" + SPARQLUtils.treeNodeToolTip)
            elif self.treeNode.data(UIUtils.dataslot_nodetype)==SPARQLUtils.linkedgeoclassnode \
                    and self.queryresult[concept]["linkedgeo"]:
                item.setData(SPARQLUtils.linkedgeoinstancenode,UIUtils.dataslot_nodetype)
                item.setIcon(UIUtils.linkedgeoinstanceicon)
                item.setData(self.treeNode.data(UIUtils.dataslot_linkedconceptrel),UIUtils.dataslot_linkedconceptrel)
                item.setToolTip("Linked GeoInstance " + str(item.text()) + ": <br>" + SPARQLUtils.treeNodeToolTip)
            else:
                item.setData(SPARQLUtils.instancenode,UIUtils.dataslot_nodetype)
                item.setIcon(UIUtils.instanceicon)
                item.setToolTip("Instance " + str(item.text()) + ": <br>" + SPARQLUtils.treeNodeToolTip)
            self.treeNode.appendRow(item)
