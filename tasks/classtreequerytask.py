import urllib
from qgis.core import Qgis
from qgis.PyQt.QtCore import QSettings, QItemSelectionModel
from qgis.PyQt.QtGui import QStandardItem
from qgis.PyQt.QtWidgets import QStyle
from SPARQLWrapper import SPARQLWrapper, JSON, GET
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog
)

MESSAGE_CATEGORY = 'ClassTreeQueryTask'

class ClassTreeQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl,dlg,treeNode):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.dlg=dlg
        self.treeNode=treeNode
        self.geoTreeViewModel=self.dlg.geoTreeViewModel
        self.amount=-1
        s = QSettings()  # getting proxy from qgis options settings
        self.proxyEnabled = s.value("proxy/proxyEnabled")
        self.proxyType = s.value("proxy/proxyType")
        self.proxyHost = s.value("proxy/proxyHost")
        self.proxyPort = s.value("proxy/proxyPort")
        self.proxyUser = s.value("proxy/proxyUser")
        self.proxyPassword = s.value("proxy/proxyPassword")
        #
        self.query="""PREFIX owl: <http://www.w3.org/2002/07/owl#>\n
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n
                    SELECT DISTINCT ?subject ?label ?supertype ?hasgeo\n
                    WHERE {\n
                       { ?subject <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> owl:Class .  } UNION { ?individual <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?subject . OPTIONAL {BIND(EXISTS {?individual <http://www.opengis.net/ont/geosparql#hasGeometry>/<http://www.opengis.net/ont/geosparql#asWKT> ?wkt } AS ?hasgeo)}} .\n
                       OPTIONAL { ?subject rdfs:subClassOf ?supertype } .\n
                       OPTIONAL { ?subject <http://www.w3.org/2000/01/rdf-schema#label> ?label }.\n
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
        if self.proxyHost != None and self.proxyHost != "" and self.proxyPort != None and self.proxyPort != "":
            QgsMessageLog.logMessage('Proxy? ' + str(self.proxyHost), MESSAGE_CATEGORY, Qgis.Info)
            proxy = urllib.request.ProxyHandler({'http': self.proxyHost})
            opener = urllib.request.build_opener(proxy)
            urllib.request.install_opener(opener)
        sparql = SPARQLWrapper(self.triplestoreurl,
                               agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
        QgsMessageLog.logMessage('Started task "{}"'.format(str(self.query)), MESSAGE_CATEGORY, Qgis.Info)
        sparql.setQuery(self.query)
        sparql.setMethod(GET)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        self.classtreemap={"root":self.treeNode}
        self.subclassmap={"root":set()}
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
                if result["supertype"]["value"]!=subval:
                    self.subclassmap[result["supertype"]["value"]].add(subval)
                else:
                    self.subclassmap["root"].add(subval)
            else:
                self.subclassmap["root"].add(subval)
        QgsMessageLog.logMessage('Started task "{}"'.format(str(self.subclassmap)), MESSAGE_CATEGORY, Qgis.Info)
        QgsMessageLog.logMessage('Started task "{}"'.format(str(self.classtreemap)), MESSAGE_CATEGORY, Qgis.Info)
        return True

    def buildTree(self,curNode,classtreemap,subclassmap):
        if curNode not in self.alreadyprocessed:
            for item in subclassmap[curNode]:
                if item in classtreemap and item not in self.alreadyprocessed:
                    QgsMessageLog.logMessage('Started task "{}"'.format("Append: "+str(curNode)+" - "+str(item)), MESSAGE_CATEGORY,
                                         Qgis.Info)
                    classtreemap[curNode].appendRow(classtreemap[item])
                self.buildTree(item,classtreemap,subclassmap)
            self.alreadyprocessed.add(curNode)


    def finished(self, result):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.treeNode.text()+" ["+str(self.amount)+"]"), MESSAGE_CATEGORY, Qgis.Info)
        self.alreadyprocessed=set()
        self.dlg.classTreeViewModel.clear()
        self.rootNode=self.dlg.classTreeViewModel.invisibleRootItem()
        self.classtreemap["root"]=self.rootNode
        self.buildTree("root",self.classtreemap,self.subclassmap)