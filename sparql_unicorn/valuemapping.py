
from qgis.PyQt.QtWidgets import QDialog, QLabel, QLineEdit,QPushButton,QListWidget,QComboBox,QMessageBox,QRadioButton,QListWidgetItem,QTableWidgetItem,QTableWidget,QPlainTextEdit
from qgis.core import QgsProject
from SPARQLWrapper import SPARQLWrapper, JSON
import json
import requests

class ValueMappingDialog(QDialog):
	
    currentrow=""
	
    triplestoreconf=""
	
    interlinkOrEnrich=False
    
    searchResultMap={}

    table=False
    
    valmaptable=False

    def __init__(self,column,row,triplestoreconf,interlinkOrEnrich,table,fieldname,layer):
        super(QDialog, self).__init__()
        self.currentcol=column
        self.currentrow=row
        self.table=table
        self.triplestoreconf=triplestoreconf
        self.interlinkOrEnrich=interlinkOrEnrich
        self.valmaptable=QTableWidget(self)
        self.valmaptable.move(10,100)
        while self.valmaptable.rowCount() > 0:
            self.valmaptable.removeRow(0);
        row=0
        self.valmaptable.setHorizontalHeaderLabels(["From","To"])
        self.valmaptable.setColumnCount(2)
        cbox=QComboBox(self)
        cbox.move(10,10)
        toaddset={"All"}
        for f in layer.getFeatures():
            toaddset.add(f.attribute(fieldname))
        for item in toaddset:
            cbox.addItem(str(item))
        self.foundClass=QPlainTextEdit()
        self.foundClass.move(80,10)
        findMappingButton=QPushButton("Find Mapping",self)
        findMappingButton.move(10,70)
        addMappingButton=QPushButton("Add Mapping",self)
        addMappingButton.move(40,70)
        applyButton=QPushButton("Apply",self)
        applyButton.move(10,300)        
        
    """Returns classes for a given label from a triple store."""
    def getClassesFromLabel(self,comboBox):
        viewlist=[]
        resultlist=[]
        label=self.conceptSearchEdit.text()
        language="en"
        results={}
        self.searchResult.clear()
        query=""
        if self.currentcol==4:
            if "propertyfromlabelquery" in self.triplestoreconf[self.tripleStoreEdit.currentIndex()+1]:
                query=self.triplestoreconf[self.tripleStoreEdit.currentIndex()+1]["propertyfromlabelquery"].replace("%%label%%",label)
        else:
            if "classfromlabelquery" in self.triplestoreconf[self.tripleStoreEdit.currentIndex()+1]:
                query=self.triplestoreconf[self.tripleStoreEdit.currentIndex()+1]["classfromlabelquery"].replace("%%label%%",label)
        if "SELECT" in query:
            query=query.replace("%%label%%",label).replace("%%language%%",language)
            sparql = SPARQLWrapper(self.triplestoreconf[self.tripleStoreEdit.currentIndex()]["endpoint"], agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            self.searchResultMap={}
            for res in results["results"]["bindings"]:
                item=QListWidgetItem()
                item.setData(0,str(res["class"]["value"]))
                item.setText(str(res["label"]["value"]))
                self.searchResultMap[res["label"]["value"]]=res["class"]["value"]
                self.searchResult.addItem(item)
        else:
            myResponse = json.loads(requests.get(query).text)
            for ent in myResponse["search"]:
                qid=ent["url"]
                label=ent["label"]+" ("+ent["id"]+") "
                if "description" in ent:
                    label+="["+ent["description"]+"]"
                results[qid]=label    
                self.searchResultMap[label]=ent["url"]
            for result in results:
                item=QListWidgetItem()
                item.setData(0,result)
                item.setText(str(results[result]))
                self.searchResult.addItem(item)
        return viewlist
		
    def applyConceptToColumn(self):
        print("test")
        print(str(self.searchResultMap))
        inputstr=self.searchResultMap[self.searchResult.currentItem().text()]
        if inputstr.startswith("//"):
            inputstr="http:"+str(inputstr)
        if self.interlinkOrEnrich==-1:
            self.table.setText(inputstr)
        else:
            item=QTableWidgetItem(self.searchResult.currentItem().text())
            item.setText(self.searchResult.currentItem().text())
            item.setData(1,inputstr)
            if self.interlinkOrEnrich:
                self.table.setItem(self.currentrow,self.currentcol,item)
            else:
                item2=QTableWidgetItem()
                item2.setText(self.tripleStoreEdit.currentText())
                item2.setData(0,self.triplestoreconf[self.tripleStoreEdit.currentIndex()+1]["endpoint"])
                self.table.setItem(self.currentrow,self.currentcol,item)
                self.table.setItem(self.currentrow,(self.currentcol+1),item2)
        self.close()
