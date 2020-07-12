
from qgis.PyQt.QtWidgets import QDialog, QLabel, QLineEdit,QPushButton,QListWidget,QComboBox,QMessageBox,QRadioButton,QListWidgetItem,QTableWidgetItem
from qgis.PyQt.QtCore import QRegExp
from qgis.PyQt import uic
from qgis.core import QgsProject
from qgis.PyQt.QtGui import QRegExpValidator,QValidator
from SPARQLWrapper import SPARQLWrapper, JSON
from .searchdialog import SearchDialog
import json
import requests
import os.path

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'whattoenrich.ui'))

class EnrichmentDialog(QDialog, FORM_CLASS):
	
    currentrow=""
	
    triplestoreconf=""
	
    interlinkOrEnrich=False

    table=False

    def __init__(self,triplestoreconf,prefixes,enrichtable,layer,classid="",triplestoreurl=""):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.classid=classid
        self.triplestoreurl=triplestoreurl
        self.triplestoreconf=triplestoreconf
        self.prefixes=prefixes
        self.enrichtable=enrichtable
        self.layer=layer
        for triplestore in self.triplestoreconf:
            if not "File"==triplestore["name"]:
                self.tripleStoreEdit.addItem(triplestore["name"])
        self.searchButton.clicked.connect(self.getAttributeStatistics)
        self.searchConceptButton.clicked.connect(self.createValueMappingSearchDialog)
        self.costumpropertyLabel.hide()
        self.inAreaEditText.hide()
        self.searchButton2.clicked.connect(self.getAttributeStatistics)
        self.searchButton2.hide()
        self.applyButton.clicked.connect(self.applyConceptToColumn)    
        
    def createValueMappingSearchDialog(self, row=-1, column=-1):
        self.buildSearchDialog(row,column,-1,self.conceptSearchEdit)

    ## 
    #  @brief Builds the search dialog for the concept search
    #  
    #  @param [in] self The object pointer
    #  @param [in] row The row for enrichment
    #  @param [in] column The column for enrichment
    #  @param [in] interlinkOrEnrich Indicates if enrichment or interlinking is calling this dialog
    #  @param [in] table The UI element used for displaying results
    def buildSearchDialog(self,row,column,interlinkOrEnrich,table):
       self.currentcol=column
       self.currentrow=row
       self.interlinkdialog = SearchDialog(column,row,self.triplestoreconf,self.prefixes,interlinkOrEnrich,table,True)
       self.interlinkdialog.setMinimumSize(650, 500)
       self.interlinkdialog.setWindowTitle("Search Property or Class")
       self.interlinkdialog.exec_()

    def getAttributeStatistics(self,concept="wd:Q3914",endpoint_url="https://query.wikidata.org/sparql",labellang="en",inarea="wd:Q183"):
        if self.conceptSearchEdit.text()=="":
            return
        concept="<"+self.conceptSearchEdit.text()+">"
        query=self.triplestoreconf[self.tripleStoreEdit.currentIndex()+1]["whattoenrichquery"].replace("%%concept%%",concept).replace("%%area%%",inarea)
		#"select (COUNT(distinct ?con) AS ?countcon) (COUNT(?rel) AS ?countrel) ?rel WHERE { ?con wdt:P31 "+str(concept)+" . ?con wdt:P625 ?coord . ?con wdt:P17  "+str(inarea)+" . ?con ?rel ?val . } GROUP BY ?rel ORDER BY DESC(?countrel)"
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
        if len(results["results"]["bindings"])==0:
            return
        maxcons=int(results["results"]["bindings"][0]["countcon"]["value"])
        attlist={}
        urilist={}
        for result in results["results"]["bindings"]:
            attlist[result["rel"]["value"][result["rel"]["value"].rfind('/')+1:]]=round((int(result["countrel"]["value"])/maxcons)*100,2)
            urilist[result["rel"]["value"][result["rel"]["value"].rfind('/')+1:]]=result["rel"]["value"]
        sortedatt = sorted(attlist.items(),reverse=True, key=lambda kv: kv[1])
        labels={}
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
                    labels[ent]=myResponse["entities"][ent]["labels"]["en"]["value"]               
                i=i+1
        counter=0
        for att in sortedatt:
            if att[1]<1:
                continue
            if att[0] in labels:
                item=QListWidgetItem()
                item.setText(labels[att[0]]+" ("+str(att[1])+"%)")
                item.setData(1,urilist[att[0]])
                self.searchResult.addItem(item)
                counter+=1
            else:
                item=QListWidgetItem()
                item.setText(att[0]+" ("+str(att[1])+"%)")
                item.setData(1,urilist[att[0]])
                self.searchResult.addItem(item)
        #msgBox=QMessageBox()
        #msgBox.setText(str("Finished"))
        #msgBox.exec()

    def applyConceptToColumn(self,costumURI=False):
        fieldnames = [field.name() for field in self.layer.fields()]
        item=QTableWidgetItem(self.searchResult.currentItem().text()[0:self.searchResult.currentItem().text().rfind('(')-1])
        #item.setFlags(QtCore.Qt.ItemIsEnabled)
        row = self.enrichtable.rowCount() 
        self.enrichtable.insertRow(row)
        self.enrichtable.setItem(row,0,item)
        item=QTableWidgetItem()
        item.setData(1,self.searchResult.currentItem().data(1))
        item.setText(self.searchResult.currentItem().text())
        self.enrichtable.setItem(row,1,item)
        item=QTableWidgetItem()
        item.setText(self.triplestoreconf[self.tripleStoreEdit.currentIndex()+1]["endpoint"])
        self.enrichtable.setItem(row,2,item)
        cbox=QComboBox()
        cbox.addItem("Get Remote")
        cbox.addItem("No Enrichment")
        cbox.addItem("Exclude")
        self.enrichtable.setCellWidget(row,3,cbox)
        cbox=QComboBox()	
        cbox.addItem("Enrich Value")	
        cbox.addItem("Enrich URI")	
        cbox.addItem("Enrich Both")	
        self.enrichtable.setCellWidget(row,4,cbox)
        cbox=QComboBox()
        for fieldd in fieldnames:
            cbox.addItem(fieldd)	
        self.enrichtable.setCellWidget(row,5,cbox)
        itemm=QTableWidgetItem("http://www.w3.org/2000/01/rdf-schema#label")
        self.enrichtable.setItem(row,6,itemm) 
        itemm=QTableWidgetItem(self.conceptSearchEdit.text())
        self.enrichtable.setItem(row,7,itemm)
        itemm=QTableWidgetItem("")
        self.enrichtable.setItem(row,8,itemm)
        self.close()
