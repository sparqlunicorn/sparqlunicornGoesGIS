
from qgis.PyQt.QtWidgets import QDialog, QLabel, QLineEdit,QPushButton,QListWidget,QComboBox,QMessageBox,QRadioButton,QListWidgetItem,QTableWidgetItem
from qgis.PyQt.QtCore import QRegExp
from qgis.PyQt.QtGui import QRegExpValidator,QValidator
from SPARQLWrapper import SPARQLWrapper, JSON
import json
import requests

class SearchDialog(QDialog):
	
    currentrow=""
	
    triplestoreconf=""
	
    interlinkOrEnrich=False

    table=False

    def __init__(self,column,row,triplestoreconf,interlinkOrEnrich,table,propOrClass=False,bothOptions=False,currentprefixes=None,addVocab=None):
        super(QDialog, self).__init__()
        self.currentcol=column
        self.currentrow=row
        self.table=table
        self.currentprefixes=currentprefixes
        self.bothOptions=bothOptions
        self.triplestoreconf=triplestoreconf
        self.interlinkOrEnrich=interlinkOrEnrich
        self.conceptSearchEdit = QLineEdit(self)
        self.conceptSearchEdit.move(110,10)
        self.conceptSearchEdit.setMinimumSize(180,25)
        self.addVocab=addVocab
        conceptSearchLabel = QLabel("Search Concept:",self)
        conceptSearchLabel.move(5,10)
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
        #self.tripleStoreEdit.setEnabled(False)
        for triplestore in self.triplestoreconf:
            if not "File"==triplestore["name"]:
                self.tripleStoreEdit.addItem(triplestore["name"])
        if addVocab!=None:
            for cov in addVocab:
                self.tripleStoreEdit.addItem(addVocab[cov]["label"])
        tripleStoreLabel = QLabel("Triple Store:",self)
        tripleStoreLabel.move(5,40)
        searchButton = QPushButton("Search",self)
        searchButton.move(300,10)
        searchButton.clicked.connect(self.getClassesFromLabel)
        costumpropertyLabel = QLabel("Define Own URI:",self)
        costumpropertyLabel.move(10,75)
        urlregex = QRegExp("http[s]?://(?:[a-zA-Z#]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        urlvalidator = QRegExpValidator(urlregex, self)
        self.costumproperty = QLineEdit(self)
        self.costumproperty.move(110,70)
        self.costumproperty.setMinimumSize(200,25)
        self.costumproperty.setValidator(urlvalidator)
        self.costumproperty.textChanged.connect(self.check_state3)
        self.costumproperty.textChanged.emit(self.costumproperty.text())
        costumpropertyButton = QPushButton("Use Own Class/Property",self)
        costumpropertyButton.move(315,70)
        costumpropertyButton.clicked.connect(self.applyConceptToColumn2)
        searchResultLabel = QLabel("Search Results",self)
        searchResultLabel.move(100,100)
        self.searchResult = QListWidget(self)
        self.searchResult.move(30,120)
        self.searchResult.setMinimumSize(600, 300)
        applyButton = QPushButton("Apply",self)
        applyButton.move(150,430)
        applyButton.clicked.connect(self.applyConceptToColumn)

    def check_state3(self):
        self.check_state(self.costumproperty)
		
    def check_state(self,sender):
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QValidator.Acceptable:
            color = '#c4df9b' # green
        elif state == QValidator.Intermediate:
            color = '#fff79a' # yellow
        else:
            color = '#f6989d' # red
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)

    """Returns classes for a given label from a triple store."""
    def getClassesFromLabel(self,comboBox):
        viewlist=[]
        resultlist=[]
        label=self.conceptSearchEdit.text()
        language="en"
        results={}
        self.searchResult.clear()
        query=""
        position=self.tripleStoreEdit.currentIndex()
        if self.tripleStoreEdit.currentIndex()>len(self.triplestoreconf):
            if self.findProperty.isChecked():
                self.addVocab[self.addVocab.keys()[position-len(self.triplestoreconf)]]["source"]["properties"]
                viewlist={k:v for k,v in d.iteritems() if label in k}
            else:
                self.addVocab[self.addVocab.keys()[position-len(self.triplestoreconf)]]["source"]["classes"]
                viewlist={k:v for k,v in d.iteritems() if label in k}
            for res in viewlist:
                item=QListWidgetItem()
                item.setData(1,val)
                item.setText(key)
                self.searchResult.addItem(item)
        else:    
            if self.findProperty.isChecked():
                if "propertyfromlabelquery" in self.triplestoreconf[self.tripleStoreEdit.currentIndex()+1]:
                    query=self.triplestoreconf[self.tripleStoreEdit.currentIndex()+1]["propertyfromlabelquery"].replace("%%label%%",label)
            else:
                if "classfromlabelquery" in self.triplestoreconf[self.tripleStoreEdit.currentIndex()+1]:
                    query=self.triplestoreconf[self.tripleStoreEdit.currentIndex()+1]["classfromlabelquery"].replace("%%label%%",label)
            if query=="":
                msgBox=QMessageBox()
                msgBox.setText("No search query specified for this triplestore")
                msgBox.exec()
                return
            if "SELECT" in query:
                query=query.replace("%%label%%",label).replace("%%language%%",language)
                sparql = SPARQLWrapper(self.triplestoreconf[self.tripleStoreEdit.currentIndex()]["endpoint"], agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
                sparql.setQuery(query)
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                for res in results["results"]["bindings"]:
                    item=QListWidgetItem()
                    item.setData(1,str(res["class"]["value"]))
                    if "label" in res:
                        item.setText(str(res["label"]["value"] +" ("+res["class"]["value"]+")"))
                    else:
                        item.setText(str(res["class"]["value"]))
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

    def applyConceptToColumn2(self):
        self.applyConceptToColumn(True)

    def applyConceptToColumn(self,costumURI=False):
        print("test")
        if costumURI:
            if self.costumproperty.text()=="":
                return   
            toinsert=self.costumproperty.text()
        else:
            if self.searchResult.count()==0:
                return   
            toinsert=str(self.searchResult.currentItem().data(1))
        if self.bothOptions==True:	
            haschanged=False
            for prefix in self.currentprefixes:
                if self.currentprefixes[prefix] in toinsert:
                    toinsert=toinsert.replace(self.currentprefixes[prefix],prefix+":")
                    haschanged=True
            if haschanged:
                self.table.insertPlainText(toinsert)
            else:
                self.table.insertPlainText("<"+toinsert+">")
        elif self.interlinkOrEnrich==-1:
            self.table.setText(str(toinsert))
        else:
            if costumURI:
                item=QTableWidgetItem(toinsert)
                item.setText(toinsert)
            else:
                item=QTableWidgetItem(self.searchResult.currentItem().text())
                item.setText(self.searchResult.currentItem().text())
            item.setData(1,toinsert)
            if self.interlinkOrEnrich:
                self.table.setItem(self.currentrow,self.currentcol,item)
            else:
                item2=QTableWidgetItem()
                item2.setText(self.tripleStoreEdit.currentText())
                item2.setData(0,self.triplestoreconf[self.tripleStoreEdit.currentIndex()+1]["endpoint"])
                self.table.setItem(self.currentrow,self.currentcol,item)
                self.table.setItem(self.currentrow,(self.currentcol+1),item2)
        self.close()
