from qgis.PyQt.QtWidgets import QDialog, QLabel, QLineEdit,QPushButton,QListWidget,QPlainTextEdit,QComboBox,QCheckBox,QMessageBox,QListWidgetItem,QProgressDialog
from qgis.PyQt.QtCore import QRegExp,Qt
from qgis.PyQt import uic
from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtGui import QRegExpValidator,QValidator,QIntValidator
from .sparqlhighlighter import SPARQLHighlighter
from .detecttriplestoretask import DetectTripleStoreTask
from SPARQLWrapper import SPARQLWrapper, JSON
import os.path
import sys

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'triplestoredialog.ui'))

class TripleStoreDialog(QDialog,FORM_CLASS):
	
    triplestoreconf=""
	
    def __init__(self,triplestoreconf,prefixes,prefixstore,comboBox):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.triplestoreconf=triplestoreconf 
        self.prefixstore=prefixstore
        self.comboBox=comboBox
        self.prefixes=prefixes
        for item in triplestoreconf:
            self.tripleStoreChooser.addItem(item["name"])
        self.tripleStoreChooser.currentIndexChanged.connect(self.loadTripleStoreConfig)    
        #self.addTripleStoreButton.clicked.connect(self.addNewSPARQLEndpoint)	
        urlregex = QRegExp("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        urlvalidator = QRegExpValidator(urlregex, self)
        self.tripleStoreEdit.setValidator(urlvalidator)
        self.tripleStoreEdit.textChanged.connect(self.check_state1)
        self.tripleStoreEdit.textChanged.emit(self.tripleStoreEdit.text())
        self.epsgEdit.setValidator(QIntValidator(1, 100000))	
        prefixregex = QRegExp("[a-z]+")
        prefixvalidator = QRegExpValidator(prefixregex, self)
        self.tripleStorePrefixNameEdit.setValidator(prefixvalidator)
        self.addPrefixButton.clicked.connect(self.addPrefixToList)	
        self.removePrefixButton.clicked.connect(self.removePrefixFromList)	
        self.testConnectButton.clicked.connect(self.testTripleStoreConnection)
        self.deleteTripleStore.clicked.connect(self.deleteTripleStoreFunc)
        self.resetConfiguration.clicked.connect(self.restoreFactory)		
        self.newTripleStore.clicked.connect(self.createNewTripleStore)		
        #self.exampleQuery.textChanged.connect(self.validateSPARQL)	
        self.sparqlhighlighter = SPARQLHighlighter(self.exampleQuery)	
        self.tripleStorePrefixEdit.setValidator(urlvalidator)
        self.tripleStorePrefixEdit.textChanged.connect(self.check_state2)
        self.tripleStorePrefixEdit.textChanged.emit(self.tripleStorePrefixEdit.text())
        self.tripleStoreApplyButton.clicked.connect(self.applyCustomSPARQLEndPoint)	
        self.tripleStoreCloseButton.clicked.connect(self.closeTripleStoreDialog)
        self.detectConfiguration.clicked.connect(self.detectTripleStoreConfiguration)		
        s = QSettings() #getting proxy from qgis options settings
        self.proxyEnabled = s.value("proxy/proxyEnabled")
        self.proxyType = s.value("proxy/proxyType")
        self.proxyHost = s.value("proxy/proxyHost")
        self.proxyPort = s.value("proxy/proxyPort")
        self.proxyUser = s.value("proxy/proxyUser")
        self.proxyPassword = s.value("proxy/proxyPassword")
        #tripleStoreApplyButton = QPushButton("Reset Configuration",self)	
        #tripleStoreApplyButton.move(330,560)	
        #tripleStoreApplyButton.clicked.connect(self.resetTripleStoreConfig)	
		
    def loadTripleStoreConfig(self):
        if self.tripleStoreChooser.currentIndex() in self.triplestoreconf:
            self.tripleStoreEdit.setText(self.triplestoreconf[self.tripleStoreChooser.currentIndex()]["endpoint"])
            self.tripleStoreNameEdit.setText(self.triplestoreconf[self.tripleStoreChooser.currentIndex()]["name"])
            self.prefixList.clear()
            for prefix in self.triplestoreconf[self.tripleStoreChooser.currentIndex()]["prefixes"]:
                self.prefixList.addItem(prefix)
            self.prefixList.sortItems()
            if "active" in self.triplestoreconf[self.tripleStoreChooser.currentIndex()]:
                self.activeCheckBox.setChecked(self.triplestoreconf[self.tripleStoreChooser.currentIndex()]["active"])
            if "crs" in self.triplestoreconf[self.tripleStoreChooser.currentIndex()]:
                self.epsgEdit.setText(str(self.triplestoreconf[self.tripleStoreChooser.currentIndex()]["crs"]))
            else:
                self.epsgEdit.setText("4326")
            self.exampleQuery.setPlainText(self.triplestoreconf[self.tripleStoreChooser.currentIndex()]["querytemplate"][0]["query"])
		
		
    def closeTripleStoreDialog(self):
        self.close()

    def testTripleStoreConnection(self,calledfromotherfunction=False,showMessageBox=True,query="SELECT ?a ?b ?c WHERE { ?a ?b ?c .} LIMIT 1"):
        progress = QProgressDialog("Checking connection to triple store "+self.tripleStoreEdit.text()+"...", "Abort", 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)
        progress.show()
        self.qtask=DetectTripleStoreTask("Checking connection to triple store "+self.tripleStoreEdit.text()+"...",self.triplestoreconf,self.tripleStoreEdit.text(),self.tripleStoreNameEdit.text(),True,False,self.prefixes,self.prefixstore,self.tripleStoreChooser,self.comboBox,False,None,progress)
        QgsApplication.taskManager().addTask(self.qtask)

    def detectTripleStoreConfiguration(self):	
        progress = QProgressDialog("Detecting configuration for triple store "+self.tripleStoreEdit.text()+"...", "Abort", 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)
        progress.show()
        self.qtask=DetectTripleStoreTask("Detecting configuration for triple store "+self.tripleStoreEdit.text()+"...",self.triplestoreconf,self.tripleStoreEdit.text(),self.tripleStoreNameEdit.text(),False,True,self.prefixes,self.prefixstore,self.tripleStoreChooser,self.comboBox,False,None,progress)
        QgsApplication.taskManager().addTask(self.qtask)
	
    ## 
    #  @brief Addes a new SPARQL endpoint to the triple store registry
    #  
    #  @param [in] self The object pointer
    def addNewSPARQLEndpoint(self):
        self.addTripleStore=True
        self.applyCustomSPARQLEndPoint()
		
    ## 
    #  @brief Addes a new SPARQL endpoint to the triple store registry
    #  
    #  @param [in] self The object pointer
    def deleteTripleStoreFunc(self):
        if self.tripleStoreChooser.currentIndex()!=0:
            del self.triplestoreconf[self.tripleStoreChooser.currentIndex()]
            self.tripleStoreChooser.clear()
            for item in self.triplestoreconf:
                self.tripleStoreChooser.addItem(item["name"])
				
    def createNewTripleStore(self):
        self.tripleStoreChooser.addItem("New triple store")
        self.tripleStoreChooser.setCurrentIndex(self.tripleStoreChooser.count()-1)
        self.tripleStoreNameEdit.setText("New triple store")
        self.tripleStoreEdit.setText("")
		
				
    def restoreFactory(self):
        with open(os.path.join(__location__, 'triplestoreconf.json'),'r') as myfile:
            data=myfile.read()
        self.triplestoreconf=json.loads(data)
        self.tripleStoreChooser.clear()
        for item in self.triplestoreconf:
            self.tripleStoreChooser.addItem(item["name"])
        self.writeConfiguration()

    ## 
    #  @brief Adds a prefix to the list of prefixes in the search dialog window.
    #  
    #  @param [in] self The object pointer
    def addPrefixToList(self):	
        item=QListWidgetItem()	
        item.setData(0,"PREFIX "+self.tripleStorePrefixNameEdit.text()+":<"+self.tripleStorePrefixEdit.text()+">")	
        item.setText("PREFIX "+self.tripleStorePrefixNameEdit.text()+":<"+self.tripleStorePrefixEdit.text()+">")	
        self.prefixList.addItem(item)	

    ## 
    #  @brief Removes a prefix from the list of prefixes in the search dialog window.
    #  
    #  @param [in] self The object pointer
    def removePrefixFromList(self):	
        item=QListWidgetItem()	
        for item in self.prefixList.selectedItems():
            self.prefixList.removeItemWidget(item)

    def writeConfiguration(self):
        f = open("triplestoreconf_personal.json", "w")
        f.write(json.dumps(self.triplestoreconf,indent=2))
        f.close()

    def applyCustomSPARQLEndPoint(self):	
        if not self.testTripleStoreConnection(True):	
           return	
        if self.tripleStoreNameEdit.text()=="":	
           msgBox=QMessageBox()	
           msgBox.setWindowTitle("Triple Store Name is missing!")
           msgBox.setText("Please enter a triple store name")	
           msgBox.exec()	
           return	
        #self.endpoints.append(self.tripleStoreEdit.text())	
        self.comboBox.addItem(self.tripleStoreNameEdit.text())	
        curprefixes=[]	
        for i in range(self.prefixList.count()):	
            curprefixes.append(self.prefixList.item(i).text()	)
        if self.addTripleStore:
            index=len(self.triplestoreconf)
            self.tripleStoreChooser.addItem(self.tripleStoreNameEdit.text()	)
            self.triplestoreconf.append({})
            self.triplestoreconf[index]["querytemplate"]=[]
            self.triplestoreconf[index]["querytemplate"].append({})
            self.triplestoreconf[index]["querytemplate"][0]["label"]="Example Query"
            self.triplestoreconf[index]["querytemplate"][0]["query"]=self.exampleQuery.toPlainText()
        else:
            index=self.tripleStoreChooser.currentIndex()
        self.triplestoreconf[index]={}
        self.triplestoreconf[index]["endpoint"]=self.tripleStoreEdit.text()
        self.triplestoreconf[index]["name"]=self.tripleStoreNameEdit.text()	
        self.triplestoreconf[index]["mandatoryvariables"]=[]
        self.triplestoreconf[index]["mandatoryvariables"].append(self.queryVarEdit.text())
        self.triplestoreconf[index]["mandatoryvariables"].append(self.queryVarItemEdit.text())        
        self.triplestoreconf[index]["prefixes"]=curprefixes
        self.triplestoreconf[index]["crs"]=self.epsgEdit.text()	
        self.triplestoreconf[index]["active"]=self.activeCheckBox.isChecked()
        self.addTripleStore=False
		
    def check_state1(self):
        self.check_state(self.tripleStoreEdit)

    def check_state2(self):
        self.check_state(self.tripleStorePrefixEdit)

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
		

