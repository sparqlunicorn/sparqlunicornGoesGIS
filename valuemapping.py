
from qgis.PyQt.QtWidgets import QDialog, QLabel, QLineEdit,QPushButton,QListWidget,QComboBox,QMessageBox,QRadioButton,QListWidgetItem,QTableWidgetItem,QTableWidget,QPlainTextEdit
from qgis.core import QgsProject
from .searchdialog import SearchDialog
from .sparqlhighlighter import SPARQLHighlighter
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
	
    fieldname=""

    def __init__(self,column,row,triplestoreconf,interlinkOrEnrich,table,fieldname,layer,valuemap):
        super(QDialog, self).__init__()
        self.currentcol=column
        self.currentrow=row
        self.table=table
        self.fieldname=fieldname
        self.triplestoreconf=triplestoreconf
        self.interlinkOrEnrich=interlinkOrEnrich
        self.valuemap=valuemap
        self.queryedit=QPlainTextEdit(self)
        self.queryedit.zoomIn(4)
        self.queryhighlight=SPARQLHighlighter(self.queryedit)
        self.queryedit.move(320,100)
        self.queryedit.setMinimumSize(310,300)
        self.queryedit.setPlainText("SELECT ?item\n WHERE {\n ?item ?rel %%"+fieldname+"%% . \n}")
        self.tripleStoreEdit = QComboBox(self)
        self.tripleStoreEdit.move(320,400)
        self.tripleStoreEdit.setEnabled(False)
        for triplestore in self.triplestoreconf:
            if not "File"==triplestore["name"]:
                self.tripleStoreEdit.addItem(triplestore["name"])
        self.valmaptable=QTableWidget(self)
        self.valmaptable.move(10,100)
        self.valmaptable.setMinimumSize(300, 300)
        while self.valmaptable.rowCount() > 0:
            self.valmaptable.removeRow(0);
        row=0
        self.valmaptable.setColumnCount(2)
        self.valmaptable.setHorizontalHeaderLabels(["From","To"])		
        if valuemap!=None:
            for key in valuemap:
                row = self.valmaptable.rowCount() 
                self.valmaptable.insertRow(row)
                item=QTableWidgetItem(key)
                item2=QTableWidgetItem(valuemap[key])
                self.valmaptable.setItem(row,0,item)
                self.valmaptable.setItem(row,1,item2)
        cboxlabel=QLabel("Select Value To Map",self)
        cboxlabel.move(10,10)
        self.cbox=QComboBox(self)
        self.cbox.move(140,10)
        toaddset={"All"}
        for f in layer.getFeatures():
            toaddset.add(f.attribute(fieldname))
        for item in toaddset:
            self.cbox.addItem(str(item))
        cboxlabel=QLabel("Map To:",self)
        cboxlabel.move(10,40)
        self.foundClass=QLineEdit(self)
        self.foundClass.move(140,40)
        self.foundClass.resize(400, self.foundClass.height())
        findMappingButton=QPushButton("Find Mapping",self)
        findMappingButton.move(10,70)
        findMappingButton.clicked.connect(self.createValueMappingSearchDialog)
        addMappingButton=QPushButton("Add Mapping",self)
        addMappingButton.move(110,70)
        addMappingButton.clicked.connect(self.addMappingToTable)
        deleteRowButton=QPushButton("Delete Selected Table Row",self)
        deleteRowButton.move(100,400)
        deleteRowButton.clicked.connect(self.deleteSelectedRow)
        sparqlLabel=QLabel("Mapping by SPARQL Query:\nColumn names may be used as variables in %%",self)
        sparqlLabel.move(320,70)
        applyButton=QPushButton("Apply",self)
        applyButton.move(10,400)    
        applyButton.clicked.connect(self.applyMapping)
      
    def addMappingToTable(self):
        if self.foundClass.text()!="":
            row = self.valmaptable.rowCount() 
            self.valmaptable.insertRow(row)
            item=QTableWidgetItem(self.cbox.currentText())
            item2=QTableWidgetItem(self.foundClass.text())
            self.valmaptable.setItem(row,0,item)
            self.valmaptable.setItem(row,1,item2)
            self.foundClass.setText("")
			
    def deleteSelectedRow(self):
        for index in self.valmaptable.selectedIndexes():
            self.valmaptable.removeRow(index.row())
	  
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

    def createValueMappingSearchDialog(self, row=-1, column=-1):
        self.buildSearchDialog(row,column,-1,self.foundClass)

    def buildSearchDialog(self,row,column,interlinkOrEnrich,table):
       self.currentcol=column
       self.currentrow=row
       self.interlinkdialog = SearchDialog(column,row,self.triplestoreconf,interlinkOrEnrich,table,True)
       self.interlinkdialog.setMinimumSize(650, 500)
       self.interlinkdialog.setWindowTitle("Search Property or Class")
       self.interlinkdialog.exec_()
	
    def applyMapping(self):
        resmap={}
        for row in range(self.valmaptable.rowCount()):
            fromm = self.valmaptable.item(row, 0).text()
            to = self.valmaptable.item(row, 1).text()
            resmap[fromm]=to
        item=QTableWidgetItem("ValueMap{}")
        item.setText("ValueMap{}")
        item.setData(1,resmap)
        if "SELECT ?item\n WHERE {\n ?item ?rel %%"+self.fieldname+"%% . \n}"!=self.queryedit.toPlainText():
            item.setData(2,self.queryedit.toPlainText())
            item.setData(3,self.tripleStoreEdit.currentText())
        self.table.setItem(self.currentrow,self.currentcol,item)
        self.close()
        return resmap
