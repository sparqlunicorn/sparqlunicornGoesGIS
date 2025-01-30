from qgis.PyQt.QtWidgets import QDialog, QListWidgetItem,QProgressDialog
from qgis.PyQt.QtCore import Qt
from qgis.PyQt import uic
from qgis.core import QgsApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QMessageBox, QStyle, QFileDialog
from qgis.PyQt.QtGui import QRegExpValidator

from ...dialogs.util.prefixdialog import PrefixDialog
from ...dialogs.util.examplequerydialog import ExampleQueryDialog
from ...util.ui.uiutils import UIUtils
from ...util.conf.configutils import ConfigUtils
from ...util.ui.sparqlhighlighter import SPARQLHighlighter
from ...tasks.query.util.detecttriplestoretask import DetectTripleStoreTask
import os.path
import json

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), '../ui/triplestoredialog.ui'))

class TripleStoreDialog(QDialog,FORM_CLASS):
	
    triplestoreconf=""
	
    def __init__(self,triplestoreconf,prefixes,prefixstore,comboBox):
        super(QDialog, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(UIUtils.linkeddataicon)
        self.triplestoreconf=triplestoreconf 
        self.prefixstore=prefixstore
        self.comboBox=comboBox
        self.prefixes=prefixes
        for item in triplestoreconf:
            if "resource" in item and "type" in item["resource"] and item["resource"]["type"]=="file":
                self.tripleStoreChooser.addItem(UIUtils.rdffileicon,
                                                item["name"] + " [File]")
            elif "type" in item:
                if item["type"] == "geosparqlendpoint":
                    self.tripleStoreChooser.addItem(UIUtils.geoendpointicon, item["name"]+ " [GeoSPARQL Endpoint]")
                elif item["type"]=="sparqlendpoint":
                    self.tripleStoreChooser.addItem(UIUtils.linkeddataicon,item["name"] + " [SPARQL Endpoint]")
                elif item["type"]=="file":
                    self.tripleStoreChooser.addItem(UIUtils.rdffileicon,item["name"] + " [File]")
                else:
                    self.tripleStoreChooser.addItem(item["name"]+" ["+str(item["type"])+"]")
        self.tripleStoreChooser.currentIndexChanged.connect(self.loadTripleStoreConfig)
        self.tripleStoreChooser.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.geometryVariableComboBox.currentIndexChanged.connect(self.switchQueryVariableInput)
        self.exampleQueryComboBox.currentIndexChanged.connect(lambda: self.exampleQuery.setPlainText(self.exampleQueryComboBox.itemData(self.exampleQueryComboBox.currentIndex())))
        self.tripleStoreEdit.setValidator(QRegExpValidator(UIUtils.urlregex, self))
        self.tripleStoreEdit.textChanged.connect(lambda: UIUtils.check_state(self.tripleStoreEdit))
        self.tripleStoreEdit.textChanged.emit(self.tripleStoreEdit.text())
        self.typePropertyEdit.setValidator(QRegExpValidator(UIUtils.urlregex, self))
        self.typePropertyEdit.textChanged.connect(lambda: UIUtils.check_state(self.typePropertyEdit))
        self.labelPropertyEdit.setValidator(QRegExpValidator(UIUtils.urlregex, self))
        self.labelPropertyEdit.textChanged.connect(lambda: UIUtils.check_state(self.labelPropertyEdit))
        self.classURIEdit.setValidator(QRegExpValidator(UIUtils.urlregex, self))
        self.classURIEdit.textChanged.connect(lambda: UIUtils.check_state(self.classURIEdit))
        self.geometryClassURIEdit.setValidator(QRegExpValidator(UIUtils.urlregex, self))
        self.geometryClassURIEdit.textChanged.connect(lambda: UIUtils.check_state(self.geometryClassURIEdit))
        self.featureCollectionURIEdit.setValidator(QRegExpValidator(UIUtils.urlregex, self))
        self.featureCollectionURIEdit.textChanged.connect(lambda: UIUtils.check_state(self.featureCollectionURIEdit))
        self.geometryCollectionURIEdit.setValidator(QRegExpValidator(UIUtils.urlregex, self))
        self.geometryCollectionURIEdit.textChanged.connect(lambda: UIUtils.check_state(self.geometryCollectionURIEdit))
        self.collectionMemberPropertyEdit.setValidator(QRegExpValidator(UIUtils.urlregex, self))
        self.collectionMemberPropertyEdit.textChanged.connect(lambda: UIUtils.check_state(self.collectionMemberPropertyEdit))
        self.subclassPropertyEdit.setValidator(QRegExpValidator(UIUtils.urlregex, self))
        self.subclassPropertyEdit.textChanged.connect(lambda: UIUtils.check_state(self.subclassPropertyEdit))
        self.geometryPropertyEdit1.setValidator(QRegExpValidator(UIUtils.urlregex, self))
        self.geometryPropertyEdit1.textChanged.connect(lambda: UIUtils.check_state(self.geometryPropertyEdit1))
        self.geometryPropertyEdit2.setValidator(QRegExpValidator(UIUtils.urlregex, self))
        self.geometryPropertyEdit2.textChanged.connect(lambda: UIUtils.check_state(self.geometryPropertyEdit2))
        self.authenticationComboBox.hide()
        self.credentialUserName.hide()
        self.credentialPassword.hide()
        self.usernameLabel.hide()
        self.passwordLabel.hide()
        self.latVarEdit.hide()
        self.prefixList.itemDoubleClicked.connect(lambda item: PrefixDialog(self.prefixList,prefixstore,item.data(257),item.data(256)).exec())
        self.secondGeometryVarLabel.hide()
        self.testConnectButton.clicked.connect(self.testTripleStoreConnection)
        self.deleteTripleStore.clicked.connect(self.deleteTripleStoreFunc)
        self.resetConfiguration.clicked.connect(self.restoreFactory)		
        self.newTripleStore.clicked.connect(self.createNewTripleStore)
        self.addExampleQueryButton.clicked.connect(lambda: ExampleQueryDialog(self.exampleQueryComboBox).exec())
        self.editQueryNameButton.clicked.connect(lambda: ExampleQueryDialog(self.exampleQueryComboBox,self.exampleQueryComboBox.currentText()).exec())
        self.saveExampleQueryButton.clicked.connect(lambda: self.exampleQueryComboBox.setItemData(self.exampleQueryComboBox.currentIndex(),self.exampleQuery.toPlainText()))
        self.removeExampleQueryButton.clicked.connect(lambda: self.exampleQueryComboBox.removeItem(self.exampleQueryComboBox.currentIndex()))
        self.configurationAsJSONButton.clicked.connect(self.saveConfigurationAsJSON)
        self.sparqlhighlighter = SPARQLHighlighter(self.exampleQuery)
        self.tripleStoreApplyButton.clicked.connect(self.applyCustomSPARQLEndPoint)
        self.useAuthenticationCheckBox.stateChanged.connect(self.enableAuthentication)
        self.addPrefixButton.clicked.connect(lambda: PrefixDialog(self.prefixList,prefixstore).exec())
        self.removePrefixButton.clicked.connect(self.removePrefixFromList)
        self.detectConfiguration.clicked.connect(self.detectTripleStoreConfiguration)
        self.varInfoButton.clicked.connect(self.createVarInfoDialog)
        self.varInfoButton.setIcon(
            QIcon(self.style().standardIcon(getattr(QStyle, 'SP_MessageBoxInformation'))))
        self.loadTripleStoreConfig()

    def saveConfigurationAsJSON(self):
        conffilename=QFileDialog.getSaveFileName(self,"Save File",str(self.triplestoreconf[self.tripleStoreChooser.currentIndex()]["name"])+".json")
        if conffilename!="" and conffilename[0]!="":
            file=open(conffilename[0],"w")
            file.write(json.dumps(ConfigUtils.removeInstanceKeys(self.triplestoreconf[self.tripleStoreChooser.currentIndex()],"instance"),indent=2))
            file.close()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Configuration File for "+str(self.tripleStoreChooser.currentText())+"<br/>saved as<br/>"+str(conffilename[0]))
            msg.exec()

    def createVarInfoDialog(self):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("SPARQL Query Templates Variables")
        msgBox.setWindowIcon(QIcon(self.style().standardIcon(getattr(QStyle,'SP_MessageBoxInformation'))))
        thetext="<html><h3>Template Variables for the usage in example queries</h3><table border=1 cellspacing=0><tr><th>Variable</th><th>Value</th></tr>"
        thetext+="<tr><td>%%concept%%</td><td>The currently selected concept in the class tree</td></tr>"
        if "typeproperty" in self.triplestoreconf[self.comboBox.currentIndex()]:
            thetext+=f"<tr><td>%%typeproperty%%</td><td>{self.triplestoreconf[self.comboBox.currentIndex()]['typeproperty']}</td></tr>"
        if "subclassproperty" in self.triplestoreconf[self.comboBox.currentIndex()]:
            thetext+=f"<tr><td>%%subclassproperty%%</td><td>{self.triplestoreconf[self.comboBox.currentIndex()]['subclassproperty']}</td></tr>"
        if "labelproperty" in self.triplestoreconf[self.comboBox.currentIndex()]:
            thetext+=f"<tr><td>%%labelproperty%%</td><td>{self.triplestoreconf[self.comboBox.currentIndex()]['labelproperty']}</td></tr>"
        if "geometryproperty" in self.triplestoreconf[self.comboBox.currentIndex()]:
            if isinstance(self.triplestoreconf[self.comboBox.currentIndex()]["geometryproperty"],str):
                thetext+=f"<tr><td>%%geomproperty%%</td><td>{self.triplestoreconf[self.comboBox.currentIndex()]['geometryproperty']}</td></tr>"
            elif isinstance(self.triplestoreconf[self.comboBox.currentIndex()]["geometryproperty"],list):
                thetext+=f"<tr><td>%%geomproperty%%</td><td>{self.triplestoreconf[self.comboBox.currentIndex()]['geometryproperty'][0]}</td></tr>"
        thetext+="</html>"
        msgBox.setText(thetext)
        msgBox.exec()

    def switchQueryVariableInput(self):
        if "Single Variable" in self.geometryVariableComboBox.currentText():
            self.latVarEdit.hide()
            self.secondGeometryVarLabel.hide()
        else:
            self.latVarEdit.show()
            self.secondGeometryVarLabel.show()


    def enableAuthentication(self):
        if self.useAuthenticationCheckBox.checkState():
            self.authenticationComboBox.show()
            self.credentialUserName.show()
            self.credentialPassword.show()
            self.usernameLabel.show()
            self.passwordLabel.show()
        else:
            self.authenticationComboBox.hide()
            self.credentialUserName.hide()
            self.credentialPassword.hide()
            self.usernameLabel.hide()
            self.passwordLabel.hide()

    def loadTripleStoreConfig(self):
        if self.tripleStoreChooser.currentIndex()<len(self.triplestoreconf):
            curstore=self.triplestoreconf[self.tripleStoreChooser.currentIndex()]
            if curstore["resource"]["type"]=="endpoint":
                self.tripleStoreEdit.setText(curstore["resource"]["url"])
            if curstore["resource"]["type"]=="file":
                self.tripleStoreEdit.setText(curstore["resource"]["url"])
            self.tripleStoreNameEdit.setText(curstore["name"])
            self.prefixList.clear()
            if "resource" in curstore and "type" in curstore["resource"]:
                if "sparqlendpoint" in curstore["resource"]["type"]:
                    self.rdfResourceComboBox.setCurrentIndex(0)
                elif curstore["resource"]["type"]=="file" and curstore["resource"]["url"].startswith("http"):
                    self.rdfResourceComboBox.setCurrentIndex(1)
                else:
                    self.rdfResourceComboBox.setCurrentIndex(2)
            for prefix in curstore["prefixes"]:
                item=QListWidgetItem()
                item.setText(str(prefix)+": <"+str(curstore["prefixes"][prefix])+">")
                item.setData(256,curstore["prefixes"][prefix])
                item.setData(257,prefix)
                self.prefixList.addItem(item)
            self.prefixList.sortItems()
            if "labelproperty" in curstore:
                if isinstance(curstore["labelproperty"], list):
                    self.labelPropertyEdit.setText(curstore["labelproperty"][0])
                else:
                    self.labelPropertyEdit.setText(curstore["labelproperty"])
            else:
                self.labelPropertyEdit.setText("http://www.w3.org/2000/01/rdf-schema#label")
            if "typeproperty" in curstore:
                self.typePropertyEdit.setText(curstore["typeproperty"])
            else:
                self.typePropertyEdit.setText("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
            if "subclassproperty" in curstore:
                self.subclassPropertyEdit.setText(curstore["subclassproperty"])
            else:
                self.subclassPropertyEdit.setText("http://www.w3.org/2000/01/rdf-schema#subClassOf")
            if "collectionmemberproperty" in curstore:
                self.collectionMemberPropertyEdit.setText(curstore["collectionmemberproperty"])
            else:
                self.collectionMemberPropertyEdit.setText("http://www.w3.org/2000/01/rdf-schema#member")
            if "featurecollectionclasses" in curstore:
                self.featureCollectionURIEdit.setText(curstore["featurecollectionclasses"][0])
            else:
                self.featureCollectionURIEdit.setText("http://www.opengis.net/ont/geosparql#FeatureCollection")
            if "geometrycollectionclasses" in curstore:
                self.geometryCollectionURIEdit.setText(curstore["geometrycollectionclasses"][0])
            else:
                self.geometryCollectionURIEdit.setText("http://www.opengis.net/ont/geosparql#GeometryCollection")
            if "geometryclasses" in curstore:
                self.geometryClassURIEdit.setText(curstore["geometryclasses"][0])
            else:
                self.geometryClassURIEdit.setText("http://www.opengis.net/ont/geosparql#Geometry")
            if "classes" in curstore:
                self.classURIEdit.setText(curstore["classes"][0])
            else:
                self.classURIEdit.setText("http://www.w3.org/2002/07/owl#Class")
            if "geometryproperty" in curstore and isinstance(curstore["geometryproperty"],list):
                if len(curstore["geometryproperty"])>0:
                    self.geometryPropertyEdit1.setText(curstore["geometryproperty"][0])
                if len(curstore["geometryproperty"]) > 1:
                    self.geometryPropertyEdit2.setText(curstore["geometryproperty"][1])
            elif "geometryproperty" in curstore and isinstance(curstore["geometryproperty"],str):
                self.geometryPropertyEdit1.setText(
                    curstore["geometryproperty"])
                self.geometryPropertyEdit2.setText("")
            else:
                self.geometryPropertyEdit1.setText("")
                self.geometryPropertyEdit2.setText("")
            if "auth" in curstore:
                self.enableAuthentication()
                self.credentialUserName.setText(curstore["auth"]["userCredential"])
                self.credentialPassword.setText(curstore["auth"]["userPassword"])
            if "querytemplate" in curstore and isinstance(curstore["querytemplate"],list):
                self.exampleQueryComboBox.clear()
                for template in curstore["querytemplate"]:
                    self.exampleQueryComboBox.addItem(template["label"],template["query"])
            if "querytemplate" in curstore and curstore["querytemplate"]!=None and len(curstore["querytemplate"])>0:
                self.exampleQuery.setPlainText(curstore["querytemplate"][0]["query"])

    def testTripleStoreConnection(self,calledfromotherfunction=False,showMessageBox=True,query="SELECT ?a ?b ?c WHERE { ?a ?b ?c .} LIMIT 1"):
        progress = QProgressDialog("Checking connection to triple store "+self.tripleStoreEdit.text()+"...", "Abort", 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)
        progress.setWindowIcon(UIUtils.sparqlunicornicon)
        progress.show()
        self.qtask=DetectTripleStoreTask("Checking connection to triple store "+self.tripleStoreEdit.text()+"...",
                                         self.triplestoreconf,self.tripleStoreEdit.text(),
                                         self.tripleStoreNameEdit.text(),self.credentialUserName.text(),
            self.credentialPassword.text(), self.authenticationComboBox.currentText(),True,False,self.prefixes,
                                         self.prefixstore,self.tripleStoreChooser,
                                         self.comboBox,False,None,self,progress)
        QgsApplication.taskManager().addTask(self.qtask)

    def detectTripleStoreConfiguration(self):	
        progress = QProgressDialog("Detecting configuration for triple store "+self.tripleStoreEdit.text()+"...", "Abort", 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)
        progress.setWindowIcon(UIUtils.sparqlunicornicon)
        progress.show()
        self.qtask=DetectTripleStoreTask("Detecting configuration for triple store "+self.tripleStoreEdit.text()+"...",self.triplestoreconf,self.tripleStoreEdit.text(),self.tripleStoreNameEdit.text(),self.credentialUserName.text(),
            self.credentialPassword.text(), self.authenticationComboBox.currentText(),False,True,self.prefixes,self.prefixstore,self.tripleStoreChooser,self.comboBox,False,None,self,progress)
        QgsApplication.taskManager().addTask(self.qtask)
	
    ## 
    #  @brief Adds a new SPARQL endpoint to the triple store registry
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
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, 'triplestoreconf.json'),'r') as myfile:
            data=myfile.read()
        self.triplestoreconf=json.loads(data)
        self.tripleStoreChooser.clear()
        for item in self.triplestoreconf:
            self.tripleStoreChooser.addItem(item["name"])
        self.writeConfiguration()
        msgBox=QMessageBox()	
        msgBox.setWindowTitle("Triple Store Settings Reset!")
        msgBox.setText("Triple store settings have been reset to default!")	
        msgBox.exec()	
        return	

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
        for item in self.prefixList.selectedItems():
            self.prefixList.takeItem(self.prefixList.row(item))

    def writeConfiguration(self):
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        f = open(os.path.join(__location__, "triplestoreconf_personal.json"), "w")
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
        curprefixes={}
        for i in range(self.prefixList.count()):
            curprefixes[self.prefixList.item(i).data(257)]=self.prefixList.item(i).data(256)
        if self.addTripleStore:
            index=len(self.triplestoreconf)
            self.tripleStoreChooser.addItem(self.tripleStoreNameEdit.text()	)
        else:
            index=self.tripleStoreChooser.currentIndex()
        self.triplestoreconf[index]={}
        self.triplestoreconf[index]["resource"]={"type":"endpoint","url":self.tripleStoreEdit.text()}
        self.triplestoreconf[index]["name"]=self.tripleStoreNameEdit.text()
        if "SPARQL Endpoint" in self.rdfResourceComboBox.currentText():
            self.triplestoreconf[index]["type"] = "sparqlendpoint"
        elif "RDF File" in self.rdfResourceComboBox.currentText():
            self.triplestoreconf[index]["type"] = "file"
        if self.useAuthenticationCheckBox.checkState(Qt.Checked):
            self.triplestoreconf[index]["auth"]={}
            self.triplestoreconf[index]["auth"]["userCredential"] = self.credentialUserName.text()
            self.triplestoreconf[index]["auth"]["userPassword"] = self.credentialPassword.text()
            self.triplestoreconf[index]["auth"]["method"]=self.authenticationComboBox.currentText()
        else:
            self.triplestoreconf[index]["mandatoryvariables"]["auth"]={}
        self.triplestoreconf[index]["mandatoryvariables"]=[self.queryVarEdit.text(),self.queryVarItemEdit.text()]
        self.triplestoreconf[index]["labelproperty"]=self.labelPropertyEdit.text()
        self.triplestoreconf[index]["typeproperty"]=self.typePropertyEdit.text()
        self.triplestoreconf[index]["subclassproperty"]=self.subclassPropertyEdit.text()
        self.triplestoreconf[index]["collectionmemberproperty"]=self.collectionMemberPropertyEdit.text()
        self.triplestoreconf[index]["geometrycollectionclasses"] = [self.geometryCollectionClassURIEdit.text()]
        self.triplestoreconf[index]["featurecollectionclasses"] = [self.featureCollectionClassURIEdit.text()]
        self.triplestoreconf[index]["geometryclasses"] = [self.geometryClassURIEdit.text()]
        self.triplestoreconf[index]["classes"] = [self.classURIEdit.text()]
        self.triplestoreconf.append({})
        self.triplestoreconf[index]["querytemplate"] = []
        for i in range(self.exampleQueryComboBox.count()):
            self.triplestoreconf[index]["querytemplate"].append({})
            self.triplestoreconf[index]["querytemplate"][i]["label"] = self.exampleQueryComboBox.itemText(i)
            self.triplestoreconf[index]["querytemplate"][i]["query"] = self.exampleQueryComboBox.itemData(i)
        self.triplestoreconf[index]["prefixes"]=curprefixes
        self.addTripleStore=False

