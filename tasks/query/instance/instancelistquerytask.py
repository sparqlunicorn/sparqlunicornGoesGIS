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
        labelpattern=SPARQLUtils.resolvePropertyToTriplePattern("%%labelproperty%%","?label","?con",self.triplestoreconf,"OPTIONAL","FILTER(LANG(?label) =  \""+str(self.preferredlang)+"\") ")+" "+SPARQLUtils.resolvePropertyToTriplePattern("%%labelproperty%%","?label","?con",self.triplestoreconf,"OPTIONAL",None)
        geotriplepattern=None
        if "geotriplepattern" in self.triplestoreconf:
            geotriplepattern=""
            for geopat in self.triplestoreconf["geotriplepattern"]:
                geotriplepattern+=f'OPTIONAL {{ {geopat.replace("?geo","?hasgeo").replace("?item","?con").replace("?lat","?hasgeo")}+" }}\n'
        geometryproperty=None
        if "geometryproperty" in self.triplestoreconf:
            if type(self.triplestoreconf["geometryproperty"]) is list:
                geometryproperty = self.triplestoreconf["geometryproperty"][0]
            else:
                geometryproperty = self.triplestoreconf["geometryproperty"]
        if nodetype==SPARQLUtils.collectionclassnode:
            if "geometryproperty" in self.triplestoreconf:
                thequery=f"SELECT ?con ?label ?hasgeo WHERE {{  <{self.treeNode.data(UIUtils.dataslot_conceptURI)}> <http://www.w3.org/2000/01/rdf-schema#member> ?con .\n {labelpattern}\n BIND(EXISTS {{ ?con <{geometryproperty}> ?wkt }} AS ?hasgeo) }}"
            else:
                thequery=f"SELECT ?con ?label WHERE {{  <{self.treeNode.data(UIUtils.dataslot_conceptURI)}> <http://www.w3.org/2000/01/rdf-schema#member> ?con . {labelpattern} }}"
        elif nodetype==SPARQLUtils.linkedgeoclassnode:
            thequery = f"SELECT ?con ?label ?hasgeo ?linkedgeo WHERE {{\n ?con <{typeproperty}> <{self.treeNode.data(UIUtils.dataslot_conceptURI)}> .\n {labelpattern}\n OPTIONAL {{?con <{geometryproperty}> ?hasgeo . }}\n  OPTIONAL {{?con <{self.treeNode.data(UIUtils.dataslot_linkedconceptrel)}> ?linkedgeo . }}\n }}"
        else:
            if "geometryproperty" in self.triplestoreconf:
                if geotriplepattern is not None:
                    thequery = f"SELECT ?con ?label ?hasgeo WHERE {{ ?con <{typeproperty}> <{self.treeNode.data(UIUtils.dataslot_conceptURI)}> . {labelpattern} {geotriplepattern} }}"
                else:
                    thequery = f"SELECT ?con ?label ?hasgeo WHERE {{ ?con <{typeproperty}> <{self.treeNode.data(UIUtils.dataslot_conceptURI)}> . {labelpattern} OPTIONAL {{ ?con <{geometryproperty}> ?hasgeo }} }}"
            else:
                thequery = f"SELECT ?con ?label WHERE {{ ?con <{typeproperty}> <{self.treeNode.data(UIUtils.dataslot_conceptURI)}> . {labelpattern} }}"
        results = SPARQLUtils.executeQuery(self.triplestoreurl,thequery,self.triplestoreconf)
        #QgsMessageLog.logMessage("Process literal: " + str(results),
        #                         MESSAGE_CATEGORY, Qgis.Info)
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
                    self.queryresult[result["con"]["value"]]["label"] = f'{result["label"]["value"]} ({SPARQLUtils.labelFromURI(result["con"]["value"],self.triplestoreconf["prefixesrev"])})'
                else:
                    self.queryresult[result["con"]["value"]]["label"]=SPARQLUtils.labelFromURI(result["con"]["value"],self.triplestoreconf["prefixesrev"])
        return True

    def finished(self, result):
        if self.treeNode.data(UIUtils.dataslot_instanceamount)==None:
            self.treeNode.setData(str(len(self.queryresult)),UIUtils.dataslot_instanceamount)
            self.treeNode.setText(f"{self.treeNode.text()} [{len(self.queryresult)}]")
        if(self.hasgeocount>0 and self.hasgeocount<len(self.queryresult)) and self.treeNode.data(UIUtils.dataslot_nodetype)!=SPARQLUtils.collectionclassnode and self.treeNode.data(UIUtils.dataslot_nodetype)!=SPARQLUtils.linkedgeoclassnode:
            self.treeNode.setIcon(UIUtils.halfgeoclassicon)
            self.treeNode.setData(SPARQLUtils.halfgeoclassnode, UIUtils.dataslot_nodetype)
        elif(self.hasgeocount>0 and self.hasgeocount==len(self.queryresult)) and self.treeNode.data(UIUtils.dataslot_nodetype)!=SPARQLUtils.collectionclassnode and self.treeNode.data(UIUtils.dataslot_nodetype)!=SPARQLUtils.linkedgeoclassnode:
            self.treeNode.setIcon(UIUtils.geoclassicon)
            self.treeNode.setData(SPARQLUtils.geoclassnode, UIUtils.dataslot_nodetype)
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
                item.setToolTip(f"GeoInstance {item.text()}: <br>{SPARQLUtils.treeNodeToolTip}")
            elif self.treeNode.data(UIUtils.dataslot_nodetype)==SPARQLUtils.linkedgeoclassnode \
                    and self.queryresult[concept]["linkedgeo"]:
                item.setData(SPARQLUtils.linkedgeoinstancenode,UIUtils.dataslot_nodetype)
                item.setIcon(UIUtils.linkedgeoinstanceicon)
                item.setData(self.treeNode.data(UIUtils.dataslot_linkedconceptrel),UIUtils.dataslot_linkedconceptrel)
                item.setToolTip(f"Linked GeoInstance {item.text()}: <br>{SPARQLUtils.treeNodeToolTip}")
            else:
                item.setData(SPARQLUtils.instancenode,UIUtils.dataslot_nodetype)
                item.setIcon(UIUtils.instanceicon)
                item.setToolTip(f"Instance {item.text()}: <br>{SPARQLUtils.treeNodeToolTip}")
            self.treeNode.appendRow(item)
        SPARQLUtils.handleException(MESSAGE_CATEGORY)