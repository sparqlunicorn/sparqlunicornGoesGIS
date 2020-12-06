from qgis.PyQt.QtWidgets import QDialog, QLabel, QLineEdit,QPushButton,QListWidget,QPlainTextEdit,QComboBox,QCheckBox,QMessageBox,QListWidgetItem
from qgis.PyQt.QtCore import QRegExp
from qgis.PyQt import uic
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtGui import QRegExpValidator,QValidator,QIntValidator
from .sparqlhighlighter import SPARQLHighlighter
from SPARQLWrapper import SPARQLWrapper, JSON
import os.path

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'triplestoredialog.ui'))

class TripleStoreDialog(QDialog,FORM_CLASS):
	
    triplestoreconf=""
	
    def __init__(self,triplestoreconf,comboBox):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.triplestoreconf=triplestoreconf
        self.comboBox=comboBox
        for item in triplestoreconf:
            self.tripleStoreChooser.addItem(item["name"])
        self.tripleStoreChooser.currentIndexChanged.connect(self.loadTripleStoreConfig)    
        self.addTripleStoreButton.clicked.connect(self.addNewSPARQLEndpoint)	
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
        #self.exampleQuery.textChanged.connect(self.validateSPARQL)	
        self.sparqlhighlighter = SPARQLHighlighter(self.exampleQuery)	
        self.tripleStorePrefixEdit.setValidator(urlvalidator)
        self.tripleStorePrefixEdit.textChanged.connect(self.check_state2)
        self.tripleStorePrefixEdit.textChanged.emit(self.tripleStorePrefixEdit.text())
        self.tripleStoreApplyButton.clicked.connect(self.applyCustomSPARQLEndPoint)	
        self.tripleStoreCloseButton.clicked.connect(self.closeTripleStoreDialog)	
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

    ## 
    #  @brief Tests the connection for a given triple store.
    #  
    #  @param [in] self The object pointer
    #  @param [in] calledfromotherfunction Indicates if the method is called from a super fu
    #  @return Return true if the connection was successful, false otherwise
    #  
    def testTripleStoreConnection(self,calledfromotherfunction=False):	
        if self.proxyHost!=None and self.ProxyPort!=None:
            proxy = urllib.ProxyHandler({'http': proxyHost})
            opener = urllib.build_opener(proxy)
            urllib.install_opener(opener)
        sparql = SPARQLWrapper(self.tripleStoreEdit.text(), agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")	
        sparql.setQuery("SELECT ?a ?b ?c WHERE { ?a ?b ?c .} LIMIT 1")	
        sparql.setReturnFormat(JSON)	
        print("now sending query")	
        try:	
            results = sparql.query()	
            if not calledfromotherfunction:	
                msgBox=QMessageBox()	
                msgBox.setText("URL depicts a valid SPARQL Endpoint!")	
                msgBox.exec()	
            return True	
        except:	
            msgBox=QMessageBox()	
            msgBox.setText("URL does not depict a valid SPARQL Endpoint!")	
            msgBox.exec()	
            return False	
        
    ## 
    #  @brief Addes a new SPARQL endpoint to the triple store registry
    #  
    #  @param [in] self The object pointer
    def addNewSPARQLEndpoint(self):
        self.addTripleStore=True
        self.applyCustomSPARQLEndPoint()

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


    def applyCustomSPARQLEndPoint(self):	
        if not self.testTripleStoreConnection(True):	
           return	
        if self.tripleStoreNameEdit.text()=="":	
           msgBox=QMessageBox()	
           msgBox.setText("Triple Store Name is missing!")	
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
		

