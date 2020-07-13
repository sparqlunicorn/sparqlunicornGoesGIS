from time import sleep
from rdflib import *
import json
import requests
from qgis.core import Qgis
from qgis.PyQt.QtWidgets import QListWidgetItem,QMessageBox
from rdflib.plugins.sparql import prepareQuery
from SPARQLWrapper import SPARQLWrapper, JSON, POST, GET
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
    )

MESSAGE_CATEGORY = 'GeoConceptsQueryTask'

class GeoConceptsQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl,query,triplestoreconf,layerconcepts,queryvar,getlabels,layercount):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl=triplestoreurl
        self.triplestoreconf=triplestoreconf
        self.query=query
        self.layercount=layercount
        self.getlabels=getlabels
        self.queryvar=queryvar
        self.layerconcepts=layerconcepts
        self.amountoflabels=-1
        self.resultlist=[]
        self.viewlist=[]

    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(
                                     self.description()),
                                 MESSAGE_CATEGORY, Qgis.Info)
        sparql = SPARQLWrapper(self.triplestoreurl, agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
        sparql.setQuery(self.query)
        print("now sending query")
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            self.viewlist.append(str(result[self.queryvar]["value"]))
        print(self.viewlist)
        #self.layercount.setText("["+str(len(viewlist))+"]")
        if self.getlabels and "classlabelquery" in self.triplestoreconf and self.triplestoreconf["classlabelquery"]!="":
            labels=self.getLabelsForClasses(viewlist,self.triplestoreconf["classlabelquery"])
            print(labels)
            self.amountoflabels=len(labels)
            i=0
            sorted_labels=sorted(labels.items(),key=lambda x:x[1])
            for lab in sorted_labels:
                self.resultlist.append(labels[lab[0]]+"("+lab[0]+")")
                i=i+1
        return True

    ## Executes a SPARQL endpoint specific query to find labels for given classes. The query may be configured in the configuration file.
    #  @param self The object pointer.
    #  @param classes array of classes to find labels for
    #  @param query the class label query
    def getLabelsForClasses(self,classes,query):
        result={}
        query=self.triplestoreconf["classlabelquery"]
        #url="https://www.wikidata.org/w/api.php?action=wbgetentities&props=labels&ids="
        if "SELECT" in query:
            vals="VALUES ?class { "
            for qid in classes:
                vals+=qid+" "
            vals+="}\n"
            query=query.replace("%%concepts%%",vals)
            sparql = SPARQLWrapper(self.triplestoreurl, agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            for res in results["results"]["bindings"]:
                result[res["class"]["value"]]=res["label"]["value"]
        else:
            url=self.triplestoreconf["classlabelquery"]
            i=0
            qidquery=""
            for qid in classes:
                if "Q" in qid:
                    qidquery+="Q"+qid.split("Q")[1]
                if (i%50)==0:
                    print(url.replace("%%concepts%%",qidquery))
                    myResponse = json.loads(requests.get(url.replace("%%concepts%%",qidquery)).text)
                    print(myResponse)
                    for ent in myResponse["entities"]:
                        print(ent)
                        if "en" in myResponse["entities"][ent]["labels"]:
                            result[ent]=myResponse["entities"][ent]["labels"]["en"]["value"]                
                    qidquery=""
                else:
                    qidquery+="|"
                i=i+1
        return result

    def finished(self, result):
        if len(self.resultlist)>0:
            for concept in self.resultlist:
                self.layerconcepts.addItem(concept)
        elif len(self.viewlist)>0:
            for concept in self.viewlist:
                self.layerconcepts.addItem(concept)
        if self.amountoflabels!=-1:
            self.layercount.setText("["+str(self.amountoflabels)+"]")
