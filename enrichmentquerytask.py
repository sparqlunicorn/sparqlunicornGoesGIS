from time import sleep
from rdflib import *
import json
import requests
from qgis.PyQt.QtCore import QVariant
from qgis.core import Qgis,QgsField
from qgis.PyQt.QtWidgets import QMessageBox,QTableWidgetItem
from rdflib.plugins.sparql import prepareQuery
from SPARQLWrapper import SPARQLWrapper, JSON, POST, GET
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog,
    )

MESSAGE_CATEGORY = 'EnrichmentQueryTask'

## Executes an enrichment task on a given layer with a given configuration.
class EnrichmentQueryTask(QgsTask):

    def __init__(self, description, triplestoreurl,columnmap,layer,strategy,language,row,originalRowCount,item,table,idfield,idprop,propertyy,content,progress):
        super().__init__(description, QgsTask.CanCancel)
        self.exception = None
        self.triplestoreurl=triplestoreurl
        self.labels=None
        self.row=row
        self.propertyy=propertyy
        self.content=content
        self.item=item
        self.table=table
        self.idfield=idfield
        self.idprop=idprop
        self.originalRowCount=originalRowCount
        self.progress=progress
        self.language=language
        self.strategy=strategy
        self.layer=layer
        self.urilist=None
        self.sortedatt=None
        self.columnmap=columnmap
        self.resultmap={}
        self.results=None

    ## Executes the enrichment task.
    # @param self The object pointer
    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(
                                     self.description()),
                                 MESSAGE_CATEGORY, Qgis.Info)
        attlist={}
        attlist[self.item]=[]
        attlist[self.idfield]=[]
        for f in self.layer.getFeatures():
            if self.item in f:
                attlist[self.item].append(f[self.item])
            attlist[self.idfield].append(f[self.idfield])
            query=""
            if self.content=="Enrich URI": 
                query+="SELECT ?item WHERE {\n"
            elif self.content=="Enrich Value" or self.strategy=="Enrich Both":
                query+="SELECT ?item ?val ?valLabel ?vals WHERE {\n"
            query+="VALUES ?vals { "
            print(attlist)
            for it in attlist[self.idfield]:
                if str(it).startswith("http"):
                    query+="<"+str(it)+"> "
                elif self.idprop=="http://www.w3.org/2000/01/rdf-schema#label" and self.language!=None and self.language!="":
                    query+="\""+str(it)+"\"@"+self.language+" "
                else:
                    query+="\""+str(it)+"\" "
            query+=" } . \n"
            proppp=self.propertyy.data(1)
            if self.propertyy.data(1).startswith("//"):
                proppp="http:"+proppp
            if self.table.item(self.row, 7).text()!="" and "wikidata" in self.triplestoreurl:
                query+="?item wdt:P31 <"+self.table.item(self.row, 7).text()+"> .\n"
            else:
                query+="?item rdf:type <"+self.table.item(self.row, 7).text()+"> .\n"
            query+="?item <"+self.idprop+"> ?vals .\n"
            query+="?item <"+proppp+"> ?val . \n"
            if (self.content=="Enrich Value" or self.content=="Enrich Both") and not "wikidata" in self.triplestoreurl:
                query+="OPTIONAL{ ?val rdfs:label ?valLabel }"
            elif (self.content=="Enrich Value" or self.content=="Enrich Both") and "wikidata" in self.triplestoreurl:
                query+="SERVICE wikibase:label { bd:serviceParam wikibase:language \"[AUTO_LANGUAGE],"+self.language+"\". }\n"
            query+="} ORDER BY ?item "
            print(query)
            print(self.triplestoreurl)
            try:
                sparql = SPARQLWrapper(self.triplestoreurl, agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
                sparql.setQuery(query)
                sparql.setMethod(POST)
                print("now sending query")
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
            except Exception as e: 
                try:
                    sparql = SPARQLWrapper(self.triplestoreurl, agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
                    sparql.setQuery(query)
                    sparql.setMethod(GET)
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                except Exception as e:
                    #msgBox=QMessageBox()
                    #msgBox.setText("The following exception occurred: "+str(e))
                    #msgBox.exec()
                    return False
            print(str(results))
            #resultcounter=0
            for resultcounter in results["results"]["bindings"]:
                if self.content=="Enrich Value":
                    self.resultmap[resultcounter["vals"]["value"]]=resultcounter["valLabel"]["value"]
                elif self.content=="Enrich URI":
                    self.resultmap[resultcounter["vals"]["value"]]=resultcounter["val"]["value"]
                else:
                    self.resultmap[resultcounter["vals"]["value"]]=resultcounter["valLabel"]["value"]+";"+resultcounter["val"]["value"]
                print(str(self.resultmap))
        return True

    ## Detects the type of a column which is to be entered into a QGIS vector layer.
    #  @param self The object pointer.
    #  @param table the layer to analyze
    # the column to consider
    def detectColumnType(self,table,col):
        intcount=0
        doublecount=0
        for row in range(table.rowCount()):
            if self.item(row,col)=="":
                intcount+=1
                doublecount+=1
                continue
            if self.item(row, col).text().isdigit():
                intcount+=1
            try:
                float(self.item(row, col).text())
                doublecount+=1
            except:
                print("")
        if intcount==self.dlg.enrichTable.rowCount():
            return QVariant.Integer
        if doublecount==self.dlg.enrichTable.rowCount():
            return QVariant.Double
        return QVariant.String

    ## Writes the result of the enrichment task to the result table in the main view.
    # @param self The object pointer
    # @param result the result indicator of the calculation
    def finished(self, result):
        rowww=0
        if self.row>=self.originalRowCount:
            self.layer.dataProvider().addAttributes([QgsField(self.item,QVariant.String)])
            self.layer.updateFields()
        fieldnames = [field.name() for field in self.layer.fields()]
        print(str(self.layer.dataProvider().capabilitiesString()))
        for f in self.layer.getFeatures():
            if rowww>=self.table.rowCount():
                self.table.insertRow(rowww)
                if f[self.idfield] in self.resultmap:
                    if strategy=="Merge":
                        newitem=QTableWidgetItem(str(f[item])+str(self.resultmap[f[self.idfield]]))
                    elif strategy=="Keep Local":
                        if f[item]==None:
                            newitem=QTableWidgetItem(str(self.resultmap[f[self.idfield]]))
                        else:
                            newitem=QTableWidgetItem(str(f[self.item]))
                    elif strategy=="Ask User":
                        newitem=QTableWidgetItem(str(f[self.item])+";"+str(self.resultmap[f[self.idfield]]))
                    elif strategy=="Keep Remote":
                        if not f[idfield] in self.resultmap or self.resultmap[f[self.idfield]]==None:
                            newitem=QTableWidgetItem(str(f[self.item]))
                        else:
                            newitem=QTableWidgetItem(str(self.resultmap[f[self.idfield]]))
                    else:
                        newitem=QTableWidgetItem(str(self.resultmap[f[self.idfield]]))
                    self.table.setItem(rowww,row,newitem)
                    #if ";" in str(newitem):
                    #    newitem.setBackground(QColor.red)
                    print(str(newitem))
                    rowww+=1  
            else:
                rowww=0            
                for f in self.layer.getFeatures():
                    if rowww>=self.table.rowCount():
                        self.table.insertRow(rowww)
                    #if item in f:
                    newitem=QTableWidgetItem(str(f[self.item]))
                    self.table.setItem(rowww,self.row,newitem)
                    #if ";" in str(newitem):
                    #    newitem.setBackground(QColor.red)
                    print(str(newitem))
                    rowww+=1
        self.layer.commitChanges()
        self.progress.close()
