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

MESSAGE_CATEGORY = 'EnrichmentQueryTask'

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
        QgsMessageLog.logMessage('Started task "{}"'.format(
                                     self.description()),
                                 MESSAGE_CATEGORY, Qgis.Info)
        layers = QgsProject.instance().layerTreeRoot().children()
        selectedLayerIndex = self.dlg.chooseLayerEnrich.currentIndex()
        self.enrichLayer = layers[selectedLayerIndex].layer().clone()
        attlist={}
        itemlist=[]
        propertylist=[]
        excludelist=[]
        resultmap={}
        self.dlg.enrichTableResult.clear()
        self.dlg.enrichTableResult.setRowCount(0)		
        self.dlg.enrichTableResult.setColumnCount(self.dlg.enrichTable.rowCount())
        fieldnames=[]
        for row in range(self.dlg.enrichTable.rowCount()):
            fieldnames.append(self.dlg.enrichTable.item(row, 0).text())
        self.dlg.enrichTableResult.setHorizontalHeaderLabels(fieldnames)
        for row in range(self.dlg.enrichTable.rowCount()):
            idfield=self.dlg.enrichTable.cellWidget(row, 5).currentText()
            idprop=self.dlg.enrichTable.item(row, 6).text()
            if idprop==None or idprop=="":
                msgBox=QMessageBox()
                msgBox.setText("ID Property has not been specified for column "+str(self.dlg.enrichTable.item(row, 0).text()))
                msgBox.exec()
                return
            item = self.dlg.enrichTable.item(row, 0).text()
            propertyy=self.dlg.enrichTable.item(row, 1)
            triplestoreurl=""
            if self.dlg.enrichTable.item(row, 2)!=None:
                triplestoreurl=self.dlg.enrichTable.item(row, 2).text()
                print(self.dlg.enrichTable.item(row, 2).text())
            strategy = self.dlg.enrichTable.cellWidget(row, 3).currentText()
            content=""
            if self.dlg.enrichTable.cellWidget(row, 4)!=None:
                content = self.dlg.enrichTable.cellWidget(row, 4).currentText()
            if item!=idfield:
                propertylist.append(self.dlg.enrichTable.item(row, 1)) 
            if strategy=="Exclude":
                excludelist.append(row)
            if strategy!="No Enrichment" and propertyy!=None:
                if row>=self.originalRowCount:
                    self.enrichLayer.dataProvider().addAttributes([QgsField(item,QVariant.String)])
                    self.enrichLayer.updateFields()
                fieldnames = [field.name() for field in self.enrichLayer.fields()]
                self.enrichLayer.startEditing()
                print(str(self.enrichLayer.dataProvider().capabilitiesString()))
                print(str(fieldnames))
                print("Enrichment for "+propertyy.text())
                print("Item: "+idfield)
                itemlist.append(item)
                attlist[item]=[]
                attlist[idfield]=[]
                for f in self.enrichLayer.getFeatures():
                    if item in f:
                        attlist[item].append(f[item])
                    attlist[idfield].append(f[idfield])
                query=""
                if content=="Enrich URI": 
                    query+="SELECT ?item WHERE {\n"
                elif content=="Enrich Value" or content=="Enrich Both":
                    query+="SELECT ?item ?val ?valLabel ?vals WHERE {\n"
                query+="VALUES ?vals { "
                print(attlist)
                for it in attlist[idfield]:
                    if str(it).startswith("http"):
                        query+="<"+str(it)+"> "
                    elif idprop=="http://www.w3.org/2000/01/rdf-schema#label" and self.dlg.enrichTable.item(row, 8).text()!="":
                        query+="\""+str(it)+"\"@"+self.dlg.enrichTable.item(row, 8).text()+" "
                    else:
                        query+="\""+str(it)+"\" "
                query+=" } . \n"
                proppp=propertyy.data(1)
                if propertyy.data(1).startswith("//"):
                    proppp="http:"+proppp
                if self.dlg.enrichTable.item(row, 7).text()!="" and "wikidata" in triplestoreurl:
                    query+="?item wdt:P31 <"+self.dlg.enrichTable.item(row, 7).text()+"> .\n"
                else:
                    query+="?item rdf:type <"+self.dlg.enrichTable.item(row, 7).text()+"> .\n"
                query+="?item <"+idprop+"> ?vals .\n"
                query+="?item <"+proppp+"> ?val . \n"
                if (content=="Enrich Value" or content=="Enrich Both") and not "wikidata" in triplestoreurl:
                    query+="OPTIONAL{ ?val rdfs:label ?valLabel }"
                elif (content=="Enrich Value" or content=="Enrich Both") and "wikidata" in triplestoreurl:
                    query+="SERVICE wikibase:label { bd:serviceParam wikibase:language \"[AUTO_LANGUAGE],en\". }\n"
                query+="} ORDER BY ?item "
                print(query)
                print(triplestoreurl)
                try:
                    sparql = SPARQLWrapper(triplestoreurl, agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
                    sparql.setQuery(query)
                    sparql.setMethod(POST)
                    print("now sending query")
                    sparql.setReturnFormat(JSON)
                    results = sparql.query().convert()
                except Exception as e: 
                    try:
                        sparql = SPARQLWrapper(triplestoreurl, agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
                        sparql.setQuery(query)
                        sparql.setMethod(GET)
                        sparql.setReturnFormat(JSON)
                        results = sparql.query().convert()
                    except Exception as e:
                        msgBox=QMessageBox()
                        msgBox.setText("The following exception occurred: "+str(e))
                        msgBox.exec()
                        return    
                print(str(results))
                #resultcounter=0
                for resultcounter in results["results"]["bindings"]:
                    if content=="Enrich Value":
                        resultmap[resultcounter["vals"]["value"]]=resultcounter["valLabel"]["value"]
                    elif content=="Enrich URI":
                        resultmap[resultcounter["vals"]["value"]]=resultcounter["val"]["value"]
                    else:
                        resultmap[resultcounter["vals"]["value"]]=resultcounter["valLabel"]["value"]+";"+resultcounter["val"]["value"]
                print(str(resultmap))
                rowww=0            
                for f in self.enrichLayer.getFeatures():
                    if rowww>=self.dlg.enrichTableResult.rowCount():
                        self.dlg.enrichTableResult.insertRow(rowww)
                    if f[idfield] in resultmap:
                        if strategy=="Merge":
                            newitem=QTableWidgetItem(str(f[item])+str(resultmap[f[idfield]]))
                        elif strategy=="Keep Local":
                            if f[item]==None:
                                newitem=QTableWidgetItem(str(resultmap[f[idfield]]))
                            else:
                                newitem=QTableWidgetItem(str(f[item]))
                        elif strategy=="Ask User":
                            newitem=QTableWidgetItem(str(f[item])+";"+str(resultmap[f[idfield]]))
                        elif strategy=="Keep Remote":
                            if not f[idfield] in resultmap or resultmap[f[idfield]]==None:
                                newitem=QTableWidgetItem(str(f[item]))
                            else:
                                newitem=QTableWidgetItem(str(resultmap[f[idfield]]))
                        else:
                            newitem=QTableWidgetItem(str(resultmap[f[idfield]]))
                        self.dlg.enrichTableResult.setItem(rowww,row,newitem)
                        #if ";" in str(newitem):
                        #    newitem.setBackground(QColor.red)
                        print(str(newitem))
                    rowww+=1  
            else:
                rowww=0            
                for f in self.enrichLayer.getFeatures():
                    if rowww>=self.dlg.enrichTableResult.rowCount():
                        self.dlg.enrichTableResult.insertRow(rowww)
                    #if item in f:
                    newitem=QTableWidgetItem(str(f[item]))
                    self.dlg.enrichTableResult.setItem(rowww,row,newitem)
                    #if ";" in str(newitem):
                    #    newitem.setBackground(QColor.red)
                    print(str(newitem))
                    rowww+=1
            self.enrichLayer.commitChanges()
            row+=1
        iface.vectorLayerTools().stopEditing(self.enrichLayer)
        self.enrichLayer.dataProvider().deleteAttributes(excludelist)
        self.enrichLayer.updateFields()
        self.dlg.enrichTable.hide()
        self.dlg.enrichTableResult.show()
        self.dlg.startEnrichment.setText("Enrichment Configuration")
        self.dlg.startEnrichment.clicked.disconnect()
        self.dlg.startEnrichment.clicked.connect(self.dlg.showConfigTable)
        self.dlg.addEnrichedLayerRowButton.setEnabled(False)
        return self.enrichLayer
        return True

    def finished(self, result):
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
