
from qgis.PyQt.QtWidgets import QDialog, QLabel, QLineEdit,QPushButton,QTableWidget,QComboBox,QMessageBox,QRadioButton,QListWidgetItem,QTableWidgetItem
from qgis.PyQt.QtCore import QRegExp
from qgis.PyQt.QtGui import QRegExpValidator,QValidator
from SPARQLWrapper import SPARQLWrapper, JSON
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
        self.conceptSearchEdit.move(110,10)
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
        searchButton = QPushButton("Search",self)
        searchButton.move(300,10)
        searchButton.clicked.connect(self.getAttributeStatistics)
        costumpropertyLabel = QLabel("Label Language:",self)
        costumpropertyLabel.move(10,75)
        self.costumproperty = QLineEdit(self)
        self.costumproperty.move(110,70)
        self.costumproperty.setText("en")
        self.costumproperty.setMinimumSize(200,25)
        costumpropertyButton = QLabel("In Area:",self)
        costumpropertyButton.move(5,95)
        inAreaEdit = QLabel("In Area:",self)
        inAreaEdit.move(55,95)
        inAreaEdit.setText("Germany")
        searchResultLabel = QLabel("Search Results",self)
        searchResultLabel.move(100,100)
        self.searchResult = QTableWidget(self)
        self.searchResult.move(30,120)
        self.searchResult.setMinimumSize(800, 300)
        self.searchResult.setColumnCount(5)
        self.searchResult.setHorizontalHeaderLabels(["Concept Count","Relation Count","Value Count","Occurance Percentage","Relation","Relation Label"])
        applyButton = QPushButton("Apply",self)
        applyButton.move(150,430)
        applyButton.clicked.connect(self.applyConceptToColumn)

    def getAttributeStatistics(self,concept="wd:Q3914",endpoint_url="https://query.wikidata.org/sparql",labellang="en",inarea="wd:Q183"):
        concept="wd:Q3914"
        query="select (COUNT(distinct ?con) AS ?countcon) (COUNT(?rel) AS ?countrel) (COUNT(distinct ?val) AS ?countval) ?rel ?relLabel WHERE { ?con wdt:P31 "+str(concept)+" . ?con wdt:P625 ?coord . ?con wdt:P17  "+str(inarea)+" . ?con ?rel ?val . SERVICE wikibase:label { bd:serviceParam wikibase:language \""+str(labellang)+"\" . }  } GROUP BY ?rel ?relLabel ORDER BY DESC(?countrel)"
        msgBox=QMessageBox()
        msgBox.setText(str("".join(self.prefixes[self.tripleStoreEdit.currentIndex()+1]) + query))
        msgBox.exec()
        sparql = SPARQLWrapper(endpoint_url, agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
        sparql.setQuery("".join(self.prefixes[self.tripleStoreEdit.currentIndex()]) + query)
        sparql.setReturnFormat(JSON)
        try:
            results = sparql.query().convert()
            msgBox=QMessageBox()
            msgBox.setText(str(results["results"]["bindings"]))
            msgBox.exec()
        except Exception as e:
            msgBox=QMessageBox()
            msgBox.setText("The following exception occurred: "+str(e))
            msgBox.exec()
            return  
        self.searchResult.clear()
        self.searchResult.setColumnCount(6)
        self.searchResult.setHorizontalHeaderLabels(["Concept Count","Relation Count","Value Count","Occurance Percentage","Relation","Relation Label"])
        maxcons=int(results["results"]["bindings"][0]["countcon"]["value"])
        for result in results["results"]["bindings"]:
            row = self.searchResult.rowCount() 
            self.searchResult.insertRow(row)
            item=QTableWidgetItem(result["countcon"]["value"])
            self.searchResult.setItem(row,0,item)
            item=QTableWidgetItem(result["countrel"]["value"])
            self.searchResult.setItem(row,1,item)
            item=QTableWidgetItem(result["countval"]["value"])
            self.searchResult.setItem(row,2,item)
            item=QTableWidgetItem(str(round((int(result["countrel"]["value"])/maxcons)*100,2))+"%")
            self.searchResult.setItem(row,3,item)
            item=QTableWidgetItem(result["rel"]["value"])
            self.searchResult.setItem(row,4,item)
            item=QTableWidgetItem(result["relLabel"]["value"][result["relLabel"]["value"].rfind('/')+1:])
            self.searchResult.setItem(row,5,item)

    def applyConceptToColumn(self,costumURI=False):
        self.close()
