from ..util.sparqlutils import SPARQLUtils
from qgis.core import Qgis
from qgis.PyQt.QtCore import QSettings, QItemSelectionModel, Qt
from qgis.PyQt.QtGui import QStandardItem, QIcon
from qgis.PyQt.QtWidgets import QHeaderView
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog
)

MESSAGE_CATEGORY = 'ClassTreeQueryTask'

class ClassTreeQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl,dlg,treeNode,triplestoreconf,graph=None):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.dlg=dlg
        self.graph=graph
        self.triplestoreconf=triplestoreconf
        self.treeNode=treeNode
        self.classTreeViewModel=self.dlg.classTreeViewModel
        self.amount=-1
        self.query="""PREFIX owl: <http://www.w3.org/2002/07/owl#>\n
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n
                    SELECT DISTINCT ?subject ?label ?supertype ?hasgeo\n
                    WHERE {\n"""
        self.optionalpart=""
        if "highload" in self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()] and self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["highload"]:
            self.query+="{ ?individual <"+self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["typeproperty"]+"> ?subject . } UNION { ?subject <"+str(self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["typeproperty"])+"> owl:Class .  } .\n"
        elif "geometryproperty" in self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()] and self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["geometryproperty"]=="http://www.opengis.net/ont/geosparql#hasGeometry":
            self.optionalpart="OPTIONAL {BIND(EXISTS {?individual <"+str(self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["geometryproperty"])+"> ?lit . ?lit ?a ?wkt } AS ?hasgeo)}"
            self.query+="{ ?individual <"+str(self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["typeproperty"])+"> ?subject . "+str(self.optionalpart)+"} UNION { ?subject <"+str(self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["typeproperty"])+"> owl:Class .  } .\n"
        elif "geometryproperty" in self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()] and self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["geometryproperty"]!="":
            self.optionalpart="OPTIONAL {BIND(EXISTS {?individual <"+str(self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["geometryproperty"])+"> ?wkt } AS ?hasgeo)}"
            self.query+="{ ?individual <"+self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["typeproperty"]+"> ?subject . "+str(self.optionalpart)+"} UNION { ?subject <"+str(self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["typeproperty"])+"> owl:Class .  }  .\n"
        else:
            self.query += "{ ?individual <" + self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["typeproperty"] + "> ?subject . } UNION { ?subject <" + str(self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["typeproperty"]) + "> owl:Class .  }  .\n"
        self.query+="""OPTIONAL { ?subject <"""+str(self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["subclassproperty"])+"""> ?supertype } .\n
                       OPTIONAL { ?subject <"""+str(self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["labelproperty"])+"""> ?label }.\n
                        FILTER (\n
                            (\n
                            ?subject != owl:Class &&\n
                            ?subject != rdf:List &&\n
                            ?subject != rdf:Property &&\n
                            ?subject != rdfs:Class &&\n
                            ?subject != rdfs:Datatype &&\n
                            ?subject != rdfs:ContainerMembershipProperty &&\n
                            ?subject != owl:DatatypeProperty &&\n
                            ?subject != owl:AnnotationProperty &&\n
                            ?subject != owl:Restriction &&\n
                            ?subject != owl:ObjectProperty &&\n
                            ?subject != owl:NamedIndividual &&\n
                            ?subject != owl:Ontology) )\n
                    }"""

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        self.classtreemap={"root":self.treeNode}
        self.subclassmap={"root":set()}
        if self.graph==None:
            results = SPARQLUtils.executeQuery(self.triplestoreurl,self.query,self.triplestoreconf)
        else:
            results=self.graph.query(self.query)
        if results=="Exists error":
            results = SPARQLUtils.executeQuery(self.triplestoreurl, self.query.replace(self.optionalpart,"").replace("?hasgeo",""), self.triplestoreconf)
        if results==False:
            return False
        hasparent={}
        QgsMessageLog.logMessage('Got results! '+str(len(results["results"]["bindings"])), MESSAGE_CATEGORY, Qgis.Info)        
        for result in results["results"]["bindings"]:
            subval=result["subject"]["value"]
            if subval==None or subval=="":
                continue
            if subval not in self.classtreemap:
                self.classtreemap[subval]=QStandardItem()
                self.classtreemap[subval].setData(subval,256)
                if "label" in result:
                    if "hasgeo" in result:
                        self.classtreemap[subval].setText(
                        result["label"]["value"]+" ("+SPARQLUtils.labelFromURI(subval,self.triplestoreconf["prefixesrev"])+")")
                        self.classtreemap[subval].setIcon(SPARQLUtils.geoclassicon)
                        self.classtreemap[subval].setData(SPARQLUtils.geoclassnode, 257)
                        self.classtreemap[subval].setToolTip("GeoClass "+str(self.classtreemap[subval].text())+": <br>"+SPARQLUtils.treeNodeToolTip)
                    else:
                        self.classtreemap[subval].setText(
                        result["label"]["value"]+" ("+SPARQLUtils.labelFromURI(subval,self.triplestoreconf["prefixesrev"])+")")
                        self.classtreemap[subval].setIcon(SPARQLUtils.classicon)
                        self.classtreemap[subval].setData(SPARQLUtils.classnode, 257)
                        self.classtreemap[subval].setToolTip("Class "+str(self.classtreemap[subval].text())+": <br>"+str(SPARQLUtils.treeNodeToolTip))
                else:
                    if "hasgeo" in result:
                        self.classtreemap[subval].setText(SPARQLUtils.labelFromURI(subval,self.triplestoreconf["prefixesrev"]))
                        self.classtreemap[subval].setIcon(SPARQLUtils.geoclassicon)
                        self.classtreemap[subval].setData(SPARQLUtils.geoclassnode, 257)
                        self.classtreemap[subval].setToolTip("GeoClass "+str(self.classtreemap[subval].text())+": <br>"+SPARQLUtils.treeNodeToolTip)
                    else:
                        self.classtreemap[subval].setText(SPARQLUtils.labelFromURI(subval,self.triplestoreconf["prefixesrev"]))
                        self.classtreemap[subval].setIcon(SPARQLUtils.classicon)
                        self.classtreemap[subval].setData(SPARQLUtils.classnode, 257)
                        self.classtreemap[subval].setToolTip("Class "+str(self.classtreemap[subval].text())+": <br>"+SPARQLUtils.treeNodeToolTip)

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
        QgsMessageLog.logMessage('Finished generating tree structure', MESSAGE_CATEGORY, Qgis.Info)
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
        self.classTreeViewModel.clear()
        QgsMessageLog.logMessage('Started task "{}"'.format(
            "Recursive tree building"), MESSAGE_CATEGORY, Qgis.Info)
        self.rootNode=self.dlg.classTreeViewModel.invisibleRootItem()
        self.dlg.conceptViewTabWidget.setTabText(3, "ClassTree (" + str(len(self.classtreemap)) + ")")
        self.alreadyprocessed=set()
        self.classtreemap["root"]=self.rootNode
        self.buildTree("root",self.classtreemap,self.subclassmap,[])
        self.dlg.classTreeView.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.dlg.classTreeView.header().setStretchLastSection(False)
        self.dlg.classTreeView.header().setMinimumSectionSize(self.dlg.classTreeView.width())
        self.dlg.classTreeView.setSortingEnabled(True)
        self.dlg.classTreeView.sortByColumn(0, Qt.AscendingOrder)
        self.dlg.classTreeView.setSortingEnabled(False)
