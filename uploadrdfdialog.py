
from qgis.PyQt.QtWidgets import QDialog, QLabel, QLineEdit,QPushButton,QCheckBox,QListWidget,QComboBox,QMessageBox,QRadioButton,QListWidgetItem,QTableWidgetItem,QTableWidget,QPlainTextEdit
from qgis.core import QgsProject
from rdflib import Graph, Literal, URIRef
from rdflib.plugins.stores import sparqlstore
from .searchdialog import SearchDialog
from .sparqlhighlighter import SPARQLHighlighter
from SPARQLWrapper import SPARQLWrapper, JSON
import json
import requests

class UploadRDFDialog(QDialog):
	
    currentrow=""
	
    triplestoreconf=""
	
    interlinkOrEnrich=False
    
    searchResultMap={}

    table=False
    
    valmaptable=False
	
    fieldname=""

    def __init__(self,ttlstring):
        super(QDialog, self).__init__()
        #self.layerBoxLabel=QLabel("Choose Layer For Export: ",self)
        #self.layerBoxLabel.move(10,10)
        self.ttlstring=ttlstring
        #self.layerBox=QComboBox(self)
        #self.layerBox.move(170,10)
        #layers = QgsProject.instance().layerTreeRoot().children()
        #for layer in layers:
        #    ucl = layer.name()
        #    self.layerBox.addItem(ucl)  
        self.tripleStoreURL=QLabel("Triple Store URL: ",self)
        self.tripleStoreURL.move(10,40)
        self.tripleStoreURLEdit=QLineEdit(self)
        self.tripleStoreURLEdit.move(130,40)
        self.tripleStoreGraph=QLabel("Triple Store Graph: ",self)
        self.tripleStoreGraph.move(10,75)
        self.tripleStoreGraphEdit=QLineEdit(self)
        self.tripleStoreGraphEdit.move(130,75)
        self.username=QLabel("Username: ",self)
        self.username.move(10,110)
        self.usernameEdit=QLineEdit(self)
        self.usernameEdit.move(130,110)
        self.password=QLabel("Password: ",self)
        self.password.move(10,140)
        self.passwordEdit=QLineEdit(self)
        self.passwordEdit.move(130,140)
        checkConnectionButton=QPushButton("Check connection",self)
        checkConnectionButton.move(10,200)    
        checkConnectionButton.clicked.connect(self.checkConnection)
        applyButton=QPushButton("Apply",self)
        applyButton.move(150,200)    
        applyButton.clicked.connect(self.uploadResult)
	
    def checkConnection(self):
        print("")

    def uploadResult(self):
        query_endpoint = 'http://localhost:3030/ds/query'
        update_endpoint = self.tripleStoreURL
        g=Graph()
        g.parse(data=self.ttlstring, format="ttl")
        store = sparqlstore.SPARQLUpdateStore()
        store.open((query_endpoint, update_endpoint))
        store.add_graph(g)
        self.close()
