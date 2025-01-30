from ....util.ui.uiutils import UIUtils
from ....util.conf.configutils import ConfigUtils
from ....util.ui.qstandardclasstreeitem import QStandardClassTreeItem
from ....util.sparqlutils import SPARQLUtils
from qgis.core import Qgis,QgsTask, QgsMessageLog
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QHeaderView
import os
from os.path import exists
import json

MESSAGE_CATEGORY = 'ClassTreeQueryTask'

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

notforclasstree = ["http://www.w3.org/2002/07/owl#Class", "http://www.w3.org/1999/02/22-rdf-syntax-ns#List",
                   "http://www.w3.org/1999/02/22-rdf-syntax-ns#Property","http://www.w3.org/2000/01/rdf-schema#Property",
                   "http://www.w3.org/2000/01/rdf-schema#Class", "http://www.w3.org/2000/01/rdf-schema#Datatype",
                   "http://www.w3.org/2000/01/rdf-schema#ContainerMembershipProperty","http://www.w3.org/2000/01/rdf-schema#Resource",
                   "http://www.w3.org/2002/07/owl#DatatypeProperty", "http://www.w3.org/2002/07/owl#AnnotationProperty",
                   "http://www.w3.org/2002/07/owl#Restriction", "http://www.w3.org/2002/07/owl#ObjectProperty",
                   "http://www.w3.org/2002/07/owl#NamedIndividual", "http://www.w3.org/2002/07/owl#Ontology"]


class ClassTreeQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl,dlg,treeNode,triplestoreconf,preferredlang="en"):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.dlg=dlg
        self.preferredlang=preferredlang
        self.triplestoreconf=triplestoreconf
        self.treeNode=treeNode
        self.classTreeViewModel=self.dlg.classTreeViewModel
        self.amount=-1
        self.classtreemap=None
        self.subclassmap=None
        self.query="""PREFIX owl: <http://www.w3.org/2002/07/owl#>\n
                    PREFIX data: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n
                    SELECT DISTINCT ?subject ?label ?supertype \n
                    WHERE {\n"""
        self.query += "{ ?individual <" + str(self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["typeproperty"]) + "> ?subject . } UNION { ?subject <" + str(self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["typeproperty"]) + "> owl:Class . } UNION { ?subject <" + str(self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["typeproperty"]) + "> rdfs:Class . } UNION { ?subject <" + str(self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["subclassproperty"]) + "> ?supertype . } \n"
        self.query += """OPTIONAL { ?subject <""" + str(self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["subclassproperty"]) + """> ?supertype . }\n""" + SPARQLUtils.resolvePropertyToTriplePattern("%%labelproperty%%", "?label", "?subject",self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()],"OPTIONAL", "")+ """ }"""


    def run(self):
        #QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        if "url" in self.triplestoreconf["resource"] and os.path.exists(os.path.join(__location__,"../tmp/classtree/" + str(str(self.triplestoreconf["resource"]["url"]).replace("/", "_").replace("['","").replace("']","").replace("\\","_").replace(":","_")) + ".json")):
            self.classtreemap=None
            self.subclassmap=None
        else:
            self.classtreemap={"root":self.treeNode}
            self.subclassmap={"root":set()}
            results = SPARQLUtils.executeQuery(self.triplestoreurl,self.query,self.triplestoreconf)
            if results=="Exists error" or results==False and SPARQLUtils.exception is not None:
                results = SPARQLUtils.executeQuery(self.triplestoreurl, self.query.replace("?hasgeo","").replace("(Bound(?hasgeo) AS ?hgeo)",""), self.triplestoreconf)
            if results==False:
                if SPARQLUtils.exception is None:
                    SPARQLUtils.exception="No results"
                return False
            hasparent={}
            #QgsMessageLog.logMessage('Got results! '+str(len(results["results"]["bindings"])), MESSAGE_CATEGORY, Qgis.Info)
            for result in results["results"]["bindings"]:
                subval=result["subject"]["value"]
                if subval is None or subval=="" or subval in notforclasstree:
                    continue
                if subval not in self.classtreemap:
                    self.classtreemap[subval]=QStandardClassTreeItem()
                    self.classtreemap[subval].setData(subval,UIUtils.dataslot_conceptURI)
                    if "label" in result:
                        self.classtreemap[subval].setText(
                            result["label"]["value"] + " (" + SPARQLUtils.labelFromURI(subval, self.triplestoreconf["prefixesrev"]) + ")")
                    else:
                        self.classtreemap[subval].setText(
                            SPARQLUtils.labelFromURI(subval, self.triplestoreconf["prefixesrev"]))
                    if "hgeo" in result and (result["hgeo"]["value"]=="true" or result["hgeo"]["value"]==True or result["hgeo"]["value"]==1):
                        QgsMessageLog.logMessage("HGEO: "+str(result["hgeo"])+" "+str(subval),MESSAGE_CATEGORY, Qgis.Info)
                        self.classtreemap[subval].setIcon(UIUtils.geoclassicon)
                        self.classtreemap[subval].setData(SPARQLUtils.geoclassnode, UIUtils.dataslot_nodetype)
                        self.classtreemap[subval].setToolTip(
                            "GeoClass " + str(self.classtreemap[subval].text()) + ": <br>" + SPARQLUtils.treeNodeToolTip)
                    elif "geoclasses" in self.triplestoreconf and subval in self.triplestoreconf["geoclasses"]:
                        self.classtreemap[subval].setIcon(UIUtils.linkedgeoclassicon)
                        self.classtreemap[subval].setData(SPARQLUtils.linkedgeoclassnode, UIUtils.dataslot_nodetype)
                        #QgsMessageLog.logMessage('Started task "{}"'.format(self.triplestoreconf["geoclasses"]), MESSAGE_CATEGORY,
                        #                         Qgis.Info)
                        self.classtreemap[subval].setData(self.triplestoreconf["geoclasses"][subval][0],260)
                        self.classtreemap[subval].setToolTip(
                            "Class linked to a GeoClass " + str(self.classtreemap[subval].text()) + ": <br>" + SPARQLUtils.treeNodeToolTip)
                    else:
                        self.classtreemap[subval].setIcon(UIUtils.classicon)
                        self.classtreemap[subval].setData(SPARQLUtils.classnode, UIUtils.dataslot_nodetype)
                        self.classtreemap[subval].setToolTip(
                            "Class " + str(self.classtreemap[subval].text()) + ": <br>" + str(SPARQLUtils.treeNodeToolTip))
                if subval not in self.subclassmap:
                    self.subclassmap[subval]=set()
                if "supertype" in result:
                    if not result["supertype"]["value"] in self.subclassmap:
                        self.subclassmap[result["supertype"]["value"]] = set()
                    if result["supertype"]["value"]!=subval and not result["supertype"]["value"] in self.subclassmap[subval]:
                        self.subclassmap[result["supertype"]["value"]].add(subval)
                        hasparent[subval]=True
            for cls in self.classtreemap:
                if cls not in hasparent and cls!="root":
                    self.subclassmap["root"].add(cls)
        #QgsMessageLog.logMessage('Finished generating tree structure', MESSAGE_CATEGORY, Qgis.Info)
        #QgsMessageLog.logMessage('Started task "{}"'.format(str(self.classtreemap)), MESSAGE_CATEGORY, Qgis.Info)
        return True

    def buildTree(self,curNode,classtreemap,subclassmap,mypath):
        if curNode not in self.alreadyprocessed:
            for item in subclassmap[curNode]:
                if item in classtreemap and item not in self.alreadyprocessed:
                    #QgsMessageLog.logMessage('Started task "{}"'.format("Append: "+str(curNode)+" - "+str(item)), MESSAGE_CATEGORY,
                    #                     Qgis.Info)
                    classtreemap[curNode].appendRow(classtreemap[item])
                if item!=curNode and item not in mypath:
                    self.buildTree(item,classtreemap,subclassmap,mypath+[item])
            self.alreadyprocessed.add(curNode)


    def finished(self, result):
        #QgsMessageLog.logMessage('Started task "{}"'.format(
        #    "Recursive tree building"), MESSAGE_CATEGORY, Qgis.Info)
        self.classTreeViewModel.clear()
        self.rootNode=self.dlg.classTreeViewModel.invisibleRootItem()
        path=os.path.join(__location__, "../../../tmp/classtree/" + str(str(self.triplestoreconf["resource"]["url"]).replace("/", "_").replace("['","").replace("']","").replace("\\","_").replace(":","_")) + ".json")
        if SPARQLUtils.exception is not None:
            SPARQLUtils.handleException(MESSAGE_CATEGORY, str(self.description)+": An error occurred!")
        elif self.classtreemap is None and self.subclassmap is None and exists(path):
            elemcount=UIUtils.loadTreeFromJSONFile(self.rootNode,path)
            self.dlg.conceptViewTabWidget.setTabText(3, "ClassTree (" + str(elemcount) + ")")
        elif self.classtreemap is not None and self.subclassmap is not None:
            self.alreadyprocessed=set()
            self.dlg.conceptViewTabWidget.setTabText(3, "ClassTree (" + str(len(self.classtreemap)) + ")")
            self.classtreemap["root"]=self.rootNode
            self.buildTree("root",self.classtreemap,self.subclassmap,[])
            #QgsMessageLog.logMessage('Started task "{}"'.format(os.path.join(__location__,
            #             "../tmp/classtree/" + str(str(self.triplestoreconf["resource"]["url"]).replace("/", "_").replace("['","").replace("']","").replace("\\","_").replace(":","_")) + ".json")), MESSAGE_CATEGORY, Qgis.Info)
            f = open(os.path.join(__location__,"../../../tmp/classtree/"+str(str(self.triplestoreconf["resource"]["url"]).replace("/","_").replace("['","").replace("']","").replace("\\","_").replace(":","_"))+".json"), "w")
            res={"text": "root"}
            UIUtils.iterateTreeToJSON(self.rootNode, res, False, True, self.triplestoreconf, None)
            #QgsMessageLog.logMessage('Started task "{}"'.format(res), MESSAGE_CATEGORY, Qgis.Info)
            f.write(json.dumps(res,indent=2,default=ConfigUtils.dumper,sort_keys=True))
            f.close()
        self.dlg.classTreeView.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.dlg.classTreeView.header().setStretchLastSection(True)
        self.dlg.classTreeView.header().setMinimumSectionSize(self.dlg.classTreeView.width())
        self.dlg.classTreeView.setSortingEnabled(True)
        self.dlg.classTreeView.sortByColumn(0, Qt.AscendingOrder)
        self.dlg.classTreeView.setSortingEnabled(False)
