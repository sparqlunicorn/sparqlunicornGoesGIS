from ..util.sparqlutils import SPARQLUtils
from qgis.PyQt.QtGui import QStandardItem
from qgis.core import Qgis,QgsTask, QgsMessageLog

MESSAGE_CATEGORY = 'InstanceListQueryTask'

class InstanceListQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl,dlg,treeNode,triplestoreconf):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.dlg=dlg
        self.hasgeocount=0
        self.triplestoreconf=triplestoreconf
        self.treeNode=treeNode
        self.queryresult={}

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        typeproperty="http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        if "typeproperty" in self.triplestoreconf:
            typeproperty=self.triplestoreconf["typeproperty"]
        nodetype=self.treeNode.data(257)
        if nodetype==SPARQLUtils.collectionclassnode:
            QgsMessageLog.logMessage('Started task "{}"'.format(
                    "SELECT ?con ?label WHERE { " + str(
                        self.treeNode.data(256)) + "http://www.w3.org/2000/01/rdf-schema#member ?con . OPTIONAL { ?con <http://www.w3.org/2000/01/rdf-schema#label> ?label . } }"), MESSAGE_CATEGORY, Qgis.Info)
            thequery="SELECT ?con ?label WHERE {  <" + str(
                        self.treeNode.data(256)) + "> <http://www.w3.org/2000/01/rdf-schema#member> ?con . OPTIONAL { ?con <http://www.w3.org/2000/01/rdf-schema#label> ?label . } }"
        else:
            if "geometryproperty" in self.triplestoreconf:
                if type(self.triplestoreconf["geometryproperty"]) is list:
                    geometryproperty=self.triplestoreconf["geometryproperty"][0]
                else:
                    geometryproperty = self.triplestoreconf["geometryproperty"]
                if isinstance(self.triplestoreurl, str):
                    QgsMessageLog.logMessage('Started task "{}"'.format(
                        "SELECT ?con ?label ?hasgeo WHERE { ?con " + typeproperty + " " + str(
                            self.treeNode.data(
                                256)) + " . OPTIONAL { ?con <http://www.w3.org/2000/01/rdf-schema#label> ?label . } BIND(EXISTS {?con " + str(
                            geometryproperty) + " ?wkt } AS ?hasgeo)}"), MESSAGE_CATEGORY,
                        Qgis.Info)
                    thequery = "SELECT ?con ?label ?hasgeo WHERE { ?con <" + typeproperty + "> <" + str(
                        self.treeNode.data(
                            256)) + "> . OPTIONAL { ?con <http://www.w3.org/2000/01/rdf-schema#label> ?label . } BIND(EXISTS {?con <" + str(
                        geometryproperty) + "> ?wkt } AS ?hasgeo)}"
                else:
                    thequery = "SELECT ?con ?label ?hasgeo WHERE { ?con <" + typeproperty + "> <" + str(
                        self.treeNode.data(
                            256)) + "> . OPTIONAL { ?con <http://www.w3.org/2000/01/rdf-schema#label> ?label . } OPTIONAL { ?con <" + str(
                        geometryproperty) + "> ?hasgeo } }"
            else:
                QgsMessageLog.logMessage('Started task "{}"'.format(
                    "SELECT ?con ?label WHERE { ?con " + typeproperty + " " + str(
                        self.treeNode.data(
                            256)) + " . OPTIONAL { ?con <http://www.w3.org/2000/01/rdf-schema#label> ?label . }}"), MESSAGE_CATEGORY,
                    Qgis.Info)
                thequery = "SELECT ?con ?label WHERE { ?con <" + typeproperty + "> <" + str(
                    self.treeNode.data(
                        256)) + "> . OPTIONAL { ?con <http://www.w3.org/2000/01/rdf-schema#label> ?label . }}"
        results = SPARQLUtils.executeQuery(self.triplestoreurl,thequery,self.triplestoreconf)
        QgsMessageLog.logMessage("Query results: " + str(results), MESSAGE_CATEGORY, Qgis.Info)
        if results!=False:
            for result in results["results"]["bindings"]:
                if result["con"]["value"] not in self.queryresult:
                    self.queryresult[result["con"]["value"]]={}
                if "hasgeo" in result and (result["hasgeo"]["value"]=="true" or result["hasgeo"]["value"]=="1" or not isinstance(self.triplestoreurl, str)):
                    self.queryresult[result["con"]["value"]]["hasgeo"] = True
                    self.hasgeocount+=1
                    QgsMessageLog.logMessage('Started task "{}"'.format(
                        str(result["con"]["value"])+" "+str(self.hasgeocount) + " " + str(len(self.queryresult))),
                        MESSAGE_CATEGORY, Qgis.Info)
                elif "hasgeo" not in self.queryresult[result["con"]["value"]]:
                    self.queryresult[result["con"]["value"]]["hasgeo"] = False
                if "label" in result:
                    self.queryresult[result["con"]["value"]]["label"] = result["label"]["value"]+" ("+SPARQLUtils.labelFromURI(result["con"]["value"],self.triplestoreconf["prefixesrev"])+")"
                else:
                    self.queryresult[result["con"]["value"]]["label"]=SPARQLUtils.labelFromURI(result["con"]["value"],self.triplestoreconf["prefixesrev"])
        return True

    def finished(self, result):
        QgsMessageLog.logMessage('Started task "{}"'.format(
            self.treeNode.text()+" "+str(self.hasgeocount)+" "+str(len(self.queryresult))), MESSAGE_CATEGORY, Qgis.Info)
        if self.treeNode.data(258)==None:
            self.treeNode.setData(str(len(self.queryresult)),258)
            self.treeNode.setText(self.treeNode.text()+" ["+str(len(self.queryresult))+"]")
        if(self.hasgeocount>0 and self.hasgeocount<len(self.queryresult)) and self.treeNode.data(257)!=SPARQLUtils.collectionclassnode:
            self.treeNode.setIcon(SPARQLUtils.halfgeoclassicon)
        elif self.hasgeocount==0 and self.treeNode.data(257)!=SPARQLUtils.collectionclassnode:
            self.treeNode.setIcon(SPARQLUtils.classicon)
        self.treeNode.setData(SPARQLUtils.instancesloadedindicator,259)
        for concept in self.queryresult:
            item = QStandardItem()
            item.setData(concept, 256)
            item.setText(self.queryresult[concept]["label"])
            QgsMessageLog.logMessage(str(self.queryresult[concept]["hasgeo"]), MESSAGE_CATEGORY,
                Qgis.Info)
            if (self.treeNode.data(257)==SPARQLUtils.geoclassnode \
                    or self.treeNode.data(257)==SPARQLUtils.collectionclassnode) and self.queryresult[concept]["hasgeo"]:
                item.setData(SPARQLUtils.geoinstancenode,257)
                item.setIcon(SPARQLUtils.geoinstanceicon)
                item.setToolTip("GeoInstance " + str(item.text()) + ": <br>" + SPARQLUtils.treeNodeToolTip)
            else:
                item.setData(SPARQLUtils.instancenode,257)
                item.setIcon(SPARQLUtils.instanceicon)
                item.setToolTip("Instance " + str(item.text()) + ": <br>" + SPARQLUtils.treeNodeToolTip)
            self.treeNode.appendRow(item)
