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

MESSAGE_CATEGORY = 'RandomIntegerSumTask'

class EnrichmentQueryTask(QgsTask):
    """This shows how to subclass QgsTask"""

    def __init__(self, description, triplestoreurl,query,searchTerm,prefixes,searchResult):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl=triplestoreurl
        self.query=query
        self.prefixes=prefixes
        self.labels=None
        self.urilist=None
        self.sortedatt=None
        self.searchTerm=searchTerm
        self.searchResult=searchResult
        self.results=None

    def run(self):
        """Here you implement your heavy lifting.
        Should periodically test for isCanceled() to gracefully
        abort.
        This method MUST return True or False.
        Raising exceptions will crash QGIS, so we handle them
        internally and raise them in self.finished
        """
        QgsMessageLog.logMessage('Started task "{}"'.format(
                                     self.description()),
                                 MESSAGE_CATEGORY, Qgis.Info)
        if self.searchTerm=="":
            return False
        concept="<"+self.searchTerm+">"
		#"select (COUNT(distinct ?con) AS ?countcon) (COUNT(?rel) AS ?countrel) ?rel WHERE { ?con wdt:P31 "+str(concept)+" . ?con wdt:P625 ?coord . ?con wdt:P17  "+str(inarea)+" . ?con ?rel ?val . } GROUP BY ?rel ORDER BY DESC(?countrel)"
        sparql = SPARQLWrapper(self.triplestoreurl, agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
        sparql.setQuery("".join(self.prefixes) + self.query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        self.searchResult.clear()
        if len(results["results"]["bindings"])==0:
            return False
        maxcons=int(results["results"]["bindings"][0]["countcon"]["value"])
        attlist={}
        self.urilist={}
        for result in results["results"]["bindings"]:
            attlist[result["rel"]["value"][result["rel"]["value"].rfind('/')+1:]]=round((int(result["countrel"]["value"])/maxcons)*100,2)
            self.urilist[result["rel"]["value"][result["rel"]["value"].rfind('/')+1:]]=result["rel"]["value"]
        self.sortedatt = sorted(attlist.items(),reverse=True, key=lambda kv: kv[1])
        self.labels={}
        postdata={}
        postdata["language"]="en"
        postdata["format"]="json"
        postdata["action"]="wbgetentities"
        atts=[""]
        attcounter=0
        count=0
        for att in attlist.keys():
            #if att.startswith("P") and count==50:
            #    atts[attcounter]=atts[attcounter][:-1]
            #    attcounter+=1
            #    atts.append("")
            #    count=0
            #    atts[attcounter]+=att+"|"
            if att.startswith("P") and count<50:
                atts[attcounter]+=att+"|"
                count+=1
        #msgBox=QMessageBox()
        #msgBox.setText(str(atts))
        #msgBox.exec()  
        atts[0]=atts[0][:-1]
        i=0
        for att in atts:
            url="https://www.wikidata.org/w/api.php" #?action=wbgetentities&format=json&language=en&ids="+atts
            postdata["ids"]=att
            #msgBox=QMessageBox()
            #msgBox.setText(str(postdata))
            #msgBox.exec()
            myResponse = json.loads(requests.post(url,postdata).text)
            #msgBox=QMessageBox()
            #msgBox.setText(str(myResponse))
            #msgBox.exec()
            for ent in myResponse["entities"]:
                print(ent)
                if "en" in myResponse["entities"][ent]["labels"]:
                    self.labels[ent]=myResponse["entities"][ent]["labels"]["en"]["value"]               
                i=i+1
        return True

    def finished(self, result):
        """
        This function is automatically called when the task has
        completed (successfully or not).
        You implement finished() to do whatever follow-up stuff
        should happen after the task is complete.
        finished is always called from the main thread, so it's safe
        to do GUI operations and raise Python exceptions here.
        result is the return value from self.run.
        """
        #msgBox=QMessageBox()
        #msgBox.setText(str("Task is finished!"))
        #msgBox.exec()
        counter=0
        for att in self.sortedatt:
            if att[1]<1:
                continue
            if att[0] in self.labels:
                item=QListWidgetItem()
                item.setText(self.labels[att[0]]+" ("+str(att[1])+"%)")
                item.setData(1,self.urilist[att[0]])
                self.searchResult.addItem(item)
                counter+=1
            else:
                item=QListWidgetItem()
                item.setText(att[0]+" ("+str(att[1])+"%)")
                item.setData(1,self.urilist[att[0]])
                self.searchResult.addItem(item)
