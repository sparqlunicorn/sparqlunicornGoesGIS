from ..util.layerutils import LayerUtils
from ..util.sparqlutils import SPARQLUtils
from qgis.core import Qgis,QgsTask, QgsMessageLog
from qgis.PyQt.QtGui import QStandardItem
from qgis.core import Qgis, QgsFeature, QgsVectorLayer, QgsCoordinateReferenceSystem
from qgis.PyQt.QtCore import Qt, QSize
import json

MESSAGE_CATEGORY = 'DataSampleQueryTask'

class DataSampleQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl,dlg,concept,relation,column,row,triplestoreconf,tableWidget,mymap):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl = triplestoreurl
        self.dlg=dlg
        self.column=column
        self.mymap=mymap
        self.triplestoreconf=triplestoreconf
        self.row=row
        self.tableWidget=tableWidget
        self.concept=concept
        self.relation=relation
        self.queryresult=[]
        self.encounteredtypes=set()

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()), MESSAGE_CATEGORY, Qgis.Info)
        QgsMessageLog.logMessage('Started task "{}"'.format(self.concept+" "+self.relation),MESSAGE_CATEGORY, Qgis.Info)
        typeproperty="http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
        if "typeproperty" in self.triplestoreconf:
            typeproperty=self.triplestoreconf["typeproperty"]
        query="SELECT DISTINCT (COUNT(?val) as ?amount) ?val WHERE { ?con <"+typeproperty+"> <" + str(self.concept) + "> . ?con <"+str(self.relation)+"> ?val } GROUP BY ?val LIMIT 100"
        if "geometryproperty" in self.triplestoreconf and self.relation in self.triplestoreconf["geometryproperty"]:
            if type(self.triplestoreconf["geometryproperty"]) is list and len(self.triplestoreconf["geometryproperty"])==2:
                query = "SELECT DISTINCT (COUNT(?val) as ?amount) ?val ?val2 WHERE { ?con <" + typeproperty + "> <" + str(
                    self.concept) + "> . ?con <" + str(self.triplestoreconf["geometryproperty"][0]) + "> ?val . ?con <" + str(self.triplestoreconf["geometryproperty"][1]) + "> ?val2 . } GROUP BY ?val ?val2 LIMIT 100"
        #QgsMessageLog.logMessage('Started task "{}"'.format(str(query).replace("<","").replace(">","")),MESSAGE_CATEGORY, Qgis.Info)
        results = SPARQLUtils.executeQuery(self.triplestoreurl,query,self.triplestoreconf)
        counter=0
        #QgsMessageLog.logMessage('Started task "{}"'.format(results), MESSAGE_CATEGORY, Qgis.Info)
        for result in results["results"]["bindings"]:
            self.queryresult.append({})
            self.queryresult[counter]["value"]=result["val"]["value"]
            self.queryresult[counter]["label"]=SPARQLUtils.labelFromURI(result["val"]["value"])
            self.queryresult[counter]["amount"]=result["amount"]["value"]
            if "val2" in result:
                self.queryresult[counter]["value2"] = result["val2"]["value"]
                self.queryresult[counter]["value2label"] = SPARQLUtils.labelFromURI(result["val2"]["value"])
            if "datatype" in result["val"]:
                self.queryresult[counter]["datatype"]=result["val"]["datatype"]
                self.encounteredtypes.add(self.queryresult[counter]["datatype"])
            else:
                self.encounteredtypes.add("http://www.w3.org/2001/XMLSchema#anyURI")
            counter+=1
        #QgsMessageLog.logMessage('Started task "{}"'.format(self.queryresult), MESSAGE_CATEGORY, Qgis.Info)
        return True

    def finished(self,result):
        resstring=""
        counter=1
        #for res in self.queryresult:
        #    if "http" in res:
        #        resstring+="<a href=\""+str(res)+"\"><b>"+str(self.queryresult[res]["label"])+" ["+str(self.queryresult[res]["amount"])+"]</b></a> "
        #    elif "datatype" in self.queryresult[res]:
        #        resstring+="<a href=\""+str(self.queryresult[res]["datatype"])+"\"><b>"+str(self.queryresult[res]["label"])+" ["+str(self.queryresult[res]["amount"])+"]</b></a> "
        #    else:
        #        resstring+="<b>"+str(self.queryresult[res]["label"])+" ["+str(self.queryresult[res]["amount"])+"]</b> "
        #    if counter%5==0:
        #        resstring+="<br/>"
        #    counter+=1
        if "geometryproperty" in self.triplestoreconf and self.relation in self.triplestoreconf["geometryproperty"]:
            counter=1
            geocollection = {'type': 'FeatureCollection', 'features': []}
            for rel in self.queryresult:
                myGeometryInstanceJSON=None
                if isinstance(self.triplestoreconf["geometryproperty"],str):
                    myGeometryInstanceJSON = LayerUtils.processLiteral(rel["value"],
                                                                       (rel["datatype"] if "datatype" in rel else ""),
                                                                       True, self.triplestoreconf)
                elif type(self.triplestoreconf["geometryproperty"]) is list and len(self.triplestoreconf["geometryproperty"])==2:
                    myGeometryInstanceJSON=LayerUtils.processLiteral("POINT(" + str(float(rel["value"])) + " " + str(
                        float(rel["value2"])) + ")", "wkt", True, self.triplestoreconf)
                if myGeometryInstanceJSON!=None:
                    geojson = {'id': str(self.concept)+"_"+str(counter), 'type': 'Feature', 'properties': {},
                        'geometry': json.loads(myGeometryInstanceJSON)}
                    geocollection["features"].append(geojson)
                    counter+=1
            QgsMessageLog.logMessage(str(geocollection), MESSAGE_CATEGORY, Qgis.Info)
            self.features = QgsVectorLayer(json.dumps(geocollection), str(self.concept),"ogr")
            self.features.setCrs(QgsCoordinateReferenceSystem(4326))
            layerlist=self.mymap.layers()
            layerlist.insert(0,self.features)
            self.mymap.setLayers(layerlist)
            self.mymap.setCurrentLayer(self.features)
            self.features.selectAll()
            self.mymap.zoomToSelected(self.features)
            self.features.removeSelection()
            self.dlg.resize(QSize(self.dlg.width() + 250, self.dlg.height()))
            self.mymap.show()
        reslabelprop="label"
        if self.triplestoreconf["geometryproperty"][1]==self.relation:
            reslabelprop="value2label"
        for res in self.queryresult:
            if "http" in res:
                resstring+=str(res[reslabelprop])+" ["+str(res["amount"])+"] "
            elif "datatype" in res:
                resstring+=str(res[reslabelprop])+" ["+str(res["amount"])+"] "
            else:
                resstring+=str(res[reslabelprop])+" ["+str(res["amount"])+"] "
            if counter%5==0:
                resstring+="\n"
            counter+=1
        item = QStandardItem()
        item.setText(resstring)
        self.tableWidget.takeItem(self.row,self.column)
        self.tableWidget.setItem(self.row,self.column,item)