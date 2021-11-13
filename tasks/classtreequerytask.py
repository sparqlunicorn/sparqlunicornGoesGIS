from ..util.sparqlutils import SPARQLUtils
from qgis.core import Qgis
from qgis.PyQt.QtCore import QSettings, QItemSelectionModel, Qt
from qgis.PyQt.QtGui import QStandardItem
from qgis.PyQt.QtWidgets import QStyle
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog
)

MESSAGE_CATEGORY = 'ClassTreeQueryTask'

class ClassTreeQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl,dlg,treeNode,graph=None):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.dlg=dlg
        self.graph=graph
        self.treeNode=treeNode
        self.classTreeViewModel=self.dlg.classTreeViewModel
        self.amount=-1
        self.query="""PREFIX owl: <http://www.w3.org/2002/07/owl#>\n
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n
                    SELECT DISTINCT ?subject ?label ?supertype ?hasgeo\n
                    WHERE {\n"""
        if "highload" in self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()] and self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["highload"]:
            self.query+="{ ?subject <"+str(self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["typeproperty"])+"> owl:Class .  } UNION { ?individual <"+self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["typeproperty"]+"> ?subject . } .\n"
        elif "geometryproperty" in self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()] and self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["geometryproperty"]=="http://www.opengis.net/ont/geosparql#hasGeometry":
            self.query+="{ ?subject <"+str(self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["typeproperty"])+"> owl:Class .  } UNION { ?individual <"+str(self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["typeproperty"])+"> ?subject . OPTIONAL {BIND(EXISTS {?individual <"+str(self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["geometryproperty"])+"> ?lit . ?lit ?a ?wkt } AS ?hasgeo)}} .\n"
        else:
            self.query+="{ ?subject <"+str(self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["typeproperty"])+"> owl:Class .  } UNION { ?individual <"+self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["typeproperty"]+"> ?subject . OPTIONAL {BIND(EXISTS {?individual <"+str(self.dlg.triplestoreconf[self.dlg.comboBox.currentIndex()]["geometryproperty"])+"> ?wkt } AS ?hasgeo)}} .\n"
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
            results = SPARQLUtils.executeQuery(self.triplestoreurl,self.query)
        else:
            results=self.graph.query(self.query)
        if results==False:
            return False
        hasparent={}
        for result in results["results"]["bindings"]:
            QgsMessageLog.logMessage('Started task "{}"'.format(str(result)), MESSAGE_CATEGORY, Qgis.Info)
            subval=result["subject"]["value"]
            if subval==None or subval=="":
                continue
            if subval not in self.classtreemap:
                self.classtreemap[subval]=QStandardItem()
                self.classtreemap[subval].setData(subval, 256)
                if "label" in result:
                    if "hasgeo" in result:
                        self.classtreemap[subval].setText(
                        result["label"]["value"]+" [GEO]")
                    else:
                        self.classtreemap[subval].setText(
                        result["label"]["value"])
                else:
                    if "hasgeo" in result:
                        self.classtreemap[subval].setText(
                        result["subject"]["value"][result["subject"]["value"].rfind('/') + 1:]+" [GEO]")
                    else:
                        self.classtreemap[subval].setText(
                        result["subject"]["value"][result["subject"]["value"].rfind('/') + 1:])
                self.classtreemap[subval].setIcon(self.dlg.style().standardIcon(getattr(QStyle, "SP_ToolBarHorizontalExtensionButton")))
            if subval not in self.subclassmap:
                self.subclassmap[subval]=set()
            if "supertype" in result:
                if not result["supertype"]["value"] in self.subclassmap:
                    self.subclassmap[result["supertype"]["value"]] = set()
                if result["supertype"]["value"]!=subval and not result["supertype"]["value"] in self.subclassmap[subval]:
                    self.subclassmap[result["supertype"]["value"]].add(subval)
                    hasparent[subval]=True
                #else:
                #    self.subclassmap["root"].add(subval)
            #else:
            #    self.subclassmap["root"].add(subval)
        for cls in self.classtreemap:
            if cls not in hasparent and cls!="root":
                self.subclassmap["root"].add(cls)
        QgsMessageLog.logMessage('Started task "{}"'.format(str(self.subclassmap)), MESSAGE_CATEGORY, Qgis.Info)
        QgsMessageLog.logMessage('Started task "{}"'.format(str(self.classtreemap)), MESSAGE_CATEGORY, Qgis.Info)
        return True

    def buildTree(self,curNode,classtreemap,subclassmap,mypath):
        if curNode not in self.alreadyprocessed:
            for item in subclassmap[curNode]:
                if item in classtreemap and item not in self.alreadyprocessed:
                    QgsMessageLog.logMessage('Started task "{}"'.format("Append: "+str(curNode)+" - "+str(item)), MESSAGE_CATEGORY,
                                         Qgis.Info)
                    classtreemap[curNode].appendRow(classtreemap[item])
                if item!=curNode and item not in mypath:
                    self.buildTree(item,classtreemap,subclassmap,mypath+[item])
            self.alreadyprocessed.add(curNode)


    def finished(self, result):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.treeNode.text()+" ["+str(self.amount)+"]"), MESSAGE_CATEGORY, Qgis.Info)
        self.rootNode=self.dlg.classTreeViewModel.invisibleRootItem()
        self.dlg.conceptViewTabWidget.setTabText(3, "ClassTree (" + str(len(self.classtreemap)) + ")")
        self.alreadyprocessed=set()
        self.classtreemap["root"]=self.rootNode
        self.buildTree("root",self.classtreemap,self.subclassmap,[])
        self.dlg.classTreeView.setSortingEnabled(True)
        self.dlg.classTreeView.sortByColumn(0, Qt.AscendingOrder);
        self.dlg.classTreeView.setSortingEnabled(False)
