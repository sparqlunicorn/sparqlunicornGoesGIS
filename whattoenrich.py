
from qgis.PyQt.QtWidgets import QDialog, QLabel, QLineEdit,QPushButton,QTableWidget,QComboBox,QMessageBox,QRadioButton,QListWidgetItem,QTableWidgetItem
from qgis.PyQt.QtCore import QRegExp
from qgis.PyQt.QtGui import QRegExpValidator,QValidator
from SPARQLWrapper import SPARQLWrapper, JSON
from .searchdialog import SearchDialog
import json
import requests

class EnrichmentDialog(QDialog):
	
    currentrow=""
	
    triplestoreconf=""
	
    interlinkOrEnrich=False

    table=False

    def __init__(self,triplestoreconf,prefixes,classid="",triplestoreurl=""):
        super(QDialog, self).__init__()
        self.classid=classid
        self.triplestoreurl=triplestoreurl
        self.triplestoreconf=triplestoreconf
        self.prefixes=prefixes
        self.conceptSearchEdit = QLineEdit(self)
        self.conceptSearchEdit.move(130,10)
        self.conceptSearchEdit.setMinimumSize(180,25)
        conceptSearchLabel = QLabel("Search ID Concept:",self)
        conceptSearchLabel.move(5,10)
        self.findConcept = QRadioButton("Class",self)
        self.findConcept.move(400,15)
        self.tripleStoreEdit = QComboBox(self)
        self.tripleStoreEdit.move(100,40)
        self.tripleStoreEdit.setEnabled(False)
        for triplestore in self.triplestoreconf:
            if not "File"==triplestore["name"]:
                self.tripleStoreEdit.addItem(triplestore["name"])
        tripleStoreLabel = QLabel("Triple Store:",self)
        tripleStoreLabel.move(5,40)
        searchButton = QPushButton("Search Properties",self)
        searchButton.move(300,90)
        searchButton.clicked.connect(self.getAttributeStatistics)
        searchConceptButton = QPushButton("Search Concept",self)
        searchConceptButton.move(350,10)
        searchConceptButton.clicked.connect(self.createValueMappingSearchDialog)
        costumpropertyLabel = QLabel("Label Language:",self)
        costumpropertyLabel.move(10,75)
        self.costumproperty = QLineEdit(self)
        self.costumproperty.move(110,70)
        self.costumproperty.setText("en")
        self.costumproperty.setMinimumSize(200,25)
        costumpropertyButton = QLabel("In Area:",self)
        costumpropertyButton.move(400,75)
        inAreaEditText = QLineEdit(self)
        inAreaEditText.move(450,75)
        searchButton2 = QPushButton("Search Area Concept",self)
        searchButton2.move(550,75)
        searchButton2.clicked.connect(self.getAttributeStatistics)
        searchResultLabel = QLabel("Search Results",self)
        searchResultLabel.move(100,100)
        self.searchResult = QTableWidget(self)
        self.searchResult.move(30,120)
        self.searchResult.setMinimumSize(800, 300)
        self.searchResult.setColumnCount(3)
        self.searchResult.setHorizontalHeaderLabels(["Occurance Percentage","Relation","Relation Label"])
        applyButton = QPushButton("Apply",self)
        applyButton.move(150,430)
        applyButton.clicked.connect(self.applyConceptToColumn)
        
        
    def createValueMappingSearchDialog(self, row=-1, column=-1):
        self.buildSearchDialog(row,column,-1,self.conceptSearchEdit)

    def buildSearchDialog(self,row,column,interlinkOrEnrich,table):
       self.currentcol=column
       self.currentrow=row
       self.interlinkdialog = SearchDialog(column,row,self.triplestoreconf,interlinkOrEnrich,table,True)
       self.interlinkdialog.setMinimumSize(650, 500)
       self.interlinkdialog.setWindowTitle("Search Property or Class")
       self.interlinkdialog.exec_()

    def getAttributeStatistics(self,concept="wd:Q3914",endpoint_url="https://query.wikidata.org/sparql",labellang="en",inarea="wd:Q183"):
        if self.conceptSearchEdit.text()=="":
            return
        concept="<"+self.conceptSearchEdit.text()+">"
        query="select (COUNT(distinct ?con) AS ?countcon) (COUNT(?rel) AS ?countrel) (COUNT(distinct ?val) AS ?countval) ?rel ?relLabel WHERE { ?con wdt:P31 "+str(concept)+" . ?con wdt:P625 ?coord . ?con wdt:P17  "+str(inarea)+" . ?con ?rel ?val . SERVICE wikibase:label { bd:serviceParam wikibase:language \""+str(labellang)+"\" . }  } GROUP BY ?rel ?relLabel ORDER BY DESC(?countrel)"
        sparql = SPARQLWrapper(endpoint_url, agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
        sparql.setQuery("".join(self.prefixes[self.tripleStoreEdit.currentIndex()]) + query)
        sparql.setReturnFormat(JSON)
        try:
            results = sparql.query().convert()
        except Exception as e:
            msgBox=QMessageBox()
            msgBox.setText("The following exception occurred: "+str(e))
            msgBox.exec()
            return  
        self.searchResult.clear()
        self.searchResult.setColumnCount(3)
        self.searchResult.setHorizontalHeaderLabels(["Occurance Percentage","Relation","Relation Label"])
        maxcons=int(results["results"]["bindings"][0]["countcon"]["value"])
        attlist={}
        for result in results["results"]["bindings"]:
            attlist[result["relLabel"]["value"][result["relLabel"]["value"].rfind('/')+1:]]=round((int(result["countrel"]["value"])/maxcons)*100,2)
        sortedatt = sorted(attlist.items(),reverse=True, key=lambda kv: kv[1])
        labels={}
        atts=""
        count=0
        for att in attlist.keys():
            if att.startswith("P") and count<50:
                atts+=att+"|"
                count+=1
        atts=atts[:-1]
        url="https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&language=en&ids="+atts
        i=0
        myResponse = json.loads(requests.get(url).text)
        #msgBox=QMessageBox()
        #msgBox.setText(str(myResponse))
        #msgBox.exec()
        for ent in myResponse["entities"]:
            print(ent)
            if "en" in myResponse["entities"][ent]["labels"]:
                labels[ent]=myResponse["entities"][ent]["labels"]["en"]["value"]               
            i=i+1
        counter=0
        for att in sortedatt:
            if att[1]<1:
                continue
            row = self.searchResult.rowCount() 
            self.searchResult.insertRow(row)
            item=QTableWidgetItem(str(att[1])+"%")
            self.searchResult.setItem(row,0,item)
            item=QTableWidgetItem(att[0])#result["relLabel"]["value"][result["relLabel"]["value"].rfind('/')+1:])
            self.searchResult.setItem(row,1,item)
            if att[0] in labels:
                item=QTableWidgetItem(labels[att[0]])#result["relLabel"]["value"][result["relLabel"]["value"].rfind('/')+1:])
                self.searchResult.setItem(row,2,item)
                counter+=1
            else:
                item=QTableWidgetItem(att[0])#result["relLabel"]["value"][result["relLabel"]["value"].rfind('/')+1:])
                self.searchResult.setItem(row,2,item)

    def applyConceptToColumn(self,costumURI=False):
        self.close()
