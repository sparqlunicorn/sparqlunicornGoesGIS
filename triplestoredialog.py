from qgis.PyQt.QtWidgets import QDialog, QLabel, QLineEdit,QPushButton,QListWidget,QPlainTextEdit,QComboBox,QCheckBox,QMessageBox
from qgis.PyQt.QtCore import QRegExp
from qgis.PyQt.QtGui import QRegExpValidator,QValidator,QIntValidator
from .sparqlhighlighter import SPARQLHighlighter
from SPARQLWrapper import SPARQLWrapper, JSON

class TripleStoreDialog(QDialog):
	
    triplestoreconf=""
	
    def __init__(self,triplestoreconf,comboBox):
        super(QDialog, self).__init__()
        self.triplestoreconf=triplestoreconf
        self.comboBox=comboBox
        self.tripleStoreChooserLabel = QLabel("Choose Triple Store:",self)	
        self.tripleStoreChooserLabel.move(0,10)
        self.tripleStoreChooser=QComboBox(self)
        for item in triplestoreconf:
            self.tripleStoreChooser.addItem(item["name"])
        self.tripleStoreChooser.move(150,10)
        self.tripleStoreChooser.currentIndexChanged.connect(self.loadTripleStoreConfig)    
        self.addTripleStoreButton = QPushButton("Add new Triple Store",self)	
        self.addTripleStoreButton.move(350,10)	
        self.addTripleStoreButton.clicked.connect(self.addNewSPARQLEndpoint)	
        self.tripleStoreLabel = QLabel("Triple Store URL:",self)	
        self.tripleStoreLabel.move(0,40)	
        urlregex = QRegExp("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
        urlvalidator = QRegExpValidator(urlregex, self)
        self.tripleStoreEdit = QLineEdit(self)	
        self.tripleStoreEdit.move(150,40)	
        self.tripleStoreEdit.setMinimumSize(350, 20)	
        self.tripleStoreEdit.setText("https://query.wikidata.org/sparql")
        self.tripleStoreEdit.setValidator(urlvalidator)
        self.tripleStoreEdit.textChanged.connect(self.check_state1)
        self.tripleStoreEdit.textChanged.emit(self.tripleStoreEdit.text())
        self.testConnectButton = QPushButton("Test Connection",self)	
        self.testConnectButton.move(510,40)	
        self.testConnectButton.clicked.connect(self.testTripleStoreConnection)	
        self.tripleStoreNameLabel = QLabel("Triple Store Name:",self)	
        self.tripleStoreNameLabel.move(0,70)	
        self.tripleStoreNameEdit = QLineEdit(self)	
        self.tripleStoreNameEdit.move(150,70)	
        self.tripleStoreNameEdit.setMinimumSize(350, 20)	
        self.tripleStoreNameEdit.setText("My cool triplestore!")	
        self.queryVarLabel = QLabel("Geometry Variable:",self)	
        self.queryVarLabel.move(10,105)	
        self.queryVarEdit = QLineEdit(self)	
        self.queryVarEdit.move(150,100)	
        self.queryVarEdit.setText("geo")	
        self.queryVarEdit.setMinimumSize(100, 20)	
        self.queryVarItemLabel = QLabel("Item Variable:",self)	
        self.queryVarItemLabel.move(305,105)	
        self.queryVarItemEdit = QLineEdit(self)	
        self.queryVarItemEdit.move(400,100)	
        self.queryVarItemEdit.setText("item")	
        self.queryVarItemEdit.setMinimumSize(100, 20)	
        self.epsgLabel = QLabel("EPSG Code:",self)	
        self.epsgLabel.move(10,125)	
        self.epsgEdit = QLineEdit(self)	
        self.epsgEdit.move(150,125)	
        self.epsgEdit.setText("4326")
        self.epsgEdit.setValidator(QIntValidator(1, 100000))
        self.epsgEdit.setMinimumSize(100, 20)
        self.activeTripleStore = QLabel("Active:",self)	
        self.activeTripleStore.move(310,125)	
        self.activeCheckBox = QCheckBox(self)	
        self.activeCheckBox.move(360,125)	
        prefixregex = QRegExp("[a-z]+")
        prefixvalidator = QRegExpValidator(prefixregex, self)
        self.tripleStorePrefixNameEdit = QLineEdit(self)	
        self.tripleStorePrefixNameEdit.move(150,150)	
        self.tripleStorePrefixNameEdit.setText("wd")	
        self.tripleStorePrefixNameEdit.setMinimumSize(100, 20)	
        self.tripleStorePrefixNameEdit.setValidator(prefixvalidator)
        self.tripleStorePrefixName = QLabel("Prefix:",self)	
        self.tripleStorePrefixName.move(10,150)	
        self.addPrefixButton = QPushButton("Add Prefix",self)	
        self.addPrefixButton.move(560,150)	
        self.addPrefixButton.clicked.connect(self.addPrefixToList)	
        self.removePrefixButton = QPushButton("Remove Selected Prefix",self)	
        self.removePrefixButton.move(100,180)
        self.removePrefixButton.clicked.connect(self.removePrefixFromList)	
        prefixListLabel = QLabel("Prefixes:",self)	
        prefixListLabel.move(20,185)	
        self.prefixList=QListWidget(self)	
        self.prefixList.move(20,210)	
        self.prefixList.setMinimumSize(300,200)	
        self.exampleQueryLabel = QLabel("Example Query (optional): ",self)	
        self.exampleQueryLabel.move(330,185)	
        self.exampleQuery=QPlainTextEdit(self)	
        self.exampleQuery.move(330,210)	
        self.exampleQuery.setMinimumSize(300,200)	
        #self.exampleQuery.textChanged.connect(self.validateSPARQL)	
        self.sparqlhighlighter = SPARQLHighlighter(self.exampleQuery)	
        #self.queryChooser=QComboBox(self)
        self.tripleStorePrefixEdit = QLineEdit(self)	
        self.tripleStorePrefixEdit.move(310,150)	
        self.tripleStorePrefixEdit.setText("http://www.wikidata.org/entity/")	
        self.tripleStorePrefixEdit.setValidator(urlvalidator)
        self.tripleStorePrefixEdit.textChanged.connect(self.check_state2)
        self.tripleStorePrefixEdit.textChanged.emit(self.tripleStorePrefixEdit.text())
        self.tripleStorePrefixEdit.setMinimumSize(250, 20)
        self.tripleStoreApplyButton = QPushButton("Apply",self)	
        self.tripleStoreApplyButton.move(10,460)	
        self.tripleStoreApplyButton.clicked.connect(self.applyCustomSPARQLEndPoint)	
        self.tripleStoreCloseButton = QPushButton("Close",self)	
        self.tripleStoreCloseButton.move(100,460)	
        self.tripleStoreCloseButton.clicked.connect(self.closeTripleStoreDialog)	
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

    def testTripleStoreConnection(self,calledfromotherfunction=False):	
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

    def addNewSPARQLEndpoint(self):
        self.addTripleStore=True
        self.applyCustomSPARQLEndPoint()


    def addPrefixToList(self):	
        item=QListWidgetItem()	
        item.setData(0,"PREFIX "+self.tripleStorePrefixNameEdit.text()+":<"+self.tripleStorePrefixEdit.text()+">")	
        item.setText("PREFIX "+self.tripleStorePrefixNameEdit.text()+":<"+self.tripleStorePrefixEdit.text()+">")	
        self.prefixList.addItem(item)	

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
		

