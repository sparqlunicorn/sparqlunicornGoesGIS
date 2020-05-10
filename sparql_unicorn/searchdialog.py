
from qgis.PyQt.QtWidgets import QDialog, QLabel, QLineEdit,QPushButton,QListWidget,QComboBox,QMessageBox,QRadioButton,QListWidgetItem,QTableWidgetItem
from SPARQLWrapper import SPARQLWrapper, JSON
import json
import requests

class SearchDialog(QDialog):
	
    currentrow=""
	
    triplestoreconf=""
	
    interlinkOrEnrich=False

    table=False

    def __init__(self,column,row,triplestoreconf,interlinkOrEnrich,table,propOrClass=False,bothOptions=False):
        super(QDialog, self).__init__()
        self.currentcol=column
        self.currentrow=row
        self.table=table
        self.bothOptions=bothOptions
        self.triplestoreconf=triplestoreconf
        self.interlinkOrEnrich=interlinkOrEnrich
        self.conceptSearchEdit = QLineEdit(self)
        self.conceptSearchEdit.move(110,10)
        conceptSearchLabel = QLabel("Search Concept:",self)
        conceptSearchLabel.move(0,10)
        self.findConcept = QRadioButton("Class",self)
        self.findConcept.move(400,15)
        if column!=4:
            self.findConcept.setChecked(True)
        self.findProperty = QRadioButton("Property",self)
        self.findProperty.move(400,40)
        if column==4 or (not interlinkOrEnrich and column!=4) or (not interlinkOrEnrich and propOrClass):
            self.findProperty.setChecked(True)
        if not bothOptions:	        
            self.findProperty.setEnabled(False)
            self.findConcept.setEnabled(False)
        self.tripleStoreEdit = QComboBox(self)
        self.tripleStoreEdit.move(100,40)
        self.tripleStoreEdit.setEnabled(False)
        for triplestore in self.triplestoreconf:
            if not "File"==triplestore["name"]:
                self.tripleStoreEdit.addItem(triplestore["name"])
        tripleStoreLabel = QLabel("Triple Store:",self)
        tripleStoreLabel.move(0,40)
        searchButton = QPushButton("Search",self)
        searchButton.move(10,70)
        searchButton.clicked.connect(self.getClassesFromLabel)
        searchResultLabel = QLabel("Search Results",self)
        searchResultLabel.move(100,100)
        self.searchResult = QListWidget(self)
        self.searchResult.move(30,120)
        self.searchResult.setMinimumSize(600, 300)
        applyButton = QPushButton("Apply",self)
        applyButton.move(150,430)
        applyButton.clicked.connect(self.applyConceptToColumn)
		
    """Returns classes for a given label from a triple store."""
    def getClassesFromLabel(self,comboBox):
        viewlist=[]
        resultlist=[]
        label=self.conceptSearchEdit.text()
        language="en"
        results={}
        self.searchResult.clear()
        query=""
        if self.findProperty.isChecked():
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
            for res in results["results"]["bindings"]:
                item=QListWidgetItem()
                item.setData(1,str(res["class"]["value"]))
                item.setText(str(res["label"]["value"]))
                self.searchResult.addItem(item)
        else:
            myResponse = json.loads(requests.get(query).text)
            qids=[]
            for ent in myResponse["search"]:
                qid=ent["concepturi"]
                if "http://www.wikidata.org/entity/" in qid and self.findProperty.isChecked():
                    qid="http://www.wikidata.org/prop/direct/"+ent["id"]
                elif "http://www.wikidata.org/wiki/" in qid and self.findConcept.isChecked():
                    qid="http://www.wikidata.org/entity/"+ent["id"]
                qids.append(qid)
                label=ent["label"]+" ("+ent["id"]+") "
                if "description" in ent:
                    label+="["+ent["description"]+"]"
                results[qid]=label    
            i=0
            for result in results:
                item=QListWidgetItem()
                item.setData(1,qids[i])
                item.setText(str(results[result]))
                self.searchResult.addItem(item)
                i+=1
        return viewlist
		
    def applyConceptToColumn(self):
        print("test")
        if self.searchResult.count()==0:
            return
        if self.bothOptions==True:	       
            self.table.insertPlainText("<"+str(self.searchResult.currentItem().data(1))+">")
        elif self.interlinkOrEnrich==-1:
            self.table.setText(str(self.searchResult.currentItem().data(1)))
        else:
            item=QTableWidgetItem(self.searchResult.currentItem().text())
            item.setText(self.searchResult.currentItem().text())
            item.setData(1,self.searchResult.currentItem().data(1))
            if self.interlinkOrEnrich:
                self.table.setItem(self.currentrow,self.currentcol,item)
            else:
                item2=QTableWidgetItem()
                item2.setText(self.tripleStoreEdit.currentText())
                item2.setData(0,self.triplestoreconf[self.tripleStoreEdit.currentIndex()+1]["endpoint"])
                self.table.setItem(self.currentrow,self.currentcol,item)
                self.table.setItem(self.currentrow,(self.currentcol+1),item2)
        self.close()
